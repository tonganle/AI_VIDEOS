from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import os
import threading
import time
from werkzeug.utils import secure_filename
import json

# 导入原有的处理函数
from video_processor import VideoProcessor

app = Flask(__name__)
CORS(app)

# 配置上传文件夹
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'webm'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

# 确保文件夹存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# 全局变量存储处理状态
processing_status = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/process-video', methods=['POST'])
def process_video():
    try:
        data = request.get_json()
        video_url = data.get('video_url', '')
        add_subtitles = data.get('add_subtitles', True)
        audio_mode = data.get('audio_mode', 'synth')
        task_id = f"task_{int(time.time())}"
        
        # 初始化处理状态
        processing_status[task_id] = {
            'status': 'processing',
            'progress': 0,
            'message': '开始处理...',
            'steps': []
        }
        
        # 在后台线程中处理视频
        thread = threading.Thread(target=process_video_background, args=(task_id, video_url, add_subtitles, audio_mode))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'message': '视频处理已开始'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def process_video_background(task_id, video_url, add_subtitles, audio_mode):
    try:
        processor = VideoProcessor()
        
        def update_status(progress, message, step=None):
            processing_status[task_id]['progress'] = progress
            processing_status[task_id]['message'] = message
            if step:
                processing_status[task_id]['steps'].append(step)
        
        # 步骤1: 下载视频
        update_status(10, '正在下载视频...', '开始下载视频')
        video_path = processor.download_video(video_url, task_id)
        update_status(20, '视频下载完成', '视频下载完成')
        
        # 步骤2: 提取音频
        update_status(30, '正在提取音频...', '开始提取音频')
        audio_path = processor.extract_audio(video_path, task_id)
        update_status(40, '音频提取完成', '音频提取完成')
        
        # 步骤3: 语音转文字
        if add_subtitles:
            update_status(50, '正在识别语音...', '开始语音识别')
            whisper_result = processor.speech_to_text_with_timestamps(audio_path)
            transcript = whisper_result['text']
            update_status(60, '语音识别完成', '语音识别完成')
            
            # 步骤4: 生成中文字幕字幕
            update_status(65, '正在生成中文字幕字幕...', '开始生成中文字幕字幕')
            subtitle_path = processor.generate_translated_srt_subtitle(whisper_result, task_id)
            update_status(70, '中文字幕字幕生成完成', '中文字幕字幕生成完成')
        else:
            update_status(50, '正在识别语音...', '开始语音识别')
            transcript = processor.speech_to_text(audio_path)
            update_status(60, '语音识别完成', '语音识别完成')
            subtitle_path = None
        
        # 步骤5: 翻译
        update_status(75, '正在翻译文案...', '开始翻译')
        translated_text = processor.translate_text(transcript)
        update_status(80, '翻译完成', '翻译完成')
        
        # 步骤6: 优化文案
        update_status(85, '正在优化文案...', '开始文案优化')
        optimized_text = processor.optimize_text(translated_text)
        update_status(90, '文案优化完成', '文案优化完成')
        
        # 步骤7: 生成语音
        update_status(95, '正在生成语音...', '开始语音合成')
        new_audio_path = processor.generate_segmented_audio(whisper_result, task_id) if add_subtitles else processor.generate_audio(optimized_text, task_id)
        update_status(98, '语音生成完成', '语音生成完成')
        
        # 步骤8: 合并视频
        update_status(99, '正在合并视频...', '开始视频合并')
        if audio_mode == 'original':
            # 只用原音轨
            output_path = processor.merge_video_audio_original(video_path, task_id, subtitle_path)
        else:
            # 用新音轨
            if add_subtitles and subtitle_path:
                output_path = processor.merge_video_audio_subtitle(video_path, new_audio_path, subtitle_path, task_id)
            else:
                output_path = processor.merge_video_audio(video_path, new_audio_path, task_id)
        update_status(100, '处理完成！', '视频处理完成')
        
        # 更新最终状态
        processing_status[task_id]['status'] = 'completed'
        processing_status[task_id]['output_file'] = output_path
        processing_status[task_id]['transcript'] = transcript
        processing_status[task_id]['translated'] = translated_text
        processing_status[task_id]['optimized'] = optimized_text
        
    except Exception as e:
        processing_status[task_id]['status'] = 'error'
        processing_status[task_id]['error'] = str(e)
        processing_status[task_id]['message'] = f'处理失败: {str(e)}'

@app.route('/api/status/<task_id>')
def get_status(task_id):
    if task_id not in processing_status:
        return jsonify({'error': '任务不存在'}), 404
    
    return jsonify(processing_status[task_id])

@app.route('/api/download/<task_id>')
def download_result(task_id):
    if task_id not in processing_status:
        return jsonify({'error': '任务不存在'}), 404
    
    status = processing_status[task_id]
    if status['status'] != 'completed':
        return jsonify({'error': '任务尚未完成'}), 400
    
    output_file = status.get('output_file')
    if not output_file or not os.path.exists(output_file):
        return jsonify({'error': '输出文件不存在'}), 404
    
    return send_file(output_file, as_attachment=True, download_name='processed_video.mp4')

@app.route('/api/upload-video', methods=['POST'])
def upload_video():
    try:
        if 'video' not in request.files:
            return jsonify({'error': '没有上传文件'}), 400
        
        file = request.files['video']
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            add_subtitles = request.form.get('add_subtitles', 'true').lower() == 'true'
            audio_mode = request.form.get('audio_mode', 'synth')
            
            task_id = f"upload_{int(time.time())}"
            
            thread = threading.Thread(target=process_uploaded_video, args=(task_id, filepath, add_subtitles, audio_mode))
            thread.daemon = True
            thread.start()
            
            return jsonify({
                'success': True,
                'task_id': task_id,
                'message': '视频上传成功，开始处理'
            })
        
        return jsonify({'error': '不支持的文件格式'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def process_uploaded_video(task_id, video_path, add_subtitles, audio_mode):
    try:
        processor = VideoProcessor()
        
        def update_status(progress, message, step=None):
            processing_status[task_id]['progress'] = progress
            processing_status[task_id]['message'] = message
            if step:
                processing_status[task_id]['steps'].append(step)
        
        processing_status[task_id] = {
            'status': 'processing',
            'progress': 0,
            'message': '开始处理上传的视频...',
            'steps': []
        }
        
        # 步骤1: 提取音频
        update_status(20, '正在提取音频...', '开始提取音频')
        audio_path = processor.extract_audio(video_path, task_id)
        update_status(30, '音频提取完成', '音频提取完成')
        
        # 步骤2: 语音转文字
        if add_subtitles:
            update_status(40, '正在识别语音...', '开始语音识别')
            whisper_result = processor.speech_to_text_with_timestamps(audio_path)
            transcript = whisper_result['text']
            update_status(50, '语音识别完成', '语音识别完成')
            
            update_status(55, '正在生成中文字幕字幕...', '开始生成中文字幕字幕')
            subtitle_path = processor.generate_translated_srt_subtitle(whisper_result, task_id)
            update_status(60, '中文字幕字幕生成完成', '中文字幕字幕生成完成')
        else:
            update_status(40, '正在识别语音...', '开始语音识别')
            transcript = processor.speech_to_text(audio_path)
            update_status(50, '语音识别完成', '语音识别完成')
            subtitle_path = None
        
        # 步骤4: 翻译
        update_status(65, '正在翻译文案...', '开始翻译')
        translated_text = processor.translate_text(transcript)
        update_status(70, '翻译完成', '翻译完成')
        
        # 步骤5: 优化文案
        update_status(80, '正在优化文案...', '开始文案优化')
        optimized_text = processor.optimize_text(translated_text)
        update_status(85, '文案优化完成', '文案优化完成')
        
        # 步骤6: 生成语音
        update_status(90, '正在生成语音...', '开始语音合成')
        new_audio_path = processor.generate_segmented_audio(whisper_result, task_id) if add_subtitles else processor.generate_audio(optimized_text, task_id)
        update_status(95, '语音生成完成', '语音生成完成')
        
        # 步骤7: 合并视频
        update_status(98, '正在合并视频...', '开始视频合并')
        if audio_mode == 'original':
            output_path = processor.merge_video_audio_original(video_path, task_id, subtitle_path)
        else:
            if add_subtitles and subtitle_path:
                output_path = processor.merge_video_audio_subtitle(video_path, new_audio_path, subtitle_path, task_id)
            else:
                output_path = processor.merge_video_audio(video_path, new_audio_path, task_id)
        update_status(100, '处理完成！', '视频处理完成')
        
        processing_status[task_id]['status'] = 'completed'
        processing_status[task_id]['output_file'] = output_path
        processing_status[task_id]['transcript'] = transcript
        processing_status[task_id]['translated'] = translated_text
        processing_status[task_id]['optimized'] = optimized_text
        
    except Exception as e:
        processing_status[task_id]['status'] = 'error'
        processing_status[task_id]['error'] = str(e)
        processing_status[task_id]['message'] = f'处理失败: {str(e)}'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 
from dashscope import SpeechSynthesizer
from dotenv import load_dotenv
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.io.VideoFileClip import VideoFileClip
from openai import OpenAI

from alibabacloud_alimt20181012.client import Client as alimt20181012Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_alimt20181012 import models as alimt_20181012_models
from alibabacloud_tea_util import models as util_models
from http import HTTPStatus

import dashscope
import os
import subprocess
import textwrap
import time
import whisper  # 在文件开头加
import json
import re
import tempfile
import shutil
from pydub import AudioSegment
import string
import librosa
import soundfile as sf
import numpy as np

load_dotenv()

class VideoProcessor:
    def __init__(self):
        self.openai_client = OpenAI()
        self.openai_client.api_key = os.environ["OPENAI_API_KEY"]
        
        # 阿里云配置
        self.ali_access_key_id = os.environ['ALI_CLOUD_ACCESS_KEY_ID']
        self.ali_access_key_secret = os.environ['ALI_CLOUD_ACCESS_KEY_SECRET']
        self.ali_api_key = os.environ["ALI_API_KEY"]
        
        # 设置dashscope API key
        dashscope.api_key = self.ali_api_key
        
        # 创建输出目录
        os.makedirs('outputs', exist_ok=True)
        os.makedirs('temp', exist_ok=True)

    def execute_command(self, command):
        """执行命令行指令"""
        print(f"执行命令: {command}")
        result = subprocess.call(command, shell=True)
        print(f"命令执行结果: {result}")
        return result

    def download_video(self, url, task_id):
        """下载YouTube视频"""
        print(f"开始下载视频: {url}")
        
        # 根据操作系统选择yt-dlp命令
        if os.name == 'nt':  # Windows
            download_command = f"yt-dlp {url} -o 'temp/raw_{task_id}.%(ext)s'"
        else:  # macOS/Linux
            download_command = f"yt-dlp {url} -o 'temp/raw_{task_id}.%(ext)s'"
        
        self.execute_command(download_command)
        
        # 查找下载的文件
        for file in os.listdir('temp'):
            if file.startswith(f'raw_{task_id}'):
                return os.path.join('temp', file)
        
        raise Exception("视频下载失败")

    def extract_audio(self, video_path, task_id):
        """从视频中提取音频"""
        print(f"从视频提取音频: {video_path}")
        
        audio_path = f"temp/audio_{task_id}.mp3"
        audio_command = f"ffmpeg -i '{video_path}' -vn '{audio_path}'"
        
        self.execute_command(audio_command)
        
        if os.path.exists(audio_path):
            return audio_path
        else:
            raise Exception("音频提取失败")

    def speech_to_text(self, audio_path):
        """使用本地 Whisper 将音频转换为文字"""
        print(f"开始本地语音识别: {audio_path}")
        try:
            model = whisper.load_model("base")  # 你也可以用"small"、"medium"、"large"
            result = model.transcribe(audio_path)
            text = result["text"]
            print(f"语音识别完成，文本长度: {len(text)}")
            return text
        except Exception as e:
            print(f"本地语音识别失败: {str(e)}")
            raise e

    def speech_to_text_with_timestamps(self, audio_path):
        """使用本地 Whisper 将音频转换为带时间戳的文字"""
        print(f"开始本地语音识别（带时间戳）: {audio_path}")
        try:
            model = whisper.load_model("base")
            result = model.transcribe(audio_path, word_timestamps=True)
            print(f"语音识别完成，文本长度: {len(result['text'])}")
            return result
        except Exception as e:
            print(f"本地语音识别失败: {str(e)}")
            raise e

    def generate_srt_subtitle(self, whisper_result, task_id, language='zh'):
        """生成SRT字幕文件"""
        print(f"开始生成SRT字幕文件")
        
        try:
            srt_path = f"temp/subtitle_{task_id}.srt"
            
            with open(srt_path, 'w', encoding='utf-8') as f:
                segment_index = 1
                
                for segment in whisper_result['segments']:
                    # 转换时间戳为SRT格式 (HH:MM:SS,mmm)
                    start_time = self.format_timestamp(segment['start'])
                    end_time = self.format_timestamp(segment['end'])
                    
                    # 写入SRT格式
                    f.write(f"{segment_index}\n")
                    f.write(f"{start_time} --> {end_time}\n")
                    f.write(f"{segment['text'].strip()}\n\n")
                    
                    segment_index += 1
            
            print(f"SRT字幕文件生成完成: {srt_path}")
            return srt_path
            
        except Exception as e:
            print(f"生成SRT字幕文件失败: {str(e)}")
            raise e

    def format_timestamp(self, seconds):
        """将秒数转换为SRT时间戳格式"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"

    def translate_text(self, text):
        """将英文翻译为中文"""
        print(f"开始翻译文本，长度: {len(text)}")
        
        try:
            config = open_api_models.Config(
                access_key_id=self.ali_access_key_id,
                access_key_secret=self.ali_access_key_secret
            )
            config.endpoint = 'mt.cn-hangzhou.aliyuncs.com'
            config.region_id = 'cn-hangzhou'
            client = alimt20181012Client(config)

            translate_request = alimt_20181012_models.TranslateGeneralRequest(
                format_type='text',
                source_language='en',
                target_language='zh',
                source_text=text,
                scene='general'
            )
            runtime = util_models.RuntimeOptions()

            response = client.translate_general_with_options(translate_request, runtime)
            translated_text = response.body.data.translated
            
            print(f"翻译完成，翻译后长度: {len(translated_text)}")
            return translated_text
            
        except Exception as e:
            print(f"翻译失败: {str(e)}")
            raise e

    def optimize_text(self, text):
        """使用通义千问优化中文文案"""
        print(f"开始优化文案，长度: {len(text)}")
        
        try:
            response = dashscope.Generation.call(
                model=dashscope.Generation.Models.qwen_turbo,
                prompt='把以下内容按照中文的习惯修改的更加通顺，可以适当的润色，不要添加任何段落样式：' + text
            )
            
            if response.status_code == HTTPStatus.OK:
                optimized_text = response.output.text
                print(f"文案优化完成，优化后长度: {len(optimized_text)}")
                return optimized_text
            else:
                print(f"文案优化失败: {response.code} - {response.message}")
                raise Exception(f"文案优化失败: {response.message}")
                
        except Exception as e:
            print(f"文案优化失败: {str(e)}")
            raise e

    def generate_audio(self, text, task_id):
        """使用Sambert生成中文语音"""
        print(f"开始生成语音，文本长度: {len(text)}")
        
        try:
            result = SpeechSynthesizer.call(
                model='sambert-zhixiang-v1',
                text=text,
                sample_rate=48000
            )
            
            if result.get_audio_data() is not None:
                audio_path = f"temp/new_audio_{task_id}.mp3"
                with open(audio_path, 'wb') as f:
                    f.write(result.get_audio_data())
                
                print(f"语音生成完成: {audio_path}")
                return audio_path
            else:
                raise Exception("语音生成失败，没有获取到音频数据")
                
        except Exception as e:
            print(f"语音生成失败: {str(e)}")
            raise e

    def merge_video_audio_subtitle(self, video_path, audio_path, subtitle_path, task_id):
        """合并视频、音频和字幕，只保留新音轨"""
        print(f"开始合并视频、音频和字幕")
        print(f"视频文件: {video_path}")
        print(f"音频文件: {audio_path}")
        print(f"字幕文件: {subtitle_path}")
        try:
            output_path = f"outputs/output_{task_id}.mp4"
            # 只保留视频和新音轨
            merge_command = (
                f'ffmpeg -y -i "{video_path}" -i "{audio_path}" '
                f'-map 0:v:0 -map 1:a:0 -vf subtitles="{subtitle_path}" '
                f'-c:v libx264 -c:a aac -shortest "{output_path}"'
            )
            self.execute_command(merge_command)
            if os.path.exists(output_path):
                print(f"视频合并完成: {output_path}")
                return output_path
            else:
                raise Exception("视频合并失败，输出文件不存在")
        except Exception as e:
            print(f"视频合并失败: {str(e)}")
            raise e

    def merge_video_audio(self, video_path, audio_path, task_id):
        """合并视频和音频（只保留新音轨）"""
        print(f"开始合并视频和音频")
        print(f"视频文件: {video_path}")
        print(f"音频文件: {audio_path}")
        try:
            output_path = f"outputs/output_{task_id}.mp4"
            merge_command = (
                f'ffmpeg -y -i "{video_path}" -i "{audio_path}" '
                f'-map 0:v:0 -map 1:a:0 -c:v libx264 -c:a aac -shortest "{output_path}"'
            )
            self.execute_command(merge_command)
            if os.path.exists(output_path):
                print(f"视频合并完成: {output_path}")
                return output_path
            else:
                raise Exception("视频合并失败，输出文件不存在")
        except Exception as e:
            print(f"视频合并失败: {str(e)}")
            raise e

    def merge_video_audio_original(self, video_path, task_id, subtitle_path=None):
        """只用原音轨合成视频，可选带字幕"""
        print(f"开始合并视频和原音轨，字幕: {subtitle_path}")
        output_path = f"outputs/output_{task_id}.mp4"
        try:
            if subtitle_path:
                merge_command = (
                    f'ffmpeg -y -i "{video_path}" -vf subtitles="{subtitle_path}" '
                    f'-c:v libx264 -c:a copy -shortest "{output_path}"'
                )
            else:
                merge_command = (
                    f'ffmpeg -y -i "{video_path}" -c:v libx264 -c:a copy -shortest "{output_path}"'
                )
            self.execute_command(merge_command)
            if os.path.exists(output_path):
                print(f"视频合并完成: {output_path}")
                return output_path
            else:
                raise Exception("视频合并失败，输出文件不存在")
        except Exception as e:
            print(f"视频合并失败: {str(e)}")
            raise e

    def cleanup_temp_files(self, task_id):
        """清理临时文件"""
        try:
            temp_files = [
                f"temp/raw_{task_id}.*",
                f"temp/audio_{task_id}.mp3",
                f"temp/new_audio_{task_id}.mp3",
                f"temp/subtitle_{task_id}.srt"
            ]
            
            for pattern in temp_files:
                import glob
                for file in glob.glob(pattern):
                    if os.path.exists(file):
                        os.remove(file)
                        print(f"已删除临时文件: {file}")
                        
        except Exception as e:
            print(f"清理临时文件失败: {str(e)}")

    def remove_punctuation(self, text):
        # 英文标点
        en_punc = string.punctuation
        # 常见中文标点
        zh_punc = '！？｡。＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～、：；""''《》【】（）·'
        all_punc = en_punc + zh_punc
        table = str.maketrans('', '', all_punc)
        return text.translate(table)

    def generate_translated_srt_subtitle(self, whisper_result, task_id):
        """对每个分句翻译并生成中文字幕SRT（保留标点）"""
        print(f"开始生成中文字幕SRT字幕文件（保留标点）")
        srt_path = f"temp/subtitle_{task_id}.srt"
        try:
            segments = whisper_result['segments']
            zh_texts = []
            for seg in segments:
                try:
                    zh = self.translate_text(seg['text'])
                except Exception as e:
                    print(f"分句翻译失败，使用原文: {e}")
                    zh = seg['text']
                # 不再去除标点
                zh_texts.append(zh)
            with open(srt_path, 'w', encoding='utf-8') as f:
                for idx, seg in enumerate(segments):
                    start_time = self.format_timestamp(seg['start'])
                    end_time = self.format_timestamp(seg['end'])
                    f.write(f"{idx+1}\n")
                    f.write(f"{start_time} --> {end_time}\n")
                    f.write(f"{zh_texts[idx].strip()}\n\n")
            print(f"中文字幕SRT字幕文件生成完成: {srt_path}")
            return srt_path
        except Exception as e:
            print(f"生成中文字幕SRT失败: {str(e)}")
            raise e

    def generate_segmented_audio(self, whisper_result, task_id):
        """对每个分句翻译、TTS合成、内容变速拉伸并拼接，返回完整音频路径（语音字幕严格同步）"""
        print(f"开始分句TTS合成并拼接音频（内容变速拉伸）")
        import tempfile
        import shutil
        from pydub import AudioSegment
        import librosa
        import soundfile as sf
        import numpy as np
        import os
        segments = whisper_result['segments']
        temp_dir = tempfile.mkdtemp(prefix=f"seg_audio_{task_id}_")
        audio_paths = []
        try:
            for idx, seg in enumerate(segments):
                print(f"[TTS] 第{idx+1}句 原文: {seg['text']}")
                try:
                    zh = self.translate_text(seg['text'])
                except Exception as e:
                    print(f"[TTS] 第{idx+1}句 翻译失败，使用原文: {e}")
                    zh = seg['text']
                print(f"[TTS] 第{idx+1}句 中文: {zh}")
                tts_result = SpeechSynthesizer.call(
                    model='sambert-zhixiang-v1',
                    text=zh,
                    sample_rate=48000,
                    speech_rate=-200  # 慢速合成
                )
                if tts_result.get_audio_data() is not None:
                    seg_audio_path = os.path.join(temp_dir, f"seg_{idx}.mp3")
                    with open(seg_audio_path, 'wb') as f:
                        f.write(tts_result.get_audio_data())
                    # 目标时长（秒）
                    target_duration = seg['end'] - seg['start']
                    # 先转为wav
                    wav_path = seg_audio_path.replace('.mp3', '.wav')
                    os.system(f'ffmpeg -y -i "{seg_audio_path}" -ar 22050 "{wav_path}"')
                    y, sr = librosa.load(wav_path, sr=None, mono=True)
                    actual_duration = librosa.get_duration(y=y, sr=sr)
                    print(f"[TTS] 第{idx+1}句 音频生成成功: {seg_audio_path} 实际时长: {actual_duration:.2f}s 目标时长: {target_duration:.2f}s")
                    # 变速拉伸
                    if actual_duration > 0.1 and abs(actual_duration - target_duration) > 0.05:
                        rate = target_duration / actual_duration  # 修正为目标/实际
                        try:
                            y_stretch = librosa.effects.time_stretch(y, rate)
                        except Exception as e:
                            print(f"[TTS] 第{idx+1}句 time_stretch失败: {e}，跳过变速")
                            y_stretch = y
                        # 裁剪或补零精确对齐
                        target_len = int(target_duration * sr)
                        if len(y_stretch) > target_len:
                            y_stretch = y_stretch[:target_len]
                        else:
                            y_stretch = np.pad(y_stretch, (0, target_len - len(y_stretch)), mode='constant')
                        sf.write(wav_path, y_stretch, sr)
                        # 再转回mp3
                        os.system(f'ffmpeg -y -i "{wav_path}" -ar 48000 "{seg_audio_path}"')
                        print(f"[TTS] 第{idx+1}句 变速拉伸完成 rate={rate:.3f}")
                    audio_paths.append(seg_audio_path)
                else:
                    print(f"[TTS] 第{idx+1}句 TTS失败，未生成音频")
            # 拼接所有音频片段
            combined = None
            total_duration = 0.0
            for path in audio_paths:
                seg_audio = AudioSegment.from_file(path)
                if combined is None:
                    combined = seg_audio
                else:
                    combined += seg_audio
                total_duration += seg_audio.duration_seconds
            final_audio_path = f"temp/new_audio_{task_id}.mp3"
            if combined:
                combined.export(final_audio_path, format="mp3")
                print(f"[TTS] 分句拼接音频完成: {final_audio_path} 总时长: {total_duration:.2f}s 共{len(audio_paths)}句")
            else:
                print("[TTS] 没有可用的分句音频，TTS全失败，未生成音频！")
                raise Exception("没有可用的分句音频，TTS全失败")
            # 清理临时分句音频
            shutil.rmtree(temp_dir)
            return final_audio_path
        except Exception as e:
            print(f"[TTS] 分句TTS合成拼接失败: {str(e)}")
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise e 
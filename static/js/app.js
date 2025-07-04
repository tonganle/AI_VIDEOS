// 全局变量
let currentTaskId = null;
let statusCheckInterval = null;

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // 初始化文件上传功能
    initializeFileUpload();
    
    // 初始化拖拽上传
    initializeDragAndDrop();
    
    // 添加页面动画
    addPageAnimations();
}

// 初始化文件上传
function initializeFileUpload() {
    const fileInput = document.getElementById('videoFile');
    const uploadArea = document.getElementById('uploadArea');
    
    fileInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            handleFileUpload(file);
        }
    });
}

// 初始化拖拽上传
function initializeDragAndDrop() {
    const uploadArea = document.getElementById('uploadArea');
    
    uploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });
    
    uploadArea.addEventListener('dragleave', function(e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
    });
    
    uploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileUpload(files[0]);
        }
    });
}

// 处理文件上传
function handleFileUpload(file) {
    // 检查文件类型
    if (!file.type.startsWith('video/')) {
        showError('请选择有效的视频文件');
        return;
    }
    
    // 检查文件大小 (限制为500MB)
    if (file.size > 500 * 1024 * 1024) {
        showError('文件大小不能超过500MB');
        return;
    }
    
    // 获取字幕选项
    const addSubtitles = document.getElementById('addSubtitlesFile').checked;
    const audioMode = document.querySelector('#file input[name="audioMode"]:checked')?.value || 'synth';
    
    // 创建FormData
    const formData = new FormData();
    formData.append('video', file);
    formData.append('add_subtitles', addSubtitles);
    formData.append('audio_mode', audioMode);
    
    // 显示加载状态
    showLoadingModal();
    
    // 发送上传请求
    fetch('/api/upload-video', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        hideLoadingModal();
        
        if (data.success) {
            currentTaskId = data.task_id;
            showStatusCard();
            startStatusCheck();
            showSuccess('视频上传成功，开始处理...');
        } else {
            showError(data.error || '上传失败');
        }
    })
    .catch(error => {
        hideLoadingModal();
        showError('上传失败: ' + error.message);
    });
}

// 处理YouTube URL
function processVideoUrl() {
    const urlInput = document.getElementById('videoUrl');
    const url = urlInput.value.trim();
    const addSubtitles = document.getElementById('addSubtitles').checked;
    const audioMode = document.querySelector('input[name="audioMode"]:checked').value;
    
    if (!url) {
        showError('请输入YouTube视频链接');
        return;
    }
    
    if (!isValidYouTubeUrl(url)) {
        showError('请输入有效的YouTube视频链接');
        return;
    }
    
    // 显示加载状态
    showLoadingModal();
    
    // 发送处理请求
    fetch('/api/process-video', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            video_url: url,
            add_subtitles: addSubtitles,
            audio_mode: audioMode
        })
    })
    .then(response => response.json())
    .then(data => {
        hideLoadingModal();
        
        if (data.success) {
            currentTaskId = data.task_id;
            showStatusCard();
            startStatusCheck();
            showSuccess('视频处理已开始...');
        } else {
            showError(data.error || '处理失败');
        }
    })
    .catch(error => {
        hideLoadingModal();
        showError('处理失败: ' + error.message);
    });
}

// 验证YouTube URL
function isValidYouTubeUrl(url) {
    const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/.+/;
    return youtubeRegex.test(url);
}

// 显示状态卡片
function showStatusCard() {
    const statusCard = document.getElementById('statusCard');
    statusCard.style.display = 'block';
    statusCard.classList.add('fade-in-up');
}

// 开始状态检查
function startStatusCheck() {
    if (statusCheckInterval) {
        clearInterval(statusCheckInterval);
    }
    
    statusCheckInterval = setInterval(checkStatus, 2000);
}

// 检查处理状态
function checkStatus() {
    if (!currentTaskId) return;
    
    fetch(`/api/status/${currentTaskId}`)
        .then(response => response.json())
        .then(data => {
            updateStatusDisplay(data);
            
            if (data.status === 'completed' || data.status === 'error') {
                clearInterval(statusCheckInterval);
                statusCheckInterval = null;
                
                if (data.status === 'completed') {
                    showResults(data);
                } else {
                    // 确保关闭加载模态框
                    hideLoadingModal();
                    showError(data.error || '处理失败');
                }
            }
        })
        .catch(error => {
            console.error('状态检查失败:', error);
        });
}

// 更新状态显示
function updateStatusDisplay(data) {
    const progressBar = document.getElementById('progressBar');
    const statusMessage = document.getElementById('statusMessage');
    const statusSteps = document.getElementById('statusSteps');
    
    // 更新进度条
    progressBar.style.width = data.progress + '%';
    progressBar.setAttribute('aria-valuenow', data.progress);
    
    // 更新状态消息
    statusMessage.textContent = data.message;
    
    // 更新步骤列表
    if (data.steps && data.steps.length > 0) {
        statusSteps.innerHTML = '';
        data.steps.forEach((step, index) => {
            const stepElement = document.createElement('div');
            stepElement.className = 'step';
            stepElement.textContent = step;
            
            if (index < data.steps.length - 1) {
                stepElement.classList.add('completed');
            } else {
                stepElement.classList.add('current');
            }
            
            statusSteps.appendChild(stepElement);
        });
    }
}

// 显示处理结果
function showResults(data) {
    // 确保关闭加载模态框
    hideLoadingModal();
    
    const resultContent = document.getElementById('resultContent');
    const textContent = document.getElementById('textContent');
    
    // 显示视频结果
    resultContent.innerHTML = `
        <div class="text-center">
            <video class="result-video" controls>
                <source src="/api/download/${currentTaskId}" type="video/mp4">
                您的浏览器不支持视频播放。
            </video>
            <div class="mt-3">
                <a href="/api/download/${currentTaskId}" class="btn btn-success">
                    <i class="fas fa-download me-2"></i>下载处理后的视频
                </a>
            </div>
        </div>
    `;
    
    // 显示文案内容
    if (data.transcript || data.translated || data.optimized) {
        textContent.style.display = 'block';
        
        if (data.transcript) {
            document.getElementById('originalText').textContent = data.transcript;
        }
        
        if (data.translated) {
            document.getElementById('translatedText').textContent = data.translated;
        }
        
        if (data.optimized) {
            document.getElementById('optimizedText').textContent = data.optimized;
        }
    }
    
    // 添加成功动画
    resultContent.classList.add('success-animation');
    
    // 显示成功消息
    showSuccess('视频处理完成！');
}

// 显示加载模态框
function showLoadingModal() {
    const modal = new bootstrap.Modal(document.getElementById('loadingModal'));
    modal.show();
}

// 隐藏加载模态框
function hideLoadingModal() {
    const modalElement = document.getElementById('loadingModal');
    if (modalElement) {
        const modal = bootstrap.Modal.getInstance(modalElement);
        if (modal) {
            modal.hide();
        } else {
            // 如果没有实例，直接隐藏元素
            modalElement.style.display = 'none';
            modalElement.classList.remove('show');
            document.body.classList.remove('modal-open');
            const backdrop = document.querySelector('.modal-backdrop');
            if (backdrop) {
                backdrop.remove();
            }
        }
    }
}

// 显示成功消息
function showSuccess(message) {
    showToast(message, 'success');
}

// 显示错误消息
function showError(message) {
    showToast(message, 'error');
}

// 显示Toast消息
function showToast(message, type) {
    // 创建toast元素
    const toastContainer = document.getElementById('toastContainer') || createToastContainer();
    
    const toastElement = document.createElement('div');
    toastElement.className = `toast align-items-center text-white bg-${type === 'success' ? 'success' : 'danger'} border-0`;
    toastElement.setAttribute('role', 'alert');
    
    toastElement.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'} me-2"></i>
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toastElement);
    
    const toast = new bootstrap.Toast(toastElement);
    toast.show();
    
    // 自动移除toast元素
    toastElement.addEventListener('hidden.bs.toast', function() {
        toastElement.remove();
    });
}

// 创建Toast容器
function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '9999';
    document.body.appendChild(container);
    return container;
}

// 添加页面动画
function addPageAnimations() {
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.6s ease-out';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
}

// 工具函数：格式化文件大小
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// 工具函数：格式化时间
function formatDuration(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    
    if (hours > 0) {
        return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    } else {
        return `${minutes}:${secs.toString().padStart(2, '0')}`;
    }
} 
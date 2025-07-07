# AI视频处理工具 - 多端应用

🎬 **YouTube视频下载、语音识别、翻译、语音合成一体化处理工具**

支持Web、桌面应用、移动端多平台部署，提供现代化的用户界面和完整的视频处理流程。

## ✨ 功能特性

- 🎥 **YouTube视频下载** - 支持YouTube链接直接下载
- 🎵 **音频提取** - 自动从视频中提取音频
- 🗣️ **语音识别** - 使用OpenAI Whisper进行英文语音转文字
- 🌐 **机器翻译** - 阿里云机器翻译服务，英文转中文
- ✨ **文案优化** - 通义千问AI优化中文文案
- 🔊 **语音合成** - 阿里云Sambert生成中文语音
- 🎬 **音视频合并** - 自动合并原视频与新音频
- 📱 **多端支持** - Web、桌面、移动端全覆盖
- 🎨 **现代化UI** - 响应式设计，支持拖拽上传

## 🚀 快速开始

### 环境要求

- Python 3.8+
- ffmpeg
- yt-dlp
- 相关API密钥

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd AI_VIDEOS
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **安装外部工具**
```bash
# 安装ffmpeg
# macOS
brew install ffmpeg

# Ubuntu
sudo apt install ffmpeg

# Windows
# 下载并安装ffmpeg

# 安装yt-dlp
pip install yt-dlp
```

4. **配置环境变量**
```bash
# 复制环境变量模板
cp env.example .env

# 编辑.env文件，填写您的API密钥
```

### 配置API密钥

在 `.env` 文件中配置以下API密钥：

```env
# OpenAI API密钥 (用于Whisper语音识别)
OPENAI_API_KEY=your_openai_api_key_here

# 阿里云DashScope API密钥 (用于通义千问和语音合成)
ALI_API_KEY=your_ali_dashscope_api_key_here

# 阿里云访问密钥ID (用于机器翻译)
ALI_CLOUD_ACCESS_KEY_ID=your_ali_access_key_id_here

# 阿里云访问密钥Secret (用于机器翻译)
ALI_CLOUD_ACCESS_KEY_SECRET=your_ali_access_key_secret_here
```

### 启动应用

```bash
# 使用启动脚本（推荐）
python run.py

# 或直接启动
python app.py
```

访问 http://localhost:5000 开始使用！

## 📱 多端部署

### Web应用

#### 本地部署
```bash
python run.py
```

#### Docker部署
```bash
# 构建镜像
docker build -t ai-video-processor .

# 启动容器
docker-compose up
```

### 桌面应用

#### 构建桌面应用
```bash
# 构建所有平台
python build_config.py desktop

# 或构建所有平台
python build_config.py all
```

生成的桌面应用位于 `build/desktop/dist/` 目录。

### 移动端应用

#### React Native
```bash
cd build/mobile/react-native
npm install
npx react-native run-android  # Android
npx react-native run-ios      # iOS
```

#### Flutter
```bash
cd build/mobile/flutter
flutter pub get
flutter run
```

## 🎯 使用指南

### Web界面使用

1. **输入YouTube链接**
   - 在"YouTube链接"标签页中输入视频URL
   - 点击"开始处理"按钮

2. **上传本地视频**
   - 切换到"上传文件"标签页
   - 拖拽或点击选择视频文件
   - 支持mp4、avi、mov、mkv、webm格式

3. **查看处理进度**
   - 实时显示处理进度和状态
   - 显示每个步骤的完成情况

4. **获取处理结果**
   - 在线预览处理后的视频
   - 下载最终视频文件
   - 查看原文、翻译、优化文案

### 处理流程

1. **视频下载/上传** → 获取视频文件
2. **音频提取** → 从视频中提取音频
3. **语音识别** → 英文语音转文字
4. **机器翻译** → 英文翻译为中文
5. **文案优化** → AI优化中文文案
6. **语音合成** → 生成中文语音
7. **音视频合并** → 输出最终视频

## 🛠️ 技术架构

### 后端技术栈
- **Flask** - Web框架
- **OpenAI Whisper** - 语音识别
- **阿里云机器翻译** - 文本翻译
- **通义千问** - 文案优化
- **阿里云Sambert** - 语音合成
- **MoviePy** - 视频处理
- **FFmpeg** - 音视频转换

### 前端技术栈
- **Bootstrap 5** - UI框架
- **Font Awesome** - 图标库
- **原生JavaScript** - 交互逻辑
- **响应式设计** - 多设备适配

### 多端打包
- **PyInstaller** - 桌面应用打包
- **Docker** - 容器化部署
- **React Native** - 移动端开发
- **Flutter** - 跨平台移动端

## 📁 项目结构

```
AI_Truck/
├── app.py                 # Flask应用主文件
├── video_processor.py     # 视频处理核心类
├── run.py                 # 启动脚本
├── build_config.py        # 多端打包配置
├── requirements.txt       # Python依赖
├── env.example           # 环境变量模板
├── templates/            # HTML模板
│   └── index.html
├── static/               # 静态资源
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
├── uploads/              # 上传文件目录
├── outputs/              # 输出文件目录
├── temp/                 # 临时文件目录
└── build/                # 构建输出目录
    ├── web/              # Web应用构建
    ├── desktop/          # 桌面应用构建
    └── mobile/           # 移动端构建
```

## 🔧 开发指南

### 添加新功能

1. **后端功能**
   - 在 `video_processor.py` 中添加新的处理方法
   - 在 `app.py` 中添加对应的API接口

2. **前端功能**
   - 在 `templates/index.html` 中添加UI元素
   - 在 `static/js/app.js` 中添加交互逻辑
   - 在 `static/css/style.css` 中添加样式

3. **多端适配**
   - 更新 `build_config.py` 中的打包配置
   - 为移动端添加相应的原生功能

### 自定义配置

- **文件大小限制**: 修改 `app.py` 中的 `MAX_FILE_SIZE`
- **支持格式**: 修改 `ALLOWED_EXTENSIONS`
- **API配置**: 在 `.env` 文件中调整API参数

## 🐛 故障排除

### 常见问题

1. **依赖安装失败**
   ```bash
   # 升级pip
   pip install --upgrade pip
   
   # 使用国内镜像
   pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
   ```

2. **ffmpeg未找到**
   ```bash
   # 检查ffmpeg安装
   ffmpeg -version
   
   # 重新安装ffmpeg
   brew install ffmpeg  # macOS
   sudo apt install ffmpeg  # Ubuntu
   ```

3. **API密钥错误**
   - 检查 `.env` 文件中的API密钥是否正确
   - 确认API密钥有足够的配额和权限

4. **视频处理失败**
   - 检查视频文件格式是否支持
   - 确认视频文件没有损坏
   - 查看控制台错误信息

### 日志查看

```bash
# 查看应用日志
tail -f app.log

# 查看Docker日志
docker logs ai-video-processor
```

## 📄 许可证

本项目采用 Apache License 2.0 许可证。

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 📞 联系方式

- 邮箱: 876775178@qq.com
- 项目地址: [GitHub Repository]

## 🙏 致谢

- OpenAI - Whisper语音识别
- 阿里云 - 机器翻译、通义千问、语音合成
- Flask - Web框架
- Bootstrap - UI框架
- 所有开源贡献者

---

**注意**: 本项目仅供学习和演示使用，请遵守相关法律法规和平台使用条款。 
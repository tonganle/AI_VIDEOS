#!/usr/bin/env python3
"""
多端打包配置文件
支持Web、桌面应用、移动端打包
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

class MultiPlatformBuilder:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.dist_dir = self.project_root / "dist"
        self.build_dir = self.project_root / "build"
        
        # 确保目录存在
        self.dist_dir.mkdir(exist_ok=True)
        self.build_dir.mkdir(exist_ok=True)

    def build_web(self):
        """构建Web应用"""
        print("🚀 开始构建Web应用...")
        
        # 创建Web构建目录
        web_build_dir = self.build_dir / "web"
        web_build_dir.mkdir(exist_ok=True)
        
        # 复制必要文件
        files_to_copy = [
            "app.py",
            "video_processor.py", 
            "requirements.txt",
            ".env.example",
            "README.md"
        ]
        
        dirs_to_copy = [
            "templates",
            "static"
        ]
        
        for file in files_to_copy:
            src = self.project_root / file
            if src.exists():
                shutil.copy2(src, web_build_dir)
        
        for dir_name in dirs_to_copy:
            src_dir = self.project_root / dir_name
            if src_dir.exists():
                shutil.copytree(src_dir, web_build_dir / dir_name, dirs_exist_ok=True)
        
        # 创建启动脚本
        self._create_web_startup_script(web_build_dir)
        
        # 创建Docker配置
        self._create_docker_config(web_build_dir)
        
        print("✅ Web应用构建完成！")
        return web_build_dir

    def build_desktop(self):
        """构建桌面应用"""
        print("🖥️ 开始构建桌面应用...")
        
        try:
            # 检查PyInstaller是否安装
            import PyInstaller
        except ImportError:
            print("❌ PyInstaller未安装，正在安装...")
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
        
        # 创建桌面应用构建目录
        desktop_build_dir = self.build_dir / "desktop"
        desktop_build_dir.mkdir(exist_ok=True)
        
        # 创建PyInstaller配置文件
        self._create_pyinstaller_config(desktop_build_dir)
        
        # 运行PyInstaller，cwd切换到desktop_build_dir
        spec_file = desktop_build_dir / "app.spec"
        subprocess.run([
            "pyinstaller",
            "--clean",
            "--distpath", str(desktop_build_dir / "dist"),
            "--workpath", str(desktop_build_dir / "build"),
            str(spec_file.name)
        ], cwd=desktop_build_dir)
        
        print("✅ 桌面应用构建完成！")
        return desktop_build_dir / "dist"

    def build_mobile(self):
        """构建移动端应用"""
        print("📱 开始构建移动端应用...")
        
        # 创建移动端构建目录
        mobile_build_dir = self.build_dir / "mobile"
        mobile_build_dir.mkdir(exist_ok=True)
        
        # 创建React Native配置
        self._create_react_native_config(mobile_build_dir)
        
        # 创建Flutter配置
        self._create_flutter_config(mobile_build_dir)
        
        print("✅ 移动端应用配置完成！")
        return mobile_build_dir

    def _create_web_startup_script(self, build_dir):
        """创建Web应用启动脚本"""
        startup_script = build_dir / "start.py"
        
        script_content = '''#!/usr/bin/env python3
"""
AI视频处理工具 - Web应用启动脚本
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 设置环境变量
os.environ.setdefault('FLASK_ENV', 'production')

# 导入并启动应用
from app import app

if __name__ == '__main__':
    print("🚀 启动AI视频处理工具...")
    print("📱 访问地址: http://localhost:5000")
    print("🛑 按 Ctrl+C 停止服务")
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\\n👋 服务已停止")
'''
        
        with open(startup_script, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        # 设置执行权限
        startup_script.chmod(0o755)

    def _create_docker_config(self, build_dir):
        """创建Docker配置文件"""
        dockerfile = build_dir / "Dockerfile"
        
        dockerfile_content = '''# 使用Python 3.9官方镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \\
    ffmpeg \\
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建必要的目录
RUN mkdir -p uploads outputs temp

# 暴露端口
EXPOSE 5000

# 设置环境变量
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# 启动应用
CMD ["python", "start.py"]
'''
        
        with open(dockerfile, 'w', encoding='utf-8') as f:
            f.write(dockerfile_content)
        
        # 创建docker-compose.yml
        docker_compose = build_dir / "docker-compose.yml"
        
        compose_content = '''version: '3.8'

services:
  ai-video-processor:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./uploads:/app/uploads
      - ./outputs:/app/outputs
      - ./temp:/app/temp
    environment:
      - FLASK_ENV=production
    restart: unless-stopped
'''
        
        with open(docker_compose, 'w', encoding='utf-8') as f:
            f.write(compose_content)

    def _create_pyinstaller_config(self, build_dir):
        """创建PyInstaller配置文件，入口脚本和datas用绝对路径"""
        spec_file = build_dir / "app.spec"
        abs_app_py = str((self.project_root / "app.py").resolve())
        abs_templates = str((self.project_root / "templates").resolve())
        abs_static = str((self.project_root / "static").resolve())
        abs_video_processor = str((self.project_root / "video_processor.py").resolve())
        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['{abs_app_py}'],
    pathex=[],
    binaries=[],
    datas=[
        ('{abs_templates}', 'templates'),
        ('{abs_static}', 'static'),
        ('{abs_video_processor}', '.'),
    ],
    hiddenimports=[
        'flask',
        'flask_cors',
        'openai',
        'dashscope',
        'moviepy',
        'alibabacloud_alimt20181012',
        'alibabacloud_tea_openapi',
        'alibabacloud_tea_util',
        'playsound',
        'werkzeug',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AI视频处理工具',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='../static/icon.ico' if os.path.exists('../static/icon.ico') else None,
)
'''
        with open(spec_file, 'w', encoding='utf-8') as f:
            f.write(spec_content)

    def _create_react_native_config(self, build_dir):
        """创建React Native配置"""
        rn_dir = build_dir / "react-native"
        rn_dir.mkdir(exist_ok=True)
        
        # 创建package.json
        package_json = rn_dir / "package.json"
        
        package_content = '''{
  "name": "ai-video-processor-mobile",
  "version": "1.0.0",
  "description": "AI视频处理工具移动端",
  "main": "index.js",
  "scripts": {
    "start": "react-native start",
    "android": "react-native run-android",
    "ios": "react-native run-ios",
    "build": "react-native bundle"
  },
  "dependencies": {
    "react": "18.2.0",
    "react-native": "0.72.0",
    "react-native-video": "^5.2.1",
    "react-native-document-picker": "^9.0.1",
    "react-native-fs": "^2.20.0",
    "react-native-vector-icons": "^10.0.0"
  },
  "devDependencies": {
    "@babel/core": "^7.20.0",
    "@babel/preset-env": "^7.20.0",
    "@babel/runtime": "^7.20.0",
    "@react-native/eslint-config": "^0.72.2",
    "@react-native/metro-config": "^0.72.6",
    "@tsconfig/react-native": "^3.0.0",
    "@types/react": "^18.0.24",
    "@types/react-test-renderer": "^18.0.0",
    "babel-jest": "^29.2.1",
    "eslint": "^8.19.0",
    "jest": "^29.2.1",
    "metro-react-native-babel-preset": "0.76.5",
    "prettier": "^2.4.1",
    "react-test-renderer": "18.2.0",
    "typescript": "4.8.4"
  }
}
'''
        
        with open(package_json, 'w', encoding='utf-8') as f:
            f.write(package_content)

    def _create_flutter_config(self, build_dir):
        """创建Flutter配置"""
        flutter_dir = build_dir / "flutter"
        flutter_dir.mkdir(exist_ok=True)
        
        # 创建pubspec.yaml
        pubspec_yaml = flutter_dir / "pubspec.yaml"
        
        pubspec_content = '''name: ai_video_processor
description: AI视频处理工具移动端

version: 1.0.0+1

environment:
  sdk: '>=3.0.0 <4.0.0'

dependencies:
  flutter:
    sdk: flutter
  cupertino_icons: ^1.0.2
  http: ^1.1.0
  video_player: ^2.7.0
  file_picker: ^6.1.1
  path_provider: ^2.1.1
  permission_handler: ^11.0.1

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^3.0.0

flutter:
  uses-material-design: true
  assets:
    - assets/images/
'''
        
        with open(pubspec_yaml, 'w', encoding='utf-8') as f:
            f.write(pubspec_content)

    def build_all(self):
        """构建所有平台"""
        print("🎯 开始构建多端应用...")
        
        results = {}
        
        # 构建Web应用
        results['web'] = self.build_web()
        
        # 构建桌面应用
        try:
            results['desktop'] = self.build_desktop()
        except Exception as e:
            print(f"❌ 桌面应用构建失败: {e}")
            results['desktop'] = None
        
        # 构建移动端应用
        results['mobile'] = self.build_mobile()
        
        # 生成构建报告
        self._generate_build_report(results)
        
        print("🎉 多端构建完成！")
        return results

    def _generate_build_report(self, results):
        """生成构建报告"""
        report_file = self.dist_dir / "build_report.md"
        
        report_content = f'''# AI视频处理工具 - 多端构建报告

## 构建时间
{self._get_current_time()}

## 构建结果

### Web应用 ✅
- 构建目录: {results['web']}
- 启动方式: `python start.py`
- Docker部署: `docker-compose up`

### 桌面应用 {'✅' if results['desktop'] else '❌'}
- 构建目录: {results['desktop'] or '构建失败'}
- 可执行文件: AI视频处理工具.exe (Windows) / AI视频处理工具 (macOS/Linux)

### 移动端应用 ✅
- React Native: {results['mobile'] / 'react-native'}
- Flutter: {results['mobile'] / 'flutter'}

## 部署说明

### Web部署
1. 进入Web构建目录
2. 安装依赖: `pip install -r requirements.txt`
3. 配置环境变量: 复制.env.example为.env并填写API密钥
4. 启动服务: `python start.py`

### Docker部署
1. 进入Web构建目录
2. 构建镜像: `docker build -t ai-video-processor .`
3. 启动容器: `docker-compose up`

### 桌面应用
直接运行生成的可执行文件即可。

### 移动端开发
1. 安装React Native或Flutter开发环境
2. 进入对应目录
3. 按照框架文档进行开发

## 注意事项
- 确保已安装ffmpeg
- 配置正确的API密钥
- 移动端需要额外的权限配置
'''
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)

    def _get_current_time(self):
        """获取当前时间"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def main():
    """主函数"""
    builder = MultiPlatformBuilder()
    
    if len(sys.argv) > 1:
        platform = sys.argv[1].lower()
        
        if platform == 'web':
            builder.build_web()
        elif platform == 'desktop':
            builder.build_desktop()
        elif platform == 'mobile':
            builder.build_mobile()
        else:
            print("❌ 无效的平台参数")
            print("用法: python build_config.py [web|desktop|mobile|all]")
    else:
        # 默认构建所有平台
        builder.build_all()

if __name__ == '__main__':
    main() 
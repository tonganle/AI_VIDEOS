#!/usr/bin/env python3
"""
AI视频处理工具 - 启动脚本
"""

import os
import sys
from pathlib import Path

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

def check_dependencies():
    """检查依赖是否安装"""
    required_packages = [
        'flask',
        'openai',
        'dashscope',
        'moviepy',
        'alibabacloud_alimt20181012'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ 缺少以下依赖包:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n请运行以下命令安装依赖:")
        print("pip install -r requirements.txt")
        return False
    
    return True

def check_environment():
    """检查环境配置"""
    required_env_vars = [
        'OPENAI_API_KEY',
        'ALI_API_KEY',
        'ALI_CLOUD_ACCESS_KEY_ID',
        'ALI_CLOUD_ACCESS_KEY_SECRET'
    ]
    
    missing_vars = []
    
    for var in required_env_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ 缺少以下环境变量:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n请复制 env.example 为 .env 并填写您的API密钥")
        return False
    
    return True

def check_external_tools():
    """检查外部工具"""
    import subprocess
    
    # 检查ffmpeg
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        print("✅ ffmpeg 已安装")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ ffmpeg 未安装")
        print("请安装 ffmpeg:")
        print("  macOS: brew install ffmpeg")
        print("  Ubuntu: sudo apt install ffmpeg")
        print("  Windows: 下载并安装 ffmpeg")
        return False
    
    # 检查yt-dlp
    try:
        subprocess.run(['yt-dlp', '--version'], capture_output=True, check=True)
        print("✅ yt-dlp 已安装")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ yt-dlp 未安装")
        print("请安装 yt-dlp:")
        print("  pip install yt-dlp")
        return False
    
    return True

def create_directories():
    """创建必要的目录"""
    directories = ['uploads', 'outputs', 'temp']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ 目录 {directory} 已创建")

def main():
    """主函数"""
    print("🚀 AI视频处理工具启动检查...")
    print("=" * 50)
    
    # 检查依赖
    print("📦 检查Python依赖...")
    if not check_dependencies():
        sys.exit(1)
    
    # 检查环境变量
    print("\n🔧 检查环境配置...")
    if not check_environment():
        sys.exit(1)
    
    # 检查外部工具
    print("\n🛠️ 检查外部工具...")
    if not check_external_tools():
        sys.exit(1)
    
    # 创建目录
    print("\n📁 创建必要目录...")
    create_directories()
    
    print("\n✅ 所有检查通过！")
    print("=" * 50)
    
    # 导入并启动应用
    try:
        from app import app
        
        print("🚀 启动AI视频处理工具...")
        print("📱 访问地址: http://localhost:5000")
        print("🛑 按 Ctrl+C 停止服务")
        print("=" * 50)
        
        app.run(host='0.0.0.0', port=5000, debug=True)
        
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
安装脚本

用于安装依赖和设置环境
"""

import subprocess
import sys
import os
from pathlib import Path


def install_requirements():
    """安装依赖包"""
    requirements_file = Path(__file__).parent.parent / 'requirements.txt'
    
    if not requirements_file.exists():
        print("错误: requirements.txt 文件不存在")
        return False
    
    try:
        print("正在安装依赖包...")
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)
        ])
        print("依赖包安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"安装依赖包失败: {e}")
        return False


def check_ffmpeg():
    """检查ffmpeg是否安装"""
    try:
        subprocess.run(['ffmpeg', '-version'], 
                      stdout=subprocess.DEVNULL, 
                      stderr=subprocess.DEVNULL, 
                      check=True)
        print("✓ ffmpeg 已安装")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠ ffmpeg 未安装或不在PATH中")
        print("请安装ffmpeg:")
        print("  macOS: brew install ffmpeg")
        print("  Ubuntu: sudo apt install ffmpeg")
        print("  Windows: 从 https://ffmpeg.org/download.html 下载")
        return False


def create_config_if_not_exists():
    """如果配置文件不存在则创建"""
    config_file = Path(__file__).parent.parent / 'config.json'
    example_file = Path(__file__).parent.parent / 'config.json.example'
    
    if not config_file.exists() and example_file.exists():
        try:
            import shutil
            shutil.copy(example_file, config_file)
            print(f"已创建配置文件: {config_file}")
            print("请编辑配置文件填入正确的参数")
        except Exception as e:
            print(f"创建配置文件失败: {e}")


def main():
    """主函数"""
    print("小鹅通视频下载器 - 环境设置")
    print("=" * 40)
    
    # 安装依赖
    if not install_requirements():
        return 1
    
    # 检查ffmpeg
    check_ffmpeg()
    
    # 创建配置文件
    create_config_if_not_exists()
    
    print("=" * 40)
    print("设置完成!")
    print("使用方法: python main.py --help")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import json
import subprocess
import sys
from typing import Optional
from pathlib import Path


class FileUtils:
    """文件处理工具类"""
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """清理文件名，移除非法字符"""
        # 移除或替换非法字符
        illegal_chars = r'[<>:"/\\|?*]'
        filename = re.sub(illegal_chars, '_', filename)
        
        # 移除控制字符
        filename = ''.join(char for char in filename if ord(char) >= 32)
        
        # 移除首尾空格和点
        filename = filename.strip(' .')
        
        # 如果文件名为空或只包含非法字符，使用默认名称
        if not filename:
            filename = 'untitled'
        
        # 限制文件名长度
        if len(filename) > 200:
            filename = filename[:200]
        
        return filename
    
    @staticmethod
    def ensure_dir(directory: str) -> None:
        """确保目录存在"""
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def get_file_size(file_path: str) -> int:
        """获取文件大小"""
        try:
            return os.path.getsize(file_path)
        except (OSError, FileNotFoundError):
            return 0
    
    @staticmethod
    def remove_file_safely(file_path: str) -> bool:
        """安全删除文件"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
        except OSError:
            pass
        return False
    
    @staticmethod
    def save_json(data: dict, file_path: str) -> bool:
        """保存JSON数据到文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False
    
    @staticmethod
    def load_json(file_path: str) -> Optional[dict]:
        """从文件加载JSON数据"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None
    
    @staticmethod
    def open_file_or_directory(path: str) -> bool:
        """打开文件或目录"""
        try:
            if sys.platform.startswith('win'):
                subprocess.run(['start', path], shell=True, check=True)
            elif sys.platform.startswith('darwin'):
                subprocess.run(['open', path], check=True)
            else:
                subprocess.run(['xdg-open', path], check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    @staticmethod
    def get_available_filename(file_path: str) -> str:
        """获取可用的文件名（如果文件已存在，添加数字后缀）"""
        if not os.path.exists(file_path):
            return file_path
        
        base, ext = os.path.splitext(file_path)
        counter = 1
        
        while True:
            new_path = f"{base}_{counter}{ext}"
            if not os.path.exists(new_path):
                return new_path
            counter += 1
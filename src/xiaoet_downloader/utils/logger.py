#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
from datetime import datetime
from typing import Optional


class Logger:
    """日志工具类"""
    
    _instance: Optional['Logger'] = None
    _logger: Optional[logging.Logger] = None
    
    def __new__(cls) -> 'Logger':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._logger is None:
            self._setup_logger()
    
    def _setup_logger(self) -> None:
        """设置日志记录器"""
        self._logger = logging.getLogger('xiaoet_downloader')
        self._logger.setLevel(logging.INFO)
        
        # 避免重复添加处理器
        if self._logger.handlers:
            return
        
        # 创建日志目录
        log_dir = 'logs'
        os.makedirs(log_dir, exist_ok=True)
        
        # 文件处理器
        log_file = os.path.join(log_dir, f'xiaoet_{datetime.now().strftime("%Y%m%d")}.log')
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self._logger.addHandler(file_handler)
        self._logger.addHandler(console_handler)
    
    def info(self, message: str) -> None:
        """记录信息日志"""
        if self._logger:
            self._logger.info(message)
    
    def warning(self, message: str) -> None:
        """记录警告日志"""
        if self._logger:
            self._logger.warning(message)
    
    def error(self, message: str) -> None:
        """记录错误日志"""
        if self._logger:
            self._logger.error(message)
    
    def debug(self, message: str) -> None:
        """记录调试日志"""
        if self._logger:
            self._logger.debug(message)
    
    def set_level(self, level: int) -> None:
        """设置日志级别"""
        if self._logger:
            self._logger.setLevel(level)


# 全局日志实例
logger = Logger()
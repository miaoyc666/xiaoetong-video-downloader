#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
小鹅通视频下载器

一个用于下载小鹅通课程视频的工具包
"""

__version__ = "2.0.0"
__author__ = "xiaoet-downloader"
__description__ = "小鹅通视频下载器"

from .models.config import XiaoetConfig
from .models.video import VideoResource, VideoMetadata, DownloadResult
from .core.manager import XiaoetDownloadManager
from .utils.logger import logger

__all__ = [
    'XiaoetConfig',
    'VideoResource', 
    'VideoMetadata',
    'DownloadResult',
    'XiaoetDownloadManager',
    'logger'
]
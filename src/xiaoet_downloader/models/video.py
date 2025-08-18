#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum


class ResourceType(Enum):
    """资源类型枚举"""
    VIDEO = 'video'
    AUDIO = 'audio'
    PRODUCT = 'product'


class DownloadStatus(Enum):
    """下载状态枚举"""
    PENDING = 'pending'
    DOWNLOADING = 'downloading'
    COMPLETED = 'completed'
    FAILED = 'failed'
    TRANSCODING = 'transcoding'


@dataclass
class VideoResource:
    """视频资源类"""
    resource_id: str
    title: str
    resource_type: ResourceType = ResourceType.VIDEO
    play_url: Optional[str] = None
    play_sign: Optional[str] = None
    is_available: bool = True
    download_status: DownloadStatus = DownloadStatus.PENDING
    file_path: Optional[str] = None
    error_message: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VideoResource':
        """从字典创建VideoResource实例"""
        return cls(
            resource_id=data.get('id', ''),
            title=data.get('title', ''),
            resource_type=ResourceType.VIDEO if data.get('id', '').startswith('v_') else ResourceType.AUDIO,
            is_available=data.get('is_available', 1) == 1
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'resource_id': self.resource_id,
            'title': self.title,
            'resource_type': self.resource_type.value,
            'play_url': self.play_url,
            'play_sign': self.play_sign,
            'is_available': self.is_available,
            'download_status': self.download_status.value,
            'file_path': self.file_path,
            'error_message': self.error_message
        }


@dataclass
class VideoMetadata:
    """视频元数据类"""
    title: str
    complete: bool
    total_segments: int = 0
    downloaded_segments: int = 0
    file_size: int = 0
    duration: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'title': self.title,
            'complete': self.complete,
            'total_segments': self.total_segments,
            'downloaded_segments': self.downloaded_segments,
            'file_size': self.file_size,
            'duration': self.duration
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VideoMetadata':
        """从字典创建VideoMetadata实例"""
        return cls(
            title=data.get('title', ''),
            complete=data.get('complete', False),
            total_segments=data.get('total_segments', 0),
            downloaded_segments=data.get('downloaded_segments', 0),
            file_size=data.get('file_size', 0),
            duration=data.get('duration')
        )


@dataclass
class DownloadResult:
    """下载结果类"""
    resource: VideoResource
    success: bool
    message: str
    file_path: Optional[str] = None
    
    def __str__(self) -> str:
        status = "成功" if self.success else "失败"
        return f"[{status}] {self.resource.title}: {self.message}"
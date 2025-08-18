#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import ffmpy
from typing import Optional

from ..models.video import VideoResource, VideoMetadata, DownloadResult, DownloadStatus
from ..utils.file_utils import FileUtils
from ..utils.logger import logger


class VideoTranscoder:
    """视频转码器"""
    
    def __init__(self, download_dir: str):
        """初始化转码器"""
        self.download_dir = download_dir
    
    def transcode_video(self, resource: VideoResource) -> DownloadResult:
        """
        转码视频
        
        Args:
            resource: 视频资源对象
            
        Returns:
            DownloadResult: 转码结果
        """
        resource_dir = os.path.join(self.download_dir, resource.resource_id)
        metadata_file = os.path.join(resource_dir, 'metadata.json')
        
        if not os.path.exists(resource_dir) or not os.path.exists(metadata_file):
            return DownloadResult(resource, False, "资源目录或元数据不存在")
        
        try:
            # 加载元数据
            metadata_dict = FileUtils.load_json(metadata_file)
            if not metadata_dict:
                return DownloadResult(resource, False, "元数据文件格式错误")
            
            metadata = VideoMetadata.from_dict(metadata_dict)
            
            if not metadata.complete:
                return DownloadResult(resource, False, "视频下载不完整，无法合并")
            
            # 处理文件名，替换非法字符
            safe_title = FileUtils.sanitize_filename(metadata.title)
            if not safe_title:
                safe_title = resource.resource_id
            
            output_file = os.path.join(self.download_dir, safe_title + '.mp4')
            
            # 检查输出文件是否已存在
            if os.path.exists(output_file):
                logger.info(f"文件 {output_file} 已存在，跳过合并")
                return DownloadResult(resource, True, "文件已存在，跳过合并", output_file)
            
            # 更新资源状态
            resource.download_status = DownloadStatus.TRANSCODING
            logger.info(f"开始合并视频: {safe_title}")
            
            # 使用ffmpy进行视频合并
            input_file = os.path.join(resource_dir, 'video.m3u8')
            ff = ffmpy.FFmpeg(
                inputs={input_file: ['-protocol_whitelist', 'crypto,file,http,https,tcp,tls']}, 
                outputs={output_file: "-c:v copy -c:a copy"}
            )
            
            logger.info(f"执行命令: {ff.cmd}")
            ff.run()
            
            # 验证输出文件
            if os.path.exists(output_file) and FileUtils.get_file_size(output_file) > 0:
                resource.download_status = DownloadStatus.COMPLETED
                resource.file_path = output_file
                logger.info(f"视频合并完成: {output_file}")
                return DownloadResult(resource, True, "合并完成", output_file)
            else:
                return DownloadResult(resource, False, "合并后文件不存在或为空")
                
        except ffmpy.FFExecutableNotFoundError:
            error_msg = "未找到ffmpeg可执行文件，请确保已正确安装ffmpeg"
            logger.error(error_msg)
            return DownloadResult(resource, False, error_msg)
        except ffmpy.FFRuntimeError as e:
            error_msg = f"视频合并过程中出错: {str(e)}"
            logger.error(error_msg)
            # 如果输出文件已部分创建但不完整，删除它
            if os.path.exists(output_file):
                FileUtils.remove_file_safely(output_file)
                logger.info(f"已删除不完整的输出文件: {output_file}")
            return DownloadResult(resource, False, error_msg)
        except Exception as e:
            error_msg = f"合并视频时发生未知错误: {str(e)}"
            logger.error(error_msg)
            return DownloadResult(resource, False, error_msg)
        finally:
            # 确保状态不是TRANSCODING
            if resource.download_status == DownloadStatus.TRANSCODING:
                resource.download_status = DownloadStatus.FAILED
    
    def check_ffmpeg_availability(self) -> bool:
        """检查ffmpeg是否可用"""
        try:
            ff = ffmpy.FFmpeg(inputs={'dummy': None}, outputs={'dummy': None})
            # 只是检查ffmpeg是否存在，不实际运行
            return True
        except ffmpy.FFExecutableNotFoundError:
            return False
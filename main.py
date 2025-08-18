#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
小鹅通视频下载器主程序

使用方法:
    python main.py                   # 下载整个课程
    python main.py --single <id>     # 下载单个视频
    python main.py --check           # 检查环境
    python main.py --help            # 显示帮助
"""

import argparse
import os
import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from xiaoet_downloader import XiaoetConfig, XiaoetDownloadManager, logger


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='小鹅通视频下载器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python main.py                           # 下载整个课程
  python main.py --single v_123456        # 下载单个视频
  python main.py --config custom.json     # 使用自定义配置文件
  python main.py --no-cache               # 忽略缓存重新下载
  python main.py --no-transcode           # 只下载不转码
  python main.py --check                  # 检查运行环境
        """
    )
    
    parser.add_argument(
        '--config', '-c',
        default='config.json',
        help='配置文件路径 (默认: config.json)'
    )
    
    parser.add_argument(
        '--single', '-s',
        help='下载单个视频资源ID'
    )
    
    parser.add_argument(
        '--no-cache',
        action='store_true',
        help='忽略缓存，重新下载所有文件'
    )
    
    parser.add_argument(
        '--no-transcode',
        action='store_true',
        help='只下载不转码'
    )
    
    parser.add_argument(
        '--check',
        action='store_true',
        help='检查运行环境'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='显示详细日志'
    )
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.verbose:
        import logging
        logger.set_level(logging.DEBUG)
    
    try:
        # 加载配置
        if not os.path.exists(args.config):
            logger.error(f"配置文件不存在: {args.config}")
            logger.info("请创建配置文件，参考 config.json.example")
            return 1
        
        config = XiaoetConfig.from_file(args.config)
        manager = XiaoetDownloadManager(config)
        
        # 检查环境
        if args.check:
            if manager.check_environment():
                logger.info("环境检查通过")
                return 0
            else:
                logger.error("环境检查失败")
                return 1
        
        # 检查环境（静默）
        if not manager.check_environment():
            logger.error("环境检查失败，请先解决环境问题")
            return 1
        
        # 下载单个视频
        if args.single:
            logger.info(f"开始下载单个视频: {args.single}")
            result = manager.download_single_video(
                args.single,
                nocache=args.no_cache,
                auto_transcode=not args.no_transcode
            )
            
            if result.success:
                logger.info(f"下载成功: {result.message}")
                return 0
            else:
                logger.error(f"下载失败: {result.message}")
                return 1
        
        # 下载整个课程
        logger.info("开始下载课程")
        results = manager.download_course(
            nocache=args.no_cache,
            auto_transcode=not args.no_transcode
        )
        
        # 返回适当的退出码
        if results['failed']:
            return 1
        else:
            return 0
            
    except KeyboardInterrupt:
        logger.info("用户中断下载")
        return 130
    except Exception as e:
        logger.error(f"程序执行出错: {str(e)}")
        if args.verbose:
            import traceback
            logger.error(traceback.format_exc())
        return 1


if __name__ == '__main__':
    sys.exit(main())
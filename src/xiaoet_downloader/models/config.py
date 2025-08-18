#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class XiaoetConfig:
    """小鹅通配置类"""
    app_id: str
    cookie: str
    product_id: str
    download_dir: str = 'download'
    
    @classmethod
    def from_file(cls, config_path: str) -> 'XiaoetConfig':
        """从配置文件加载配置"""
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                config_data = json.load(file)
            
            return cls(
                app_id=config_data.get('app_id', ''),
                cookie=config_data.get('cookie', ''),
                product_id=config_data.get('product_id', ''),
                download_dir=config_data.get('download_dir', 'download')
            )
        except FileNotFoundError:
            raise FileNotFoundError(f"配置文件 {config_path} 不存在")
        except json.JSONDecodeError:
            raise ValueError("配置文件内容不是有效的 JSON 格式")
        except Exception as e:
            raise Exception(f"读取配置文件时发生错误: {e}")
    
    def validate(self) -> bool:
        """验证配置是否完整"""
        if not self.app_id:
            raise ValueError("app_id 不能为空")
        if not self.cookie:
            raise ValueError("cookie 不能为空")
        if not self.product_id:
            raise ValueError("product_id 不能为空")
        return True
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'app_id': self.app_id,
            'cookie': self.cookie,
            'product_id': self.product_id,
            'download_dir': self.download_dir
        }
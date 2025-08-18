#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import tempfile
import json
import os
import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from xiaoet_downloader.models.config import XiaoetConfig


class TestXiaoetConfig(unittest.TestCase):
    """测试XiaoetConfig类"""
    
    def setUp(self):
        """设置测试环境"""
        self.test_config = {
            "app_id": "test_app_id",
            "cookie": "test_cookie",
            "product_id": "test_product_id",
            "download_dir": "test_download"
        }
    
    def test_from_dict(self):
        """测试从字典创建配置"""
        config = XiaoetConfig(
            app_id=self.test_config["app_id"],
            cookie=self.test_config["cookie"],
            product_id=self.test_config["product_id"],
            download_dir=self.test_config["download_dir"]
        )
        
        self.assertEqual(config.app_id, "test_app_id")
        self.assertEqual(config.cookie, "test_cookie")
        self.assertEqual(config.product_id, "test_product_id")
        self.assertEqual(config.download_dir, "test_download")
    
    def test_from_file(self):
        """测试从文件加载配置"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.test_config, f)
            temp_file = f.name
        
        try:
            config = XiaoetConfig.from_file(temp_file)
            self.assertEqual(config.app_id, "test_app_id")
            self.assertEqual(config.cookie, "test_cookie")
            self.assertEqual(config.product_id, "test_product_id")
            self.assertEqual(config.download_dir, "test_download")
        finally:
            os.unlink(temp_file)
    
    def test_validate_success(self):
        """测试配置验证成功"""
        config = XiaoetConfig(
            app_id="test_app_id",
            cookie="test_cookie",
            product_id="test_product_id"
        )
        
        self.assertTrue(config.validate())
    
    def test_validate_failure(self):
        """测试配置验证失败"""
        config = XiaoetConfig(
            app_id="",
            cookie="test_cookie",
            product_id="test_product_id"
        )
        
        with self.assertRaises(ValueError):
            config.validate()
    
    def test_to_dict(self):
        """测试转换为字典"""
        config = XiaoetConfig(
            app_id="test_app_id",
            cookie="test_cookie",
            product_id="test_product_id",
            download_dir="test_download"
        )
        
        result = config.to_dict()
        expected = {
            'app_id': 'test_app_id',
            'cookie': 'test_cookie',
            'product_id': 'test_product_id',
            'download_dir': 'test_download'
        }
        
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
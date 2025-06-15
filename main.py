#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
File name    : main.py
Author       : miaoyc
Create time  : 2025/3/8 21:11
Update time  : 2025/6/14 21:11
Description  :
"""

import ast
import ffmpy
import m3u8
import os
import json
import requests

from m3u8.model import SegmentList, Segment, find_key


def load_config(config_path):
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config_data = json.load(file)
        return config_data
    except FileNotFoundError:
        print(f"错误: 文件 {config_path} 不存在")
    except json.JSONDecodeError:
        print("错误: 文件内容不是有效的 JSON 格式")
    except Exception as e:
        print(f"读取文件时发生错误: {e}")


def download_file(url, save_path):
    """
    下载指定 URL 的文件并保存到本地
    :param url: 文件的 URL
    :param save_path: 保存文件的本地路径
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # 检查请求是否成功
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
    except requests.exceptions.RequestException as e:
        print(f"下载失败: {e}")


def extract_ts_urls(m3u8_file):
    """
    从 m3u8 文件中提取 ts 文件的 URL 列表
    :param m3u8_file: m3u8 文件路径
    :return: ts 文件的 URL 列表
    """
    with open(m3u8_file, 'r', encoding='utf-8') as file:
        m3u8_content = file.read()
    playlist = m3u8.loads(m3u8_content)
    ts_urls = [segment.uri for segment in playlist.segments]
    return ts_urls


def create_file_list(ts_files, list_file_path):
    """
    创建包含 ts 文件路径的列表文件
    :param ts_files: ts 文件路径列表
    :param list_file_path: 列表文件保存路径
    """
    with open(list_file_path, 'w') as file:
        for ts_file in ts_files:
            file.write(f"file '{ts_file}'\n")
    print(f"文件列表已保存到: {list_file_path}")


def merge_ts_files(list_file_path, output_file):
    """
    使用 ffmpeg 合并 ts 文件
    :param list_file_path: 包含 ts 文件路径的列表文件
    :param output_file: 合并后的输出文件路径
    """
    command = f"ffmpeg -f concat -safe 0 -i {list_file_path} -c copy {output_file}"
    os.system(command)
    print(f"合并完成，输出文件: {output_file}")


class Xet(object):
    def __init__(self, conf=None):
        if conf:
            self.config = conf
        else:
            current_dir = os.getcwd()
            config_path = os.path.join(current_dir, 'config.json')
            self.config = load_config(config_path)
        # init config
        self.host = self.config['host']
        self.app_id = self.config['app_id']
        self.base_url = f"https://{self.app_id}.{self.host}"
        self.cookie = self.config['cookie']
        self.product_id = self.config['product_id']
        self.download_dir = self.config['download_dir']
        # int urls
        self.get_column_items_url = f"{self.base_url}/xe.course.business.column.items.get/2.0.0"
        self.get_video_details_info_url = f"{self.base_url}/xe.course.business.video.detail_info.get/2.0.0"
        self.get_micro_navigation_url = f"{self.base_url}/xe.micro_page.navigation.get/1.0.0"
        self.get_play_url = f"{self.base_url}/xe.material-center.play/getPlayUrl"

    def get_video_detail_info(self, v_resource_id):
        payload = {
            'bizData[resource_id]': v_resource_id,
            'bizData[product_id]': self.product_id,
            'bizData[opr_sys]': 'MacIntel'
        }
        headers = {
            'cookie': self.cookie,
        }
        response = requests.request("POST", self.get_video_details_info_url, headers=headers, data=payload)
        data = json.loads(response.text).get('data').get('video_info')
        return data

    def get_column_items(self, column_id, page_index=1, page_size=100, sort='desc'):
        payload = {
            'bizData[column_id]': column_id,
            'bizData[page_index]': str(page_index),
            'bizData[page_size]': str(page_size),
            'bizData[sort]': sort
        }
        headers = {
            'cookie': self.cookie,
        }
        response = requests.request("POST", self.get_column_items_url, headers=headers, data=payload)
        data = json.loads(response.text).get('data')
        return [(i.get('resource_id'), i.get('resource_title')) for i in data.get('list')]

    def get_mico_navigation_info(self, app_id):
        payload = json.dumps({
            "app_id": app_id,
            "agent_type": 1,
            "app_version": 0
        })
        headers = {
            'cookie': self.cookie,
        }
        response = requests.request("POST", self.get_micro_navigation_url, headers=headers, data=payload)
        return json.loads(response.text).get('data', {})

    def get_play(self, app_id, user_id, play_sign):
        payload = json.dumps({
            "org_app_id": app_id,
            "app_id": app_id,
            "user_id": user_id,
            "play_sign": [
                play_sign
            ],
            "play_line": "A",
            "opr_sys": "MacIntel"
        })
        headers = {
            'cookie': self.cookie,
        }
        response = requests.request("POST", self.get_play_url, headers=headers, data=payload)
        return json.loads(response.text).get('data', {}).get(play_sign, {}).get('play_list', {})

    def download_video(self, download_dir, play_list_info, v_resource_id):
        current_dir = os.getcwd()
        resource_dir = os.path.join(download_dir, v_resource_id)
        os.makedirs(resource_dir, exist_ok=True)

        # 获取play_info
        play_info = play_list_info.get('720p_hls', {})
        m3u8_file_url = play_info.get('play_url')

        # 下载m3u8文件
        m3u8_file_path = os.path.join(current_dir, "m3u8", f"{v_resource_id}.m3u8")
        print(f"Downloading M3U8 file to: {m3u8_file_path}")
        download_file(m3u8_file_url, m3u8_file_path)

        # 提取 m3u8 文件中的 ts 文件 URL 列表
        ext = play_info.get('ext', {})
        # ext 参数示例
        # "ext": {
        #    "host": "https://v-tos-k.xiaoeknow.com",
        #    "path": "2919df88vodtranscq1252524126/2591e9eb387702303541605952/drm",
        #    "param": "sign=8dbfe87b7b39bc6bb7f00a3f358c1871\u0026t=684e210e\u0026us=jCANilCutB"
        # }
        ts_base_url = str(os.path.join(ext.get('host'), ext.get('path')))
        ts_urls = extract_ts_urls(m3u8_file_path)
        ts_urls = [os.path.join(ts_base_url, ts_url) for ts_url in ts_urls]

        ts_files = []
        list_file_path = os.path.join(str(resource_dir), "file_list.txt")
        for index, ts_url in enumerate(ts_urls):
            print(f"Downloading segment {index + 1}: {ts_url}")

            # 生成 ts 文件的本地路径
            file_name = f'segment_{index + 1}.ts'
            ts_file = os.path.join(str(resource_dir), file_name)
            print(f"TS file path: {ts_file}")
            ts_files.append(file_name)
            if os.path.exists(ts_file):
                print(f"Already Downloaded: {ts_file}")
            else:
                #download_file(ts_url, ts_file)
                print(f"Downloaded: {ts_file}")

        # 创建包含 ts 文件路径的列表文件
        create_file_list(ts_files, list_file_path)
        # 合并 ts 文件
        output_file = "output.ts"
        merge_ts_files(list_file_path, output_file)
        return


def main():
    # 业务逻辑：
    # 1. 获取配置，准备数据

    current_dir = os.getcwd()
    config_path = os.path.join(current_dir, 'config.json')
    conf = load_config(config_path)

    app_id = conf["app_id"]  # app_id
    column_id = conf["product_id"]  # 课程id
    #
    xet = Xet(conf)

    # 获取user_id（别的方法也可以获取，都行）
    # get_mico_navigation_info是点击个人中心时调用的接口之一
    navigation_info = xet.get_mico_navigation_info(app_id)
    user_id = navigation_info['user_id']
    print(f"User ID: {user_id}")
    v_resource_ids = xet.get_column_items(column_id)
    print(f"Video Resource IDs: {v_resource_ids}")
    for v_resource_id, resource_title in v_resource_ids:
        video_details_info = xet.get_video_detail_info(v_resource_id)
        # 获取 play_sign
        play_sign = video_details_info.get('play_sign')
        print(f"Video Resource ID: {v_resource_id}, Title: {resource_title}, Play Sign: {play_sign}")
        play_list_info = xet.get_play(app_id, user_id, play_sign)
        xet.download_video(xet.download_dir, play_list_info, v_resource_id)

        break


if __name__ == '__main__':
    main()

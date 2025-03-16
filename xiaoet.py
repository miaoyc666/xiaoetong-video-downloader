#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ast
import base64
import ffmpy
import m3u8
import os
import json
import requests
import subprocess
import time
import sys

from m3u8.model import SegmentList, Segment, find_key
from bs4 import BeautifulSoup


GET_COLUMN_ITEMS_URL = "https://{0}.h5.xiaoeknow.com/xe.course.business.column.items.get/2.0.0"
GET_VIDEO_DETAILS_INFO_URL = "https://{0}.h5.xiaoeknow.com/xe.course.business.video.detail_info.get/2.0.0"
GET_MICRO_NAVIGATION_URL = "https://{0}.h5.xiaoeknow.com/xe.micro_page.navigation.get/1.0.0"
GET_PLAY_URL = "https://{0}.h5.xiaoeknow.com/xe.material-center.play/getPlayUrl"


class Xet(object):
    def __init__(self, conf=None):
        if conf:
            self.config = conf
        else:
            current_dir = os.getcwd()
            config_path = os.path.join(current_dir, 'config.json')
            self.config = self.load_config(config_path)
        self.appid = self.config['app_id']
        self.cookie = self.config['cookie']
        self.product_id = self.config['product_id']
        self.download_dir = 'download'

    def load_config(self, config_path):
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

    def openfile(self, filepath):
        if sys.platform.startswith('win'):
            return subprocess.run(['call', filepath], shell=True)
        else:
            return subprocess.run(['open', filepath])

    def get_product_list(self):
        url = 'https://pc-shop.xiaoe-tech.com/{appid}/open/column.all.get/2.0'.format(appid=self.appid)
        body = {
            'data[page_index]': '0',
            'data[page_size]': '1000',
            'data[order_by]': 'start_at:desc',
            'data[state]': '0',
        }
        self.session.headers.update(
            {'Referer': 'https://pc-shop.xiaoe-tech.com/{appid}/'.format(appid=self.appid)})
        res = self.session.post(url, data=body)
        if res.status_code == 200:
            content = ast.literal_eval(res.content.decode("UTF-8"))
            if not content['code']:
                for product in content['data']:
                    print('name: {} price: {} productid: {}'.format(product['title'], int(product['price']) / 100, product['id']))
                return content['data']
            else:
                print('status: {} msg: {}'.format(content['code'], content['msg']))
        return

    def get_resource_list(self, productid):
        url = 'https://pc-shop.xiaoe-tech.com/{appid}/open/column.resourcelist.get/2.0'.format(appid=self.appid)
        body = {
            'data[page_index]': '0',
            'data[page_size]': '1000',
            'data[order_by]': 'start_at:desc',
            'data[resource_id]': productid,
            'data[state]': '0'
        }
        self.session.headers.update({'Referer': 'https://pc-shop.xiaoe-tech.com/{appid}/'.format(appid=self.appid)})
        res = self.session.post(url, data=body)
        if res.status_code == 200:
            content = ast.literal_eval(res.content.decode("UTF-8"))
            if not content['code']:
                for resource in content['data']:
                    print('name: {} resourceid: {}'.format(resource['title'], resource['id']))
                return content['data']
            else:
                print('status: {} msg: {}'.format(content['code'], content['msg']))
        return

    def transform_type(self, id):
        transform_box = {'a': 'audio', 'v': 'video', 'p': 'product'}
        type = transform_box.get(id[0], None)
        if type:
            return type
        else:
            print('Invalid id. None suitable type')
            exit (1)

    def get_resource(self, resourceid):
        resourcetype = self.transform_type(resourceid)
        url = 'https://pc-shop.xiaoe-tech.com/{appid}/open/{resourcetype}.detail.get/1.0'.format(appid=self.appid,
                                                                                  resourcetype=resourcetype)
        body = {
            'data[resource_id]': resourceid
        }
        self.session.headers.update({'Referer': 'https://pc-shop.xiaoe-tech.com/{appid}/{resourcetype}_details?id={resourceid}'.format(
            appid=self.appid, resourcetype=resourcetype, resourceid=resourceid)})
        res = self.session.post(url, data=body)
        if res.status_code == 200:
            content = ast.literal_eval(res.content.decode("UTF-8"))
            if not content['code']:
                return content['data']
            else:
                print('status: {} msg: {}'.format(content['code'], content['msg']))
        return {'id': resourceid}

    def get_productid(self, resourceid):
        res = self.get_resource(resourceid)
        if res.get('products'):
            print (res['products'][0]['product_id'])
        return

    def download_video(self, download_dir, resource, nocache=False):
        resource_dir = os.path.join(download_dir, resource['id'])
        os.makedirs(resource_dir, exist_ok=True)

        url = resource['video_hls'].replace('\\', '')
        self.session.headers.update({'Referer': 'https://pc-shop.xiaoe-tech.com/{appid}/video_details?id={resourceid}'.format(
                appid=self.appid, resourceid=resource['id'])})
        media = m3u8.loads(self.session.get(url).text)
        url_prefix, segments, changed, complete = url.split('v.f230')[0], SegmentList(), False, True

        print('Total: {} part'.format(len(media.data['segments'])))
        for index, segment in enumerate(media.data['segments']):
            ts_file = os.path.join(resource_dir, 'v_{}.ts'.format(index))
            if not nocache and os.path.exists(ts_file):
                print('Already Downloaded: {title} {file}'.format(title=resource['title'], file=ts_file))
            else:
                url = url_prefix + segment.get('uri')
                res = self.session.get(url)
                if res.status_code == 200:
                    with open(ts_file + '.tmp', 'wb') as ts:
                        ts.write(res.content)
                    os.rename(ts_file + '.tmp', ts_file)
                    changed = True
                    print('Download Successful: {title} {file}'.format(title=resource['title'], file=ts_file))
                else:
                    print('Download Failed: {title} {file}'.format(title=resource['title'], file=ts_file))
                    complete = False
            segment['uri'] = 'v_{}.ts'.format(index)
            segments.append(Segment(base_uri=None, keyobject=find_key(segment.get('key', {}), media.keys), **segment))

        m3u8_file = os.path.join(resource_dir, 'video.m3u8')
        if changed or not os.path.exists(m3u8_file):
            media.segments = segments
            with open(m3u8_file, 'w', encoding='utf8') as f:
                f.write(media.dumps())
        metadata = {'title': resource['title'], 'complete': complete}
        with open(os.path.join(download_dir, resource['id'], 'metadata'), 'w') as f:
            json.dump(metadata, f)
        return

    def download_audio(self, download_dir, resource, nocache=False):
        url = resource['audio_url'].replace('\\', '')
        audio_file = os.path.join(download_dir, '{title}.{suffix}'.format(title=resource['title'], suffix=os.path.basename(url).split('.')[-1]))
        if not nocache and os.path.exists(audio_file):
            print('Already Downloaded: {title} {file}'.format(title=resource['title'], file=audio_file))
        else:
            self.session.headers.update(
                {'Referer': 'https://pc-shop.xiaoe-tech.com/{appid}/audio_details?id={resourceid}'.format(
                    appid=self.appid, resourceid=resource['id'])})
            res = self.session.get(url, stream=True)
            if res.status_code == 200:
                with open(audio_file, 'wb') as f:
                    f.write(res.content)
                print('Download Successful: {title} {file}'.format(title=resource['title'], file=audio_file))
            else:
                print('Download Failed: {title} {file}'.format(title=resource['title'], file=audio_file))
        return

    def transcode(self, resourceid):
        resource_dir = os.path.join(self.download_dir, resourceid)
        if os.path.exists(resource_dir) and os.path.exists(os.path.join(resource_dir, 'metadata')):
            with open(os.path.join(resource_dir, 'metadata')) as f:
                metadata = json.load(f)
            if metadata['complete']:
                ff = ffmpy.FFmpeg(inputs={os.path.join(resource_dir, 'video.m3u8'): ['-protocol_whitelist', 'crypto,file,http,https,tcp,tls']}, outputs={os.path.join(self.download_dir, metadata['title'] + '.mp4'): "-c:v copy -c:a copy"})
                print(ff.cmd)
                ff.run()
        return

    def download(self, id, nocahce=False):
        os.makedirs(self.download_dir, exist_ok=True)
        if self.transform_type(id) == 'product':
            resource_list = [self.get_resource(resource['id']) for resource in self.get_resource_list(id)]
        else:
            resource_list = [self.get_resource(id)]

        for resource in resource_list:
            if resource.get('is_available') == 1:
                if self.transform_type(resource['id']) == 'audio':
                    self.download_audio(self.download_dir, resource, nocahce)
                elif self.transform_type(resource['id']) == 'video':
                    self.download_video(self.download_dir, resource, nocahce)
                    self.transcode(resource['id'])
            elif resource.get('is_available') == 0:
                print('Not purchased. name: {} resourceid: {}'.format(resource['title'], resource['id']))
            else:
                print('Not Found. resourceid: {}'.format(resource['id']))
        return

    def get_video_detail_info(self, url, v_resource_id):
        payload = {
            'bizData[resource_id]': v_resource_id,
            'bizData[product_id]': self.product_id,
            'bizData[opr_sys]': 'MacIntel'
        }
        headers = {
            'cookie': self.cookie,
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        data = json.loads(response.text).get('data').get('video_info')
        return data

    def get_column_items(self, url, column_id, page_index=1, page_size=100, sort='desc'):
        payload = {
            'bizData[column_id]': column_id,
            'bizData[page_index]': str(page_index),
            'bizData[page_size]': str(page_size),
            'bizData[sort]': sort
        }
        headers = {
            'cookie': self.cookie,
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        data = json.loads(response.text).get('data')
        return [(i.get('resource_id'), i.get('resource_title')) for i in data.get('list')]

    def get_mico_navigation_info(self, url, app_id):
        payload = json.dumps({
            "app_id": app_id,
            "agent_type": 1,
            "app_version": 0
        })
        headers = {
            'cookie': self.cookie,
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        data = json.loads(response.text).get('data', {})
        return data

    def get_play_url(self, url, app_id, user_id, play_sign):
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
        response = requests.request("POST", url, headers=headers, data=payload)
        play_list_dict = json.loads(response.text).get('data', {}).get(play_sign, {}).get('play_list', {})
        return play_list_dict


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


def main():
    # 业务逻辑：
    # 1. 获取配置，准备数据

    current_dir = os.getcwd()
    config_path = os.path.join(current_dir, 'config.json')
    conf = load_config(config_path)

    app_id = conf["app_id"]  # app_id
    column_id = conf["product_id"]  # 课程id

    get_column_items_url = GET_COLUMN_ITEMS_URL.format(app_id)
    get_video_details_info_url = GET_VIDEO_DETAILS_INFO_URL.format(app_id)
    get_micro_navigation_url = GET_MICRO_NAVIGATION_URL.format(app_id)
    get_play_url = GET_PLAY_URL.format(app_id)
    #
    xet = Xet(conf)
    navigation_info = xet.get_mico_navigation_info(get_micro_navigation_url, app_id)
    user_id = navigation_info['user_id']
    v_resource_ids = xet.get_column_items(get_column_items_url, column_id)
    for v_resource_id, resource_title in v_resource_ids:
        video_details_info = xet.get_video_detail_info(get_video_details_info_url, v_resource_id)
        play_sign = video_details_info.get('play_sign')
        play_list_dict = xet.get_play_url(get_play_url, app_id, user_id, play_sign)
        play_url = play_list_dict.get('720p_hls', {}).get('play_url')
        print(play_url)


if __name__ == '__main__':
    main()

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


GET_COLUMN_ITEMS_URL = "https://app5bsvjqkl5234.h5.xiaoeknow.com/xe.course.business.column.items.get/2.0.0"
GET_VIDEO_DETAILS_INFO_URL = "https://app5bsvjqkl5234.h5.xiaoeknow.com/xe.course.business.video.detail_info.get/2.0.0"


class Xet(object):
    def __init__(self, conf=None):
        if conf:
            self.config = conf
        else:
            current_dir = os.getcwd()
            config_path = os.path.join(current_dir, 'config.json')
            self.config = self.load_config(config_path)
        self.appid = self.config['appid']
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
            
    def login(self, re_login=False):
        session = requests.Session()
        if not re_login and self.configs.get('last_appid') == self.appid and (time.time() - self.configs.get('cookies_time')) < 14400: # 4小时
            for key, value in self.configs['cookies'].items():
                session.cookies[key] = value
        else:
            headers = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 6_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
                'Referer': '',
                'Origin': 'https://pc-shop.xiaoe-tech.com',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            html = session.get('https://pc-shop.xiaoe-tech.com/{appid}/login'.format(appid=self.appid), headers=headers).text
            soup = BeautifulSoup(html, 'lxml')
            initdata = json.loads(soup.find(name='input', id='initData')['value'])
            with open('qrcode.png', 'wb') as file:
                file.write(base64.b64decode(initdata['qrcodeImg']))
            self.openfile('qrcode.png')
            # Wait for QRcode to be scanned
            islogin = False
            for _ in range(300):
                res = json.loads(session.post('https://pc-shop.xiaoe-tech.com/{appid}/checkIfUserHasLogin'.format(appid=self.appid), data={'code': initdata['code']}).text)
                if not res['code'] and res['data']['code'] == 1:
                    islogin = True
                    break
                else:
                    time.sleep(1)
            if islogin:
                os.remove('qrcode.png')
                session.get('https://pc-shop.xiaoe-tech.com/{appid}/pcLogin/0?code={code}'.format(appid=self.appid, code=initdata['code']))
                self.configs['last_appid'] = self.appid
                self.configs['cookies_time'] = time.time()
                self.configs['cookies'] = requests.utils.dict_from_cookiejar(session.cookies)
                self.config('w')
            else:
                print('Log in timeout')
                exit(1)
        return session

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

    def get_video_detail_info(self, v_resource_id):
        payload = {
            'bizData[resource_id]': v_resource_id,
            'bizData[product_id]': self.product_id,
            'bizData[opr_sys]': 'MacIntel'
        }
        headers = {
            'cookie': self.cookie,
        }
        response = requests.request("POST", GET_VIDEO_DETAILS_INFO_URL, headers=headers, data=payload)
        data = json.loads(response.text).get('data').get('video_info')
        print(data)
        return response.text

    def get_column_items(self, column_id, page_index=1, page_size=100, sort='desc'):
        payload = {
            'bizData[column_id]': column_id,
            'bizData[page_index]': str(page_index),
            'bizData[page_size]': str(page_size),
            'bizData[sort]': sort
        }
        files = []
        headers = {
            'cookie': self.cookie,
        }
        response = requests.request("POST", GET_COLUMN_ITEMS_URL, headers=headers, data=payload, files=files)
        data = json.loads(response.text).get('data')
        return [(i.get('resource_id'), i.get('resource_title')) for i in data.get('list')]


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
    current_dir = os.getcwd()
    config_path = os.path.join(current_dir, 'config.json')
    conf = load_config(config_path)

    xet = Xet(conf)
    column_id = conf["product_id"]  # 课程id
    v_resource_ids = xet.get_column_items(column_id)
    for v_resource_id, resource_title in v_resource_ids:
        print(resource_title, v_resource_id)
        video_details_info = xet.get_video_detail_info(v_resource_id)
        print(video_details_info)
        break


if __name__ == '__main__':
    main()

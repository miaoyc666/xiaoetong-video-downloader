# Download Xiaoet videos
> 小鹅通资源下载工具

> 本工具仅支持用户已购买课程的下载，并不存在付费课程的破解

> 本工具仅供自用和学习交流使用，请勿用于商业用途


## 代码改版，近期不要使用啦   2025-6-15

## 一、安装

#### 1. 安装python 依赖

使用如下命令安装依赖：
```
sudo pip3 install -r requirements.txt
```
或者

```
sudo pip3 install ffmpy m3u8 beautifulsoup4 lxml requests
```

#### 2. 安装ffmpeg

在 MacOS 上可以使用`brew`来安装`ffmeg`工具。如果没有`brew`，可以通过下面命令安装：
```
ruby -e"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```

安装`ffmeg`的命令是：
```
brew install ffmpeg
```

安装完成后检验是否安装正确：
```
brew info ffmpeg
```

本工具中用到`ffmeg`的地方是，使用它将下载下来的`m3u8`文件转换到`mp4`格式。
其使用方式是：
```
ffmpeg -i 视频地址 [输出的文件名.mp4]
```
例如：
```
ffmpeg -i https://xxx.xxx/xxxxxx/001.m3u8 /Downloads/xx.mp4
```
这部分的转换操作已经在脚本中执行完成，因此无需手动执行上述命令。

## 二、使用方法示例     
#### 配置文件
```bash
config.json
```
#### 配置项说明
| 字段         | 说明              | 获取方式                                                                                                                                              |
|------------|-----------------|---------------------------------------------------------------------------------------------------------------------------------------------------|
| host       | 小鹅通web端api的host | 所见即所得，例如xet.citv.cn或h5.xiaoeknow.com                                                                                                              |
| cookie     | 小鹅通web端的Cookie  | web端登录后浏览器检查元素即可获取到Cookie                                                                                                                         |
| app_id     | 店铺唯一标识          | 课程链接url中获取，示例: 课程链接https://appisb9y2un7034.xet.citv.cn/p/course/column/p_608baa19e4b071a81eb6ebbc?xxxxxxx 中的appisb9y2un7034即是app_id               |
| product_id | 课程唯一标识          | 课程链接url中获取，示例: 课程链接https://appisb9y2un7034.xet.citv.cn/p/course/column/p_608baa19e4b071a81eb6ebbc?xxxxxx 中的p_608baa19e4b071a81eb6ebbc即是product_id |

#### 1. 下载单独视频/音频
```
python3 xiaoet.py <店铺ID> -d <ResourceID>
```
#### 2. 下载一个专栏所有视频/音频
```
python3 xiaoet.py <店铺ID> -d <ProductID>
```
#### 3. 列出一个店铺所有专栏(部分商铺可能失效)
```
python3 xiaoet.py <店铺ID> -pl
```
#### 4. 列出该专栏下所有视频/音频
```
python3 xiaoet.py <店铺ID> -rl <ProductID>
```
#### 5. 列出视频/音频所在专栏ID
```
python3 xiaoet.py <店铺ID> -r2p <ResourceID>
```
#### 5. ffmpeg合成视频
```
python3 xiaoet.py <店铺ID> -tc <ResourceID>
```

备注：
1. 执行命令后需要微信扫码登录，session时效性为4小时，更换店铺需要重新扫码登录
2. 默认下载目录为同级download目录下，下载完成后视频为分段，将自动合成；音频不需要合成。
3. 店铺ID为`appxxxx`形式, 专栏ID(ProductID)为`p_xxxx_xxx`形式,资源ID(ResourceID)分为视频与音频, 分别为`v_xxx_xxx`、`a_xxx_xxx`形式，需要特别注意的是，这些`ID`**区分大小写**，因此从`URL`中复制这些信息的时候注意大小写要保留。

## 三、类似项目

- [xiaoet](https://github.com/Yxnt/xiaoet)
- [xiaoetong-video-downloader](https://github.com/jiji262/xiaoetong-video-downloader)

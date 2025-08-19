# 小鹅通视频下载器 

# Download Xiaoet videos
> 小鹅通资源下载工具
> 本工具仅支持用户已购买课程的下载，并不存在付费课程的破解
> 本工具仅供自用和学习交流使用，请勿用于商业用途

## 代码改版，近期不要使用啦   2025-6-15

## ✨ 新版本特性

- 🏗️ **工程化架构**: 采用模块化设计，代码结构清晰
- 🛡️ **健壮性增强**: 完善的错误处理和重试机制
- 📊 **进度反馈**: 详细的下载进度和状态显示
- 🔧 **配置管理**: 灵活的配置文件管理
- 📝 **日志系统**: 完整的日志记录和管理
- 🧪 **单元测试**: 包含测试用例，保证代码质量
- 🎯 **命令行工具**: 友好的命令行界面

## 📁 项目结构

```
xiaoetong-video-downloader/
├── src/xiaoet_downloader/         # 主要源代码
│   ├── models/                    # 数据模型
│   │   ├── config.py              # 配置模型
│   │   └── video.py               # 视频模型
│   ├── api/                       # API客户端
│   │   └── client.py              # 小鹅通API客户端
│   ├── core/                      # 核心功能
│   │   ├── downloader.py          # 视频下载器
│   │   ├── transcoder.py          # 视频转码器
│   │   └── manager.py             # 下载管理器
│   ├── utils/                     # 工具类
│   │   ├── file_utils.py          # 文件工具
│   │   └── logger.py              # 日志工具
│   └── __init__.py                # 包初始化
├── tests/                         # 测试文件
├── scripts/                       # 脚本文件
├── main.py                        # 主程序入口
├── config.json.example            # 配置文件示例
├── requirements.txt               # 依赖列表
└── README.md                      # 说明文档
```

## 🚀 快速开始

### 1. 环境准备

#### 安装Python依赖

# 自动安装（推荐）
```bash
python scripts/setup.py
```

# 或手动安装
pip install -r requirements.txt
```

#### 安装ffmpeg
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows
# 从 https://ffmpeg.org/download.html 下载并安装
```

### 2. 配置设置

复制配置文件模板并填入你的信息：
```bash
cp config.json.example config.json
```

编辑 `config.json`：
```json
{
  "app_id": "你的app_id",
  "cookie": "你的cookie",
  "product_id": "你的product_id",
  "download_dir": "download"
}
```

#### 配置项说明
| 字段         | 说明              | 获取方式                                                                                                                                              |
|------------|-----------------|---------------------------------------------------------------------------------------------------------------------------------------------------|
| host       | 小鹅通web端api的host | 所见即所得，例如xet.citv.cn或h5.xiaoeknow.com                                                                                                              |
| cookie     | 小鹅通web端的Cookie  | web端登录后浏览器检查元素即可获取到Cookie                                                                                                                         |
| app_id     | 店铺唯一标识          | 课程链接url中获取，示例: 课程链接https://appisb9y2un7034.xet.citv.cn/p/course/column/p_608baa19e4b071a81eb6ebbc?xxxxxxx 中的appisb9y2un7034即是app_id               |
| product_id | 课程唯一标识          | 课程链接url中获取，示例: 课程链接https://appisb9y2un7034.xet.citv.cn/p/course/column/p_608baa19e4b071a81eb6ebbc?xxxxxx 中的p_608baa19e4b071a81eb6ebbc即是product_id |


### 3. 使用方法

#### 基本用法
```bash
# 下载整个课程
python main.py

# 下载单个视频
python main.py --single v_123456789

# 检查环境
python main.py --check

# 显示帮助
python main.py --help
```

#### 高级选项
```bash
# 使用自定义配置文件
python main.py --config my_config.json

# 忽略缓存重新下载
python main.py --no-cache

# 只下载不转码
python main.py --no-transcode

# 显示详细日志
python main.py --verbose
```

## 📋 配置说明

| 字段 | 说明 | 获取方式 |
|------|------|----------|
| app_id | 店铺唯一标识 | 课程链接URL中获取，如 `https://appisb9y2un7034.xet.citv.cn/...` 中的 `appisb9y2un7034` |
| cookie | 小鹅通web端的Cookie | 浏览器开发者工具中获取 |
| product_id | 课程唯一标识 | 课程链接URL中获取，如 `https://...xet.citv.cn/p/course/column/p_608baa19e4b071a81eb6ebbc` 中的 `p_608baa19e4b071a81eb6ebbc` |
| download_dir | 下载目录 | 可选，默认为 `download` |

## 🔧 开发指南

### 运行测试
```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试
python -m pytest tests/test_config.py
```

### 代码结构说明

- **models**: 数据模型，定义配置、视频资源等数据结构
- **api**: API客户端，处理与小鹅通服务器的通信
- **core**: 核心功能，包括下载器、转码器和管理器
- **utils**: 工具类，提供文件处理、日志等通用功能

### 扩展功能

要添加新功能，请遵循以下模式：

1. 在相应的模块中添加新类或方法
2. 更新相关的数据模型
3. 添加相应的测试用例
4. 更新文档

## 🐛 故障排除

### 常见问题

1. **ffmpeg未找到**
   ```
   解决方案: 确保ffmpeg已安装并在PATH中
   ```

2. **配置文件错误**
   ```
   解决方案: 检查config.json格式是否正确，参考config.json.example
   ```

3. **网络连接问题**
   ```
   解决方案: 检查网络连接，确保可以访问小鹅通服务器
   ```

4. **Cookie过期**
   ```
   解决方案: 重新获取Cookie并更新配置文件
   ```

### 日志查看

程序运行时会在 `logs/` 目录下生成日志文件，可以查看详细的运行信息：

```bash
# 查看今天的日志
cat logs/xiaoet_$(date +%Y%m%d).log

# 实时查看日志
tail -f logs/xiaoet_$(date +%Y%m%d).log
```

## 📄 更新日志

### v2.0.0 (2025-8-8)
- 🏗️ 完全重构，采用工程化架构
- 🛡️ 增强错误处理和重试机制
- 📊 添加详细的进度反馈
- 🔧 改进配置管理
- 📝 添加完整的日志系统
- 🧪 添加单元测试
- 🎯 提供友好的命令行界面

### v1.0.0
- 基础功能实现
- 支持视频下载和转码

## 📜 许可证

本项目仅供学习和个人使用，请勿用于商业用途。

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## ⚠️ 免责声明

本工具仅用于下载用户已购买的课程内容，请遵守相关法律法规和平台使用条款。
=======
- [xiaoet](https://github.com/Yxnt/xiaoet)
- [xiaoetong-video-downloader](https://github.com/jiji262/xiaoetong-video-downloader)

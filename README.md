# YouTube Audio Downloader (Pro)

🎵 极简、高效的 YouTube 音频批量下载器 | A minimalist, efficient batch audio downloader for YouTube

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 📸 软件截图

![GUI Screenshot](screenshot.png)

## 🚀 下载安装

### ⚡ 灵巧版 (Lite) - 推荐
体积仅 **10MB**，首次运行时会自动下载必要组件。

1. 前往 [Releases](https://github.com/dearhua26/youtube-member-audio-dl/releases) 页面
2. 下载 `YouTubeAudioDownloader-v1.0.0-Lite.zip`
3. 解压后运行 `YouTubeAudioDownloader.exe`
4. **⚠️ 注意**：首次运行会弹出 "正在配置环境" 窗口，请耐心等待组件下载完成。

---

## 🎯 功能定位

这是一个通用的 YouTube 音频下载工具，旨在提供最便捷的音频获取体验：

- ✅ **常规下载**：默认支持所有公开视频的极速音频提取。
- ✅ **进阶下载 (Cookie)**：如需下载 **会员专属**、**年龄限制** 或 **所在地区受限** 的视频，只需在设置页面配置 Cookie，即可快速解锁这些内容。
- ✅ **高清音质**：直接获取高质量 **M4A 格式**，保留原始音质且体积小巧。
- ✅ **生产力伴侣**：下载的音频可直接用于 Whisper 等 AI 转录工具生成字幕。

## ✨ 技术特性

### 下载模式
- 🎯 **单视频下载**：粘贴链接即可下载。
- 📋 **批量下载**：支持从 TXT 文件批量读取链接。

### 核心功能
- 🔐 **Cookie 支持**：支持登录账号后下载受限内容。
- 🖼️ **封面内嵌**：自动将视频封面作为音频封面。
- 🔄 **断点续传**：已下载过的文件秒速跳过。
- 🛡️ **智能诊断**：内置错误分析引擎，自动提示解决办法。
- 🖥️ **可视化 UI**：无需敲代码，窗口操作。

## 📖 使用指南

### 首次使用

1. 在浏览器安装 [Get cookies.txt LOCALLY](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc) 插件
2. 登录 YouTube 会员账号，导出 cookies
3. 在软件设置页粘贴 cookies 内容
4. 输入视频链接开始下载

## 🎤 配合字幕生成

下载的 M4A 音频可以直接用于语音转文字：

```bash
# 使用 OpenAI Whisper
whisper your_audio.m4a --language Chinese --model medium
```

## 📄 许可证

[MIT License](LICENSE)

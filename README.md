# AICoder - 智能对话助手

## 项目简介

AICoder 是一款基于 Python + Tkinter 开发的跨平台 AI 对话客户端，支持调用多种主流大语言模型（OpenAI、DeepSeek、Anthropic Claude、Google Gemini、智谱 GLM、通义千问、月之暗面 Kimi 等），并提供直观易用的图形界面。本项目旨在为用户提供一个统一、可控、可扩展的 AI 交互环境，特别适合开发者、研究人员以及对隐私和成本敏感的用户。

## 主要特性

- 🧠 多模型支持：内置超过 150 种模型的显示名称与默认端点映射，涵盖国内外主流服务商。用户只需填写 API Key 即可切换模型，无需记忆复杂 URL。
- 📊 智能用量统计：自动记录每月 Token 消耗，并在界面上方实时显示上下文窗口占用（绿色/橙色/红色预警），帮助用户控制成本与上下文长度。
- 💬 流式对话体验：采用流式 API 响应，模型生成内容逐字显示，并支持 Markdown 实时渲染（代码高亮、数学公式等），交互更流畅。
- 🧰 便捷工具集成：对话历史保存/导出（TXT/Markdown）、文件上传（自动读取内容并填入输入框）、日志查看与导出（支持清空、保存）、深色/浅色主题切换（基于 sv_ttk）。
- 🔒 本地配置管理：所有 API Key、模型偏好、月度用量均存储在项目目录下的 config.json 中，无云端依赖，保护隐私。
- 🚀 打包为单文件 exe：可使用 PyInstaller 打包为 Windows 可执行文件，无需安装 Python 环境即可运行。

## 快速开始

### 1. 环境要求（源码运行）
- Python 3.8+（若直接运行源码）
- 依赖库：requests, tkinter（内置）, sv_ttk, tkhtmlview, markdown

安装依赖命令：
pip install requests sv_ttk tkhtmlview markdown

### 2. 配置文件
首次运行会自动生成 config.json，请填写以下字段：

{
    "model": "deepseek-r1",
    "api_key": "your-api-key-here",
    "base_url": "",
    "monthly_usage": 0,
    "current_month": "2026-03",
    "dark_mode": false
}

### 3. 运行程序
双击程序即可运行。


## 使用说明

### 主界面
- 导航栏：主页、设置、清空对话、保存对话、日志、关于。
- 对话区：显示历史消息，支持 Markdown 渲染。AI 回复会显示响应时间与消耗 Token 数。
- 输入区：支持多行文本，按 Enter 直接发送，按 Shift+Enter 换行。可上传文件（TXT/PY 等）自动填充内容。

### 设置详解
- 模型搜索：在设置页面的搜索框中输入关键词（如 "claude"、"通义"），实时过滤模型列表。点击模型后按"选定模型"即可生效。
- API 地址：若模型不在自动端点列表中（如本地部署的 Llama），请手动填写完整的 chat/completions 端点 URL。
- API Key：勾选"显示密钥"可查看输入内容。
- 深色模式：切换后立即生效，并保存至配置文件。

### 日志系统
程序运行过程中的关键事件（请求开始/结束、错误、配置变更）均会记录在"日志"页面中，支持清空和导出为文本文件。日志最大保留 4000 条，防止内存溢出。

## 常见问题

### Q1: 为什么发送消息后没有反应？
- 检查 API Key 是否正确，以及账户余额是否充足。
- 检查"设置"中的 API 地址是否可访问（部分服务商需要科学上网）。
- 查看"日志"页面中的错误信息。

### Q2: 上下文窗口显示红色（剩余 token 为负）怎么办？
- 点击"清空对话"按钮，或手动删除部分历史消息。程序不会自动截断上下文，需用户主动管理。

### Q3: 某些模型（如 claude-3-opus）的默认端点是什么？
- 本程序仅提供 OpenAI 兼容接口的调用。对于 Claude 模型，您需要将 base_url 设置为代理服务（如 https://api.anthropic.com/v1/messages 不兼容 OpenAI 格式）或使用第三方网关（如 OpenRouter）。建议查阅各服务商的 API 文档后填写正确的 base_url。


## 自定义与扩展

### 添加新模型
在 all_models 列表中添加元组 ('model_id', '显示名称')，同时更新 get_model_max_tokens 和 get_default_base_url_for_model 函数中的映射即可。

### 修改 UI 样式
程序使用了 sv_ttk 主题库，您可以在 setup_styles 方法中自定义颜色。若想使用其他 ttk 主题，替换 sv_ttk.set_theme 调用即可。



## 贡献与反馈

欢迎提交 Issue 和 Pull Request！项目地址：https://github.com/Tian-Technology/AICoder

---

AICoder – 让 AI 对话更自由、更透明。

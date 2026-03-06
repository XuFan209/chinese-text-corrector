# 中文文本纠错系统

基于 Flask 和 MacBERT 模型的中文文本纠错 Web 应用。

## 功能特点

- 支持文件格式：.doc、.docx、.txt
- 智能文本纠错：标点符号、漏字、多字、同音字
- 实时纠错：上传文件后立即显示结果
- 错误高亮：清晰对比原文和纠错后文本
- 历史记录：保存纠错历史
- 大文件支持：最大支持 100MB

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动应用

- Windows: 双击运行 `启动.bat`
- 或命令行: `python start.py`

### 3. 访问应用

打开浏览器访问 `http://127.0.0.1:8080`

## 项目结构

```
chinese-text-corrector/
├── app.py              # Flask 主应用
├── start.py            # 启动脚本
├── 启动.bat            # Windows 启动
├── requirements.txt    # 依赖列表
├── README.md           # 本文件
├── templates/
│   └── index.html      # 前端页面
├── static/
│   ├── style.css      # 样式
│   └── script.js       # 脚本
└── data/
    └── history.json   # 历史记录
```

## 模型说明

本项目使用 MacBERT 模型进行中文纠错，模型文件存放位置：

- **安装目录**: `D:\ProgramData\anaconda3\macbert4csc-base-chinese`
- **模型大小**: 约 390MB

## 使用说明

1. **上传文件**: 点击上传区域或拖拽文件
2. **开始纠错**: 点击"开始纠错"按钮
3. **查看结果**: 系统显示纠错详情和对比
4. **保存结果**: 复制纠错后的文本

## 配置

### 修改端口

编辑 `start.py` 或 `app.py` 中的 `port=8080` 为其他端口。

### 修改上传大小限制

编辑 `app.py`:
```python
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB
```

## 环境要求

- Python 3.9+
- Windows 10/11
- Anaconda (推荐)

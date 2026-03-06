# MacBERT 模型说明

## 概述

本项目使用 MacBERT (Macrotome-Based BERT) 模型进行中文文本纠错。

## 模型信息

- **模型名称**: macbert4csc-base-chinese
- **模型大小**: 约 390MB
- **安装位置**: `D:\ProgramData\anaconda3\macbert4csc-base-chinese`

## 模型优势

- **深度语义理解**: 基于 BERT 架构，理解上下文语义
- **高准确率**: 中文纠错任务表现优异
- **自适应纠错**: 处理各类文本错误

## 纠错功能

- 标点符号纠错
- 漏字检测
- 多字检测
- 同音/同形字纠错
- 语法错误纠错

## 首次使用

首次运行时会自动从缓存加载模型，无需手动下载。

## 故障排除

### 模型加载失败

1. 确认模型文件存在于安装目录
2. 检查 `D:\ProgramData\anaconda3\macbert4csc-base-chinese` 目录是否存在

### 纠错速度慢

- 首次加载模型需要几秒钟
- 模型加载后会缓存在内存中，后续使用更快

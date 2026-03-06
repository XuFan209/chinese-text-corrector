#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中文文本纠错系统 - Flask后端
基于MacBERT模型的中文拼写纠错

主要功能：
1. 文本纠错 - 直接输入文本进行纠错
2. 文件纠错 - 上传Word文档进行纠错
3. 文档保存 - 保存纠错后的文档
"""

import os
import ssl
import tempfile
import datetime
import traceback

from flask import Flask, request, jsonify, render_template
from docx import Document
from pycorrector import MacBertCorrector

# 禁用SSL验证（用于下载模型）
ssl._create_default_https_context = ssl._create_unverified_context

# ============================================================================
# Flask应用配置
# ============================================================================
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 最大上传文件大小：100MB
app.config['JSON_AS_ASCII'] = False  # 支持中文JSON输出

# ============================================================================
# 日志配置
# ============================================================================
log_file = open('correction_log.txt', 'w', encoding='utf-8')

def log(message):
    """记录日志到文件"""
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_file.write(f"[{timestamp}] {message}\n")
    log_file.flush()

# ============================================================================
# MacBERT模型初始化
# ============================================================================
log("Starting application...")
log("=" * 70)
log("Loading MacBERT model...")

# 从anaconda site-packages目录加载模型
import pycorrector
site_packages = os.path.dirname(os.path.dirname(pycorrector.__file__))
local_model_path = os.path.join(site_packages, 'macbert4csc-base-chinese')
macbert_corrector = MacBertCorrector(local_model_path)
macbert_threshold = 0.5  # 置信度阈值

log("MacBERT model loaded successfully")

# ============================================================================
# 路由定义
# ============================================================================

@app.route('/')
def index():
    """主页 - 渲染纠错界面"""
    return render_template('index.html')


@app.route('/test')
def test():
    """测试接口 - 检查系统状态"""
    return jsonify({
        'status': 'ok',
        'message': 'System is running',
        'correction_method': 'MacBertCorrector'
    })


@app.route('/upload', methods=['POST'])
def upload_file():
    """
    文件上传接口
    支持格式：.docx, .doc
    返回：提取的文本内容
    """
    try:
        # 检查是否有文件
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400

        # 检查文件格式
        if not (file.filename.endswith('.docx') or file.filename.endswith('.doc')):
            return jsonify({'success': False, 'error': 'Unsupported file format'}), 400

        # 保存临时文件
        temp_path = os.path.join(tempfile.gettempdir(), file.filename)
        file.save(temp_path)

        # 提取文本
        text = extract_text_from_docx(temp_path)

        # 删除临时文件
        os.remove(temp_path)

        return jsonify({
            'success': True,
            'filename': file.filename,
            'text': text,
            'original_text': text
        })

    except Exception as e:
        log(f"File upload error: {e}")
        log(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500


def extract_text_from_docx(file_path):
    """
    从Word文档中提取文本
    支持.docx和.doc格式
    """
    if file_path.endswith('.docx'):
        # .docx格式 - 使用python-docx库
        doc = Document(file_path)
        return '\n'.join([paragraph.text for paragraph in doc.paragraphs])

    elif file_path.endswith('.doc'):
        # .doc格式 - 使用docx2txt库读取
        try:
            import docx2txt
            text = docx2txt.process(file_path)
            if text and text.strip():
                # 清理文本：移除多余的空白字符和特殊字符
                import re
                # 将多个连续空白字符替换为单个空格
                text = re.sub(r'\s+', ' ', text)
                # 移除页码符号（如 - 1 -, —1—, Page 1 等格式）
                text = re.sub(r'\s*[-—]\s*\d+\s*[-—]\s*', '', text)
                text = re.sub(r'\s*Page\s*\d+\s*of\s*\d+\s*', '', text, flags=re.IGNORECASE)
                text = re.sub(r'\s*第\s*\d+\s*页\s*', '', text)
                # 移除首尾空白
                text = text.strip()
                return text
            else:
                raise Exception("文档内容为空")
        except Exception as e:
            log(f"docx2txt failed: {e}")
            raise Exception(f"无法读取.doc文件。建议将文件转换为.docx格式后重试。错误: {e}")

    return ''


def protect_patterns(text):
    """
    保护特定模式不被纠错（如日期时间格式）
    返回保护后的文本和模式映射
    """
    import re
    patterns = []
    protected_text = text
    
    # 日期时间格式: [2026-02-12 17:20:19] 或 2026-02-12 17:20:19
    datetime_pattern = r'\[?\d{4}[-/]\d{1,2}[-/]\d{1,2}\s+\d{1,2}:\d{2}:\d{2}\]?'
    
    counter = 0
    for match in re.finditer(datetime_pattern, text):
        placeholder = f"__DATETIME_{counter}__"
        patterns.append((placeholder, match.group()))
        protected_text = protected_text.replace(match.group(), placeholder, 1)
        counter += 1
    
    return protected_text, patterns


def restore_patterns(text, patterns):
    """恢复被保护的模式"""
    for placeholder, original in patterns:
        text = text.replace(placeholder, original)
    return text


@app.route('/correct', methods=['POST'])
def correct_text():
    """
    文本纠错接口
    使用MacBERT模型进行中文拼写纠错
    """
    try:
        # 获取请求数据
        data = request.get_json()
        text = data.get('text', '')

        if not text:
            return jsonify({'success': False, 'error': 'No text provided'}), 400

        # 记录日志
        log(f"\nCorrection request received")
        log(f"Original text length: {len(text)}")
        log(f"Original text (first 100 chars): {text[:100]}")

        # 保护日期时间格式
        protected_text, patterns = protect_patterns(text)
        if patterns:
            log(f"Protected {len(patterns)} datetime patterns")

        # 使用MacBERT进行纠错
        all_errors = []
        corrected_text = protected_text

        try:
            result = macbert_corrector.correct(protected_text, threshold=macbert_threshold)
            corrected_text = result['target']

            # 处理错误列表
            for error in result['errors']:
                # 过滤掉无效的错误：wrong为空字符串的情况
                # 这种情况通常是由于Word文档中的格式问题（如换行符）导致的误识别
                if error[0] and error[0].strip():
                    all_errors.append({
                        'wrong': error[0],
                        'correct': error[1],
                        'position': error[2],
                        'type': 'MacBERT'
                    })

            log(f"MacBERT found {len(result['errors'])} errors, {len(all_errors)} valid after filtering")

        except Exception as e:
            log(f"MacBERT correction failed: {e}")
            log(traceback.format_exc())

        # 恢复被保护的日期时间格式
        if patterns:
            corrected_text = restore_patterns(corrected_text, patterns)
            log(f"Restored {len(patterns)} datetime patterns")

        # 按位置排序错误
        all_errors.sort(key=lambda x: x['position'])

        # 记录结果
        log(f"Total errors: {len(all_errors)}")
        log(f"Corrected text (first 100 chars): {corrected_text[:100]}")
        log("=" * 70)

        return jsonify({
            'success': True,
            'original_text': text,
            'corrected_text': corrected_text,
            'errors': all_errors,
            'errors_count': len(all_errors)
        })

    except Exception as e:
        log(f"Correction endpoint error: {e}")
        log(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# 启动应用
# ============================================================================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

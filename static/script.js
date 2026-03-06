/**
 * 中文文本纠错系统 - 前端JavaScript
 * 
 * 主要功能：
 * 1. 文件上传 - 支持拖拽和点击上传Word文档
 * 2. 文本纠错 - 直接输入文本进行纠错
 * 3. 结果显示 - 显示纠错结果和错误详情
 */

// ============================================================================
// DOM元素引用
// ============================================================================

// 文件上传相关元素
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const clearFile = document.getElementById('clearFile');
const actionSection = document.getElementById('actionSection');
const correctBtn = document.getElementById('correctBtn');

// 文本输入相关元素
const textInput = document.getElementById('textInput');
const correctTextBtn = document.getElementById('correctTextBtn');

// 结果显示相关元素
const resultsSection = document.getElementById('resultsSection');
const errorCount = document.getElementById('errorCount');
const errorsList = document.getElementById('errorsList');
const errorStats = document.getElementById('errorStats');
const errorsListContainer = document.getElementById('errorsListContainer');
const noErrorsMessage = document.getElementById('noErrorsMessage');

// 加载动画元素
const loading = document.getElementById('loading');
const loadingText = document.getElementById('loadingText');

// ============================================================================
// 全局状态
// ============================================================================

let currentFile = null;      // 当前上传的文件
let correctionData = null;   // 纠错结果数据

// ============================================================================
// 事件监听器绑定
// ============================================================================

// 文件上传区域点击事件
uploadArea.addEventListener('click', () => {
    fileInput.click();
});

// 文件拖拽事件
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileSelect(files[0]);
    }
});

// 文件选择事件
fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileSelect(e.target.files[0]);
    }
});

// 清除文件按钮
clearFile.addEventListener('click', () => {
    resetFileUpload();
});

// 文件纠错按钮
correctBtn.addEventListener('click', () => {
    if (currentFile) {
        performCorrection(null, true);
    }
});

// 文本纠错按钮
correctTextBtn.addEventListener('click', () => {
    const text = textInput.value.trim();
    if (text) {
        performCorrection(text, false);
    } else {
        alert('请输入需要纠错的文本');
    }
});

// ============================================================================
// 文件处理函数
// ============================================================================

/**
 * 处理文件选择
 * @param {File} file - 选择的文件
 */
function handleFileSelect(file) {
    // 支持的文件扩展名
    const validExtensions = ['.doc', '.docx', '.txt'];
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();

    // 验证文件格式
    if (!validExtensions.includes(fileExtension)) {
        alert('不支持的文件格式。请上传 .doc、.docx 或 .txt 文件');
        return;
    }

    // 保存文件并更新UI
    currentFile = file;
    fileName.textContent = file.name;
    fileInfo.style.display = 'block';
    uploadArea.style.display = 'none';
    actionSection.style.display = 'block';
    resultsSection.style.display = 'none';
}

/**
 * 重置文件上传状态
 */
function resetFileUpload() {
    currentFile = null;
    fileInput.value = '';
    fileInfo.style.display = 'none';
    uploadArea.style.display = 'block';
    actionSection.style.display = 'none';
    resultsSection.style.display = 'none';
}

/**
 * 读取文本文件内容
 * @param {File} file - 文本文件
 * @returns {Promise<string>} 文件内容
 */
function readFileContent(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();

        reader.onload = function (e) {
            resolve(e.target.result);
        };

        reader.onerror = function () {
            reject(new Error('文件读取失败'));
        };

        reader.readAsText(file, 'UTF-8');
    });
}

/**
 * 上传Word文档并提取文本
 * @param {File} file - Word文档
 * @returns {Promise<string|null>} 提取的文本内容
 */
async function uploadAndExtractText(file) {
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.success) {
            return result.text;
        } else {
            console.error('Upload failed:', result.error);
            return null;
        }
    } catch (error) {
        console.error('Upload error:', error);
        return null;
    }
}

// ============================================================================
// 纠错处理函数
// ============================================================================

/**
 * 执行纠错
 * @param {string|null} text - 要纠错的文本（null表示从文件读取）
 * @param {boolean} isFile - 是否从文件读取
 */
async function performCorrection(text, isFile) {
    showLoading('正在纠错，请稍候...');

    try {
        let textToCorrect = text;

        // 如果是文件，先读取文件内容
        if (isFile && currentFile) {
            const fileExtension = currentFile.name.split('.').pop().toLowerCase();

            if (fileExtension === 'doc' || fileExtension === 'docx') {
                showLoading('正在读取文档内容...');
                textToCorrect = await uploadAndExtractText(currentFile);
                if (!textToCorrect) {
                    alert('无法读取文档内容');
                    hideLoading();
                    return;
                }
            } else if (fileExtension === 'txt') {
                showLoading('正在读取文本文件...');
                textToCorrect = await readFileContent(currentFile);
                if (!textToCorrect) {
                    alert('无法读取文件内容');
                    hideLoading();
                    return;
                }
            }
        }

        // 调用纠错API
        showLoading('正在纠错，请稍候...');

        const response = await fetch('/correct', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text: textToCorrect,
                is_file: isFile
            })
        });

        const data = await response.json();

        if (data.success) {
            correctionData = data;
            displayResults(data);
        } else {
            alert(data.error || '纠错失败');
        }
    } catch (error) {
        alert('纠错失败: ' + error.message);
    } finally {
        hideLoading();
    }
}

// ============================================================================
// 结果显示函数
// ============================================================================

/**
 * 显示纠错结果
 * @param {Object} data - 纠错结果数据
 */
function displayResults(data) {
    // 显示结果区域
    resultsSection.style.display = 'block';
    errorCount.textContent = data.errors_count;

    // 清空错误列表
    errorsList.innerHTML = '';

    // 确保errors是数组
    const errors = Array.isArray(data.errors) ? data.errors : [];

    if (errors.length > 0) {
        // 有错误，显示错误表格
        errorStats.style.display = 'flex';
        errorsListContainer.style.display = 'block';
        noErrorsMessage.style.display = 'none';

        renderErrorTable(errors, data.original_text);
    } else {
        // 无错误，显示提示信息
        errorStats.style.display = 'none';
        errorsListContainer.style.display = 'none';
        noErrorsMessage.style.display = 'block';
    }

    // 滚动到结果区域
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

/**
 * 渲染错误表格
 * @param {Array} errors - 错误列表
 * @param {string} originalText - 原始文本
 */
function renderErrorTable(errors, originalText) {
    const table = document.createElement('table');
    table.className = 'error-table';

    // 表头
    const thead = document.createElement('thead');
    thead.innerHTML = `
        <tr>
            <th>序号</th>
            <th>错误类型</th>
            <th>原文</th>
            <th>纠正后</th>
        </tr>
    `;
    table.appendChild(thead);

    // 表体
    const tbody = document.createElement('tbody');

    errors.forEach((error, index) => {
        const row = createErrorRow(error, index, originalText);
        tbody.appendChild(row);
    });

    table.appendChild(tbody);
    errorsList.appendChild(table);
}

/**
 * 创建错误行
 * @param {Object} error - 错误信息
 * @param {number} index - 错误序号
 * @param {string} originalText - 原始文本
 * @returns {HTMLTableRowElement} 表格行元素
 */
function createErrorRow(error, index, originalText) {
    const row = document.createElement('tr');
    row.className = 'error-row';

    const errorType = error.type || '未知错误';
    const wrongText = error.wrong || '';
    const correctText = error.correct || '';
    const position = error.position || 0;

    // 获取上下文（错误位置前后30个字符）
    const contextLength = 30;
    const start = Math.max(0, position - contextLength);
    const end = Math.min(originalText.length, position + wrongText.length + contextLength);
    const context = originalText.substring(start, end);

    // 高亮显示错误文本
    let originalHtml = context;
    let correctedHtml = context;

    if (wrongText) {
        const escapedWrong = escapeRegExp(wrongText);
        originalHtml = context.replace(
            new RegExp(escapedWrong, 'g'),
            `<strong class="error-word">${wrongText}</strong>`
        );
        correctedHtml = context.replace(
            new RegExp(escapedWrong, 'g'),
            `<strong class="corrected-word">${correctText}</strong>`
        );
    }

    row.innerHTML = `
        <td class="error-number">${index + 1}</td>
        <td class="error-type">${errorType}</td>
        <td class="error-sentence">${originalHtml}</td>
        <td class="corrected-sentence">${correctedHtml}</td>
    `;

    return row;
}

// ============================================================================
// 工具函数
// ============================================================================

/**
 * 转义正则表达式特殊字符
 * @param {string} string - 要转义的字符串
 * @returns {string} 转义后的字符串
 */
function escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

/**
 * 显示加载动画
 * @param {string} text - 加载提示文字
 */
function showLoading(text) {
    loadingText.textContent = text;
    loading.style.display = 'flex';
}

/**
 * 隐藏加载动画
 */
function hideLoading() {
    loading.style.display = 'none';
}

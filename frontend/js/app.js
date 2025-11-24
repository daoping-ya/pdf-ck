/**
 * PDF处理工具 - 主应用逻辑
 */

// 全局状态
const state = {
    currentFile: null,  // 当前文件信息
    currentPage: 1,     // 当前预览页码
    totalPages: 1       // 总页数
};

// DOM元素
const elements = {
    uploadBox: document.getElementById('uploadBox'),
    fileInput: document.getElementById('fileInput'),
    uploadSection: document.getElementById('uploadSection'),
    filePanel: document.getElementById('filePanel'),
    previewSection: document.getElementById('previewSection'),
    resultSection: document.getElementById('resultSection'),
    progressModal: document.getElementById('progressModal'),
    progressText: document.getElementById('progressText'),
    toast: document.getElementById('toast'),
    statusText: document.getElementById('statusText'),
    fileName: document.getElementById('fileName'),
    fileSize: document.getElementById('fileSize'),
    filePages: document.getElementById('filePages'),
    fileStatus: document.getElementById('fileStatus'),
    previewImage: document.getElementById('previewImage'),
    currentPageInput: document.getElementById('currentPage'),
    totalPagesSpan: document.getElementById('totalPages'),
    prevPageBtn: document.getElementById('prevPage'),
    nextPageBtn: document.getElementById('nextPage'),
    resultContent: document.getElementById('resultContent'),
    settingsBtn: document.getElementById('settingsBtn')
};

// ==================== 初始化 ====================

async function init() {
    console.log('App initializing...');
    try {
        const health = await API.healthCheck();
        showToast('系统就绪', 'success');
        if (elements.statusText) {
            elements.statusText.textContent = `就绪 | ${health.memory_usage_mb}MB | ${health.disk_usage?.free_gb}GB可用`;
        }
    } catch (error) {
        console.error('Health check failed:', error);
        showToast('连接服务器失败，请确保后台已启动', 'error');
        if (elements.statusText) {
            elements.statusText.textContent = '🔴 服务器未连接';
            elements.statusText.style.color = '#ef4444';
        }
    }

    setupEventListeners();
}

// ==================== 事件监听 ====================

function setupEventListeners() {
    // 设置按钮
    if (elements.settingsBtn) {
        elements.settingsBtn.addEventListener('click', openSettings);
    } else {
        console.error('Settings button not found');
    }

    // 文件选择
    if (elements.fileInput) {
        elements.fileInput.addEventListener('change', handleFileSelect);
    }

    // 拖拽上传
    if (elements.uploadBox) {
        elements.uploadBox.addEventListener('dragover', (e) => {
            e.preventDefault();
            elements.uploadBox.classList.add('drag-over');
        });

        elements.uploadBox.addEventListener('dragleave', () => {
            elements.uploadBox.classList.remove('drag-over');
        });

        elements.uploadBox.addEventListener('drop', (e) => {
            e.preventDefault();
            elements.uploadBox.classList.remove('drag-over');

            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFileSelect({ target: { files } });
            }
        });
    }

    // 工具栏按钮
    document.querySelectorAll('.tool-btn').forEach(btn => {
        btn.addEventListener('click', handleToolAction);
    });

    // 预览翻页
    if (elements.prevPageBtn) elements.prevPageBtn.addEventListener('click', () => changePage(-1));
    if (elements.nextPageBtn) elements.nextPageBtn.addEventListener('click', () => changePage(1));
    if (elements.currentPageInput) {
        elements.currentPageInput.addEventListener('change', (e) => {
            const page = parseInt(e.target.value);
            if (page >= 1 && page <= state.totalPages) {
                state.currentPage = page;
                loadPreview();
            }
        });
    }
}

// ==================== 文件处理 ====================

async function handleFileSelect(event) {
    const file = event.target.files[0];

    if (!file) return;

    if (!file.name.toLowerCase().endsWith('.pdf')) {
        showToast('请选择PDF文件', 'error');
        return;
    }

    if (file.size > 20 * 1024 * 1024) {
        showToast('文件大小超过20MB限制', 'error');
        return;
    }

    showProgress('上传中...');

    try {
        const result = await API.uploadFile(file);

        state.currentFile = result;
        state.totalPages = result.pages;
        state.currentPage = 1;

        hideProgress();
        showFilePanel(result);
        showToast('上传成功', 'success');

    } catch (error) {
        hideProgress();
        showToast(error.message, 'error');
    }
}

function showFilePanel(fileInfo) {
    // 更新文件信息
    elements.fileName.textContent = fileInfo.filename;
    elements.fileSize.textContent = `${(fileInfo.size / 1024 / 1024).toFixed(2)} MB`;
    elements.filePages.textContent = `${fileInfo.pages} 页`;
    elements.fileStatus.textContent = fileInfo.is_encrypted ? '🔒 已加密' : '🔓 未加密';

    // 显示面板
    elements.uploadSection.style.display = 'none';
    elements.filePanel.style.display = 'block';
    elements.previewSection.style.display = 'block';

    // 加载预览
    loadPreview();
}

function loadPreview() {
    if (!state.currentFile) return;

    const previewUrl = API.getPreviewUrl(state.currentFile.file_id, state.currentPage);
    elements.previewImage.src = previewUrl;
    elements.currentPageInput.value = state.currentPage;
    elements.totalPagesSpan.textContent = state.totalPages;
}

function changePage(delta) {
    const newPage = state.currentPage + delta;
    if (newPage >= 1 && newPage <= state.totalPages) {
        state.currentPage = newPage;
        loadPreview();
    }
}

// ==================== 工具操作 ====================

async function handleToolAction(event) {
    const action = event.currentTarget.dataset.action;

    if (!state.currentFile && action !== 'reset') {
        showToast('请先上传PDF文件', 'error');
        return;
    }

    switch (action) {
        case 'convert-to-word':
            await convertToWord();
            break;
        case 'extract-text':
            await extractText();
            break;
        case 'extract-text-enhanced':
            await extractTextEnhanced();
            break;
        case 'extract-tables':
            await extractTables();
            break;
        case 'extract-images':
            await extractImages();
            break;
        case 'rotate':
            await rotatePage();
            break;
        case 'encrypt':
            await encryptPDF();
            break;
        case 'decrypt':
            await decryptPDF();
            break;
        case 'reset':
            resetApp();
            break;
    }
}
// 导出相关函数
async function convertToWord() {
    const exportModal = document.getElementById('exportModal');
    const confirmExportPathInput = document.getElementById('confirmExportPath');

    // 1. 获取当前保存的设置路径
    try {
        const response = await fetch(`${window.location.origin}/api/settings`);
        const settings = await response.json();
        if (confirmExportPathInput) {
            confirmExportPathInput.value = settings.export_path || '';
        }
    } catch (e) {
        console.error('获取设置失败', e);
    }

    // 2. 显示导出向导
    if (exportModal) {
        exportModal.style.display = 'flex';
    } else {
        console.error('未找到导出模态框');
        showToast('无法打开导出向导', 'error');
    }
}

function closeExportModal() {
    const exportModal = document.getElementById('exportModal');
    if (exportModal) {
        exportModal.style.display = 'none';
    }
}

async function confirmExport() {
    closeExportModal();

    const confirmExportPathInput = document.getElementById('confirmExportPath');
    const exportPath = confirmExportPathInput ? confirmExportPathInput.value.trim() : '';

    showProgress('正在转换为Word文档...');
    console.log('开始转换为Word...');

    try {
        // 如果用户输入了新路径，先更新设置
        if (exportPath) {
            try {
                await fetch(`${window.location.origin}/api/settings`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ export_path: exportPath })
                });
            } catch (e) {
                console.warn('更新默认路径失败', e);
            }
        }

        const apiUrl = `${window.location.origin}/api/convert-to-word`;
        console.log('请求URL:', apiUrl);

        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                file_id: state.currentFile.file_id,
                pages: [],
                export_path: exportPath
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || '转换请求失败');
        }

        const data = await response.json();
        console.log('转换任务提交成功, Task ID:', data.task_id);

        // 轮询任务状态
        const result = await API.pollTaskStatus(data.task_id, (status) => {
            showProgress(`转换中... ${status.progress}%`, status.progress);
        });

        hideProgress();
        console.log('转换完成, 结果:', result);

        if (!result) {
            throw new Error('转换失败：无结果返回');
        }

        // 情况1: 保存到本地 (如果指定了路径)
        if (result.saved_to_local) {
            showToast('转换成功! 已保存到指定文件夹', 'success');
            showResult('Word导出成功', `
                <div style="text-align: center; padding: 20px;">
                    <p style="font-size: 18px; margin: 20px 0;">
                        <strong style="color: #10b981;">✅ PDF已成功转换为Word!</strong>
                    </p>
                    <p style="margin: 15px 0; color: #666;">
                        文件已保存至: <strong>${result.saved_path}</strong>
                    </p>
                    <div style="margin: 30px 0; padding: 15px; background: var(--bg-tertiary); border-radius: 8px;">
                        📂 请在文件资源管理器中查看
                    </div>
                    <button class="btn btn-primary" onclick="convertToWord()">再次导出</button>
                </div>
            `);
            return;
        }

        // 情况2: 提供下载链接 (如果路径为空)
        if (!result.output_file_id) {
            throw new Error('转换失败：未获取到输出文件');
        }

        showToast('转换成功!正在下载...', 'success');

        // 构建下载URL
        const downloadUrl = `${window.location.origin}/api/download/${result.output_file_id}?folder=processed`;
        console.log('下载URL:', downloadUrl);

        // 方式1: 使用隐藏的a标签触发下载
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = state.currentFile.filename.replace('.pdf', '.docx');
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        // 显示结果
        showResult('Word导出成功', `
            <div style="text-align: center; padding: 20px;">
                <p style="font-size: 18px; margin: 20px 0;">
                    <strong style="color: #10b981;">✅ PDF已成功转换为Word!</strong>
                </p>
                <p style="margin: 15px 0; color: #666;">
                    文件保留了原始格式、表格和图片
                </p>
                <div style="margin: 30px 0;">
                    <a href="${downloadUrl}" 
                       download="${state.currentFile.filename.replace('.pdf', '.docx')}"
                       class="btn btn-primary" 
                       style="display: inline-block; padding: 15px 30px; background: linear-gradient(135deg, #10b981, #059669); color: white; text-decoration: none; border-radius: 8px; font-size: 16px;">
                        📥 点击再次下载
                    </a>
                </div>
            </div>
        `);

    } catch (error) {
        hideProgress();
        showToast('转换失败: ' + error.message, 'error');
        console.error('转换错误:', error);
    }
}

async function extractText() {
    showProgress('提取文字中...');

    try {
        const response = await API.extractText(state.currentFile.file_id);
        const result = await API.pollTaskStatus(response.task_id, (status) => {
            showProgress(`提取中... ${status.progress}%`, status.progress);
        });

        hideProgress();
        // 格式化显示文本
        const textContent = typeof result.text === 'string' ? result.text : JSON.stringify(result.text, null, 2);
        showResult('提取的文字', `<div style="font-family: monospace; white-space: pre-wrap;">${textContent}</div>`);
        showToast(`成功提取${result.extracted_pages}页文字`, 'success');

    } catch (error) {
        hideProgress();
        showToast(error.message, 'error');
    }
}

async function extractTextEnhanced() {
    showProgress('智能提取中(保留排版)...');
    console.log('开始智能提取...');

    try {
        const apiUrl = `${window.location.origin}/api/extract-text-enhanced`;
        console.log('请求URL:', apiUrl);

        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ file_id: state.currentFile.file_id, pages: [] })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || '请求失败');
        }

        const data = await response.json();
        console.log('任务已提交, Task ID:', data.task_id);

        const result = await API.pollTaskStatus(data.task_id, (status) => {
            console.log('任务进度:', status.progress);
            showProgress(`提取中... ${status.progress}%`, status.progress);
        });

        hideProgress();

        // 显示HTML结果
        showResult('提取结果(保留排版)', result.html);
        showToast(`成功提取${result.extracted_pages}页内容`, 'success');

    } catch (error) {
        hideProgress();
        console.error('智能提取失败:', error);
        showToast('提取失败: ' + error.message, 'error');
    }
}

async function extractTables() {
    showProgress('提取表格中...');

    try {
        const response = await fetch(`${API.API_BASE || window.location.origin + '/api'}/extract-tables`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ file_id: state.currentFile.file_id, pages: [] })
        });

        const data = await response.json();
        const result = await API.pollTaskStatus(data.task_id, (status) => {
            showProgress(`提取表格中... ${status.progress}%`, status.progress);
        });

        hideProgress();

        // 生成表格HTML
        let html = `<div style="padding: 20px;"><h3>共提取 ${result.total_tables} 个表格:</h3>`;

        for (const [pageNum, tables] of Object.entries(result.tables)) {
            if (tables.length > 0) {
                html += `<h4 style="margin-top: 20px; border-bottom: 1px solid #eee; padding-bottom: 10px;">第 ${pageNum} 页</h4>`;
                tables.forEach((table, idx) => {
                    html += `<div class="table-container" style="margin-bottom: 30px; overflow-x: auto;">`;
                    html += `<p style="font-size: 12px; color: #666; margin-bottom: 5px;">表格 ${idx + 1} (${table.row_count}行 x ${table.col_count}列)</p>`;
                    html += '<table class="pdf-table" style="width: 100%; border-collapse: collapse; border: 1px solid #ddd;">';

                    // 直接渲染二维数组
                    html += '<tbody>';
                    if (table.data && Array.isArray(table.data)) {
                        table.data.forEach((row, rowIndex) => {
                            html += '<tr>';
                            row.forEach((cell, colIndex) => {
                                // 第一行通常加粗显示，模拟表头
                                const style = rowIndex === 0 ?
                                    'border: 1px solid #ddd; padding: 8px; font-weight: bold; background-color: #f8f9fa;' :
                                    'border: 1px solid #ddd; padding: 8px;';

                                // 处理null或undefined
                                const cellContent = cell === null || cell === undefined ? '' : cell;
                                html += `<td style="${style}">${cellContent}</td>`;
                            });
                            html += '</tr>';
                        });
                    }
                    html += '</tbody></table></div>';
                });
            }
        }
        html += '</div>';

        showResult('提取的表格', html);
        showToast(`成功提取${result.total_tables}个表格`, 'success');

    } catch (error) {
        hideProgress();
        showToast(error.message, 'error');
    }
}

// 图片提取相关函数
function extractImages() {
    const modal = document.getElementById('imageExportModal');
    const pathInput = document.getElementById('imageExportPath');

    // 预填默认路径
    if (state.settings && state.settings.exportPath) {
        pathInput.value = state.settings.exportPath;
    }

    if (modal) {
        modal.style.display = 'flex';
    } else {
        console.error('未找到图片导出模态框');
        // 如果模态框不存在，直接执行提取（回退机制）
        directExtractImages();
    }
}

function closeImageExportModal() {
    const modal = document.getElementById('imageExportModal');
    if (modal) modal.style.display = 'none';
}

async function confirmImageExport() {
    const pathInput = document.getElementById('imageExportPath');
    const exportPath = pathInput ? pathInput.value.trim() : '';

    closeImageExportModal();
    showProgress('提取图片中...');

    try {
        const response = await API.extractImages(state.currentFile.file_id, [], exportPath);
        const result = await API.pollTaskStatus(response.task_id, (status) => {
            showProgress(`提取图片中... ${status.progress}%`, status.progress);
        });

        hideProgress();

        // 生成图片结果HTML
        let html = `<div style="padding: 20px;">`;
        html += `<h3>共提取 ${result.total_images} 张图片</h3>`;

        if (result.saved_to_custom_path) {
            html += `<div class="alert success" style="margin-bottom: 20px; padding: 10px; background: #d1fae5; color: #065f46; border-radius: 6px;">
                ✅ 图片已保存至: <strong>${result.export_path}</strong>
            </div>`;
        }

        if (result.images && result.images.length > 0) {
            html += `<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 20px;">`;
            result.images.forEach(img => {
                html += `
                <div style="border: 1px solid #eee; border-radius: 8px; padding: 10px; text-align: center; background: #f9fafb;">
                    <div style="height: 120px; display: flex; align-items: center; justify-content: center; background: #e5e7eb; border-radius: 4px; margin-bottom: 10px; overflow: hidden;">
                        ${img.thumbnail
                        ? `<img src="/api/images/${img.thumbnail}" style="max-width: 100%; max-height: 100%; object-fit: contain;" alt="${img.filename}">`
                        : `<span style="color: #6b7280;">${img.format.toUpperCase()}</span>`
                    }
                    </div>
                    <p style="font-size: 12px; color: #374151; margin-bottom: 5px; word-break: break-all; height: 32px; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;">${img.filename}</p>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 8px;">
                        <span style="font-size: 11px; color: #9ca3af;">P${img.page} | ${(img.size / 1024).toFixed(1)} KB</span>
                        <a href="/api/download-image?path=${encodeURIComponent(img.path)}" 
                           class="icon-btn" 
                           style="padding: 4px; width: 24px; height: 24px;" 
                           title="下载此图片"
                           download>
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width: 14px; height: 14px;">
                                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                                <polyline points="7 10 12 15 17 10"></polyline>
                                <line x1="12" y1="15" x2="12" y2="3"></line>
                            </svg>
                        </a>
                    </div>
                </div>`;
            });
            html += `</div>`;
        } else {
            html += `<p style="color: #666;">未找到图片</p>`;
        }
        html += '</div>';

        showResult('提取的图片', html);
        showToast(`成功提取${result.total_images}张图片`, 'success');

    } catch (error) {
        hideProgress();
        console.error('图片提取失败:', error);
        showToast('提取失败: ' + error.message, 'error');
    }
}

// 备用：直接提取（不带路径）
async function directExtractImages() {
    showProgress('提取图片中...');
    try {
        const response = await API.extractImages(state.currentFile.file_id);
        const result = await API.pollTaskStatus(response.task_id, (status) => {
            showProgress(`提取图片中... ${status.progress}%`, status.progress);
        });
        hideProgress();
        // ... 简化的结果显示 ...
        showToast(`成功提取${result.total_images}张图片`, 'success');
    } catch (error) {
        hideProgress();
        showToast(error.message, 'error');
    }
}

async function rotatePage() {
    const angle = prompt('旋转角度 (90, 180, 270):', '90');
    if (!angle) return;

    const rotations = { [state.currentPage]: parseInt(angle) };

    showProgress('旋转页面中...');

    try {
        const response = await API.rotatePages(state.currentFile.file_id, rotations);
        const result = await API.pollTaskStatus(response.task_id, (status) => {
            showProgress(`旋转页面中... ${status.progress}%`, status.progress);
        });

        hideProgress();
        showToast('旋转成功', 'success');

        // 提供下载链接
        const downloadUrl = API.getDownloadUrl(result.output_file_id);
        showResult('处理结果', `<p>已旋转${result.rotated_pages}页</p><a href="${downloadUrl}" class="btn btn-primary" download>下载结果</a>`);

    } catch (error) {
        hideProgress();
        showToast(error.message, 'error');
    }
}

async function encryptPDF() {
    const password = prompt('请输入密码:');
    if (!password) return;

    showProgress('加密中...');

    try {
        const response = await API.encryptPDF(state.currentFile.file_id, password);
        const result = await API.pollTaskStatus(response.task_id, (status) => {
            showProgress(`加密中... ${status.progress}%`, status.progress);
        });

        hideProgress();
        showToast('加密成功', 'success');

        const downloadUrl = API.getDownloadUrl(result.output_file_id);
        showResult('加密完成', `<a href="${downloadUrl}" class="btn btn-primary" download>下载加密PDF</a>`);

    } catch (error) {
        hideProgress();
        showToast(error.message, 'error');
    }
}

async function decryptPDF() {
    const password = prompt('请输入密码:');
    if (!password) return;

    showProgress('解密中...');

    try {
        const response = await API.decryptPDF(state.currentFile.file_id, password);
        const result = await API.pollTaskStatus(response.task_id, (status) => {
            showProgress(`解密中... ${status.progress}%`, status.progress);
        });

        hideProgress();
        showToast('解密成功', 'success');

        const downloadUrl = API.getDownloadUrl(result.output_file_id);
        showResult('解密完成', `<a href="${downloadUrl}" class="btn btn-primary" download>下载解密PDF</a>`);

    } catch (error) {
        hideProgress();
        showToast(error.message, 'error');
    }
}

// ==================== UI工具函数 ====================

function showProgress(text, progress = 0) {
    elements.progressText.textContent = text;
    elements.progressModal.style.display = 'flex';

    const progressFill = document.getElementById('progressFill');
    if (progressFill) {
        progressFill.style.width = `${progress}%`;
    }
}

function hideProgress() {
    elements.progressModal.style.display = 'none';
}

function showToast(message, type = 'info') {
    elements.toast.textContent = message;
    elements.toast.className = `toast show ${type}`;

    setTimeout(() => {
        elements.toast.classList.remove('show');
    }, 3000);
}

function showResult(title, content) {
    elements.resultSection.style.display = 'block';
    elements.resultContent.innerHTML = content;
    elements.resultSection.scrollIntoView({ behavior: 'smooth' });
}

function resetApp() {
    state.currentFile = null;
    state.currentPage = 1;
    state.totalPages = 0;

    elements.fileInput.value = '';
    elements.uploadSection.style.display = 'flex';
    elements.filePanel.style.display = 'none';
    elements.previewSection.style.display = 'none';
    elements.resultSection.style.display = 'none';
    elements.previewImage.src = '';
    elements.resultContent.innerHTML = '';
}

// ==================== 设置相关 ====================

// 移除全局变量引用，改为在函数内获取
// const settingsModal = document.getElementById('settingsModal');
// ...

async function openSettings() {
    const settingsModal = document.getElementById('settingsModal');
    const enableLayoutCheckbox = document.getElementById('enableLayout');
    const enableOCRCheckbox = document.getElementById('enableOCR');
    const exportPathInput = document.getElementById('exportPath');

    // 密码验证
    const password = prompt('请输入管理员密码以访问设置:');
    if (password !== '##12345678') {
        showToast('密码错误', 'error');
        return;
    }

    try {
        // 获取当前设置
        const response = await fetch(`${window.location.origin}/api/settings`);
        const settings = await response.json();

        if (enableLayoutCheckbox) enableLayoutCheckbox.checked = settings.enable_layout_preservation;
        if (enableOCRCheckbox) enableOCRCheckbox.checked = settings.enable_ocr;
        if (exportPathInput) exportPathInput.value = settings.export_path || '';

        if (settingsModal) settingsModal.style.display = 'flex';
    } catch (error) {
        showToast('无法加载设置', 'error');
    }
}

function closeSettings() {
    const settingsModal = document.getElementById('settingsModal');
    if (settingsModal) settingsModal.style.display = 'none';
}

async function saveSettings() {
    const enableLayoutCheckbox = document.getElementById('enableLayout');
    const enableOCRCheckbox = document.getElementById('enableOCR');
    const exportPathInput = document.getElementById('exportPath');

    const newSettings = {
        enable_layout_preservation: enableLayoutCheckbox ? enableLayoutCheckbox.checked : false,
        enable_ocr: enableOCRCheckbox ? enableOCRCheckbox.checked : false,
        export_path: exportPathInput ? exportPathInput.value.trim() : ''
    };

    try {
        const response = await fetch(`${window.location.origin}/api/settings`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(newSettings)
        });

        if (response.ok) {
            showToast('设置已保存', 'success');
            closeSettings();
        } else {
            throw new Error('保存失败');
        }
    } catch (error) {
        showToast('保存设置失败', 'error');
    }
}

// 点击模态框外部关闭
window.onclick = function (event) {
    const settingsModal = document.getElementById('settingsModal');
    const exportModal = document.getElementById('exportModal');

    if (event.target == settingsModal) {
        closeSettings();
    }
    if (event.target == exportModal) {
        closeExportModal();
    }
}

// ==================== 启动应用 ====================

document.addEventListener('DOMContentLoaded', init);

// 文本提取结果下载补丁
// 将此代码添加到 frontend/js/app.js 文件末尾

// 全局变量存储提取的文本
window.extractedTextData = {
    simple: '',
    enhanced: ''
};

// 下载文本为TXT文件
function downloadExtractedText(content, filename) {
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// 复制文本到剪贴板
function copyExtractedText(content) {
    navigator.clipboard.writeText(content).then(() => {
        alert('✅ 文本已复制到剪贴板！');
    }).catch(() => {
        // 降级方案：使用传统方法
        const textarea = document.createElement('textarea');
        textarea.value = content;
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);
        textarea.select();
        try {
            document.execCommand('copy');
            alert('✅ 文本已复制到剪贴板！');
        } catch (err) {
            alert('❌ 复制失败，请手动选择文本复制');
        }
        document.body.removeChild(textarea);
    });
}

// 格式化并显示带下载按钮的文本结果
function showTextResultWithDownload(text, isEnhanced = false) {
    // 存储文本
    if (isEnhanced) {
        window.extractedTextData.enhanced = text;
    } else {
        window.extractedTextData.simple = text;
    }

    const filename = `${state.currentFile?.filename || 'extracted'}_${isEnhanced ? '增强' : '基础'}提取.txt`;

    // 创建下载和复制按钮
    const buttons = `
        <div style="margin-bottom: 15px; display: flex; gap: 10px; flex-wrap: wrap;">
            <button onclick="downloadExtractedText(window.extractedTextData.${isEnhanced ? 'enhanced' : 'simple'}, '${filename}')" 
                    style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                           color: white; border: none; padding: 10px 20px; 
                           border-radius: 8px; cursor: pointer; font-size: 14px;
                           box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
                           transition: all 0.3s;">
                📥 下载为TXT文件
            </button>
            <button onclick="copyExtractedText(window.extractedTextData.${isEnhanced ? 'enhanced' : 'simple'})" 
                    style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); 
                           color: white; border: none; padding: 10px 20px; 
                           border-radius: 8px; cursor: pointer; font-size: 14px;
                           box-shadow: 0 4px 12px rgba(17, 153, 142, 0.3);
                           transition: all 0.3s;">
                📋 复制文本
            </button>
        </div>
    `;

    // 格式化文本显示
    const formattedText = text
        .split('\n')
        .map(line => line.trim())
        .join('\n');

    // 显示结果
    const resultHtml = `
        ${buttons}
        <div style="background: #1a1f2e; 
                    border-radius: 12px; 
                    padding: 20px; 
                    max-height: 600px; 
                    overflow-y: auto;
                    border: 1px solid rgba(255,255,255,0.1);">
            <pre style="color: #e0e0e0; 
                        white-space: pre-wrap; 
                        word-wrap: break-word; 
                        font-family: 'Consolas', 'Monaco', 'Courier New', monospace; 
                        font-size: 13px; 
                        line-height: 1.8;
                        margin: 0;
                        tab-size: 4;">${escapeHtml(formattedText)}</pre>
        </div>
        ${isEnhanced ? `
        <div style="margin-top: 15px; 
                    padding: 12px; 
                    background: rgba(255, 193, 7, 0.1); 
                    border-left: 3px solid #ffc107; 
                    border-radius: 4px; 
                    color: #ffc107;">
            💡 提示：如果表格显示仍不理想，建议使用 "📄 导出Word" 功能获得最佳效果
        </div>
        ` : ''}
    `;

    showResult(resultHtml);
}

// HTML转义函数（如果不存在）
if (typeof escapeHtml === 'undefined') {
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

console.log('✅ 文本提取下载功能已加载');

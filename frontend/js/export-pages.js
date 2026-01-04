// DPI选择对话框（添加到 index.html 的 modal 部分）
const dpiSelectModalHTML = `
<div id="dpiSelectModal" class="modal" style="display: none;">
    <div class="modal-content">
        <div class="modal-header">
            <h3>选择图片质量</h3>
            <button class="close-btn" onclick="closeDpiSelectModal()">&times;</button>
        </div>
        <div class="modal-body">
            <div class="form-group">
                <label>DPI设置：</label>
                <select id="dpiSelect" class="form-control">
                    <option value="150">150 DPI - 屏幕查看</option>
                    <option value="300" selected>300 DPI - 印刷质量（推荐）</option>
                    <option value="600">600 DPI - 超高质量</option>
                </select>
                <small style="color: #999; margin-top: 5px; display: block;">
                    💡 DPI越高，图片越清晰，文件也越大
                </small>
            </div>
            <div class="form-group">
                <label>图片格式：</label>
                <select id="imageFormatSelect" class="form-control">
                    <option value="png" selected>PNG（无损，推荐）</option>
                    <option value="jpeg">JPEG（高质量）</option>
                </select>
            </div>
        </div>
        <div class="modal-footer">
            <button class="btn btn-danger" onclick="closeDpiSelectModal()">取消</button>
            <button class="btn btn-primary" onclick="confirmExportPagesAsImages()">开始导出</button>
        </div>
    </div>
</div>
`;

// 在页面加载时插入对话框
document.addEventListener('DOMContentLoaded', () => {
    document.body.insertAdjacentHTML('beforeend', dpiSelectModalHTML);
});

// 打开DPI选择对话框
function exportPagesAsImages() {
    const modal = document.getElementById('dpiSelectModal');
    if (modal) {
        modal.style.display = 'flex';
    }
}

// 关闭DPI选择对话框
function closeDpiSelectModal() {
    const modal = document.getElementById('dpiSelectModal');
    if (modal) modal.style.display = 'none';
}

// 确认导出
async function confirmExportPagesAsImages() {
    const dpi = parseInt(document.getElementById('dpiSelect').value);
    const format = document.getElementById('imageFormatSelect').value;

    closeDpiSelectModal();

    if (!state.currentFile) {
        showToast('请先上传PDF文件', 'error');
        return;
    }

    showProgress(`导出中 (${dpi} DPI)...`);

    try {
        const response = await API.exportPagesAsImages(state.currentFile.file_id, [], dpi, format);
        const result = await API.pollTaskStatus(response.task_id, (status) => {
            showProgress(`导出中... ${status.progress}%`, status.progress);
        });

        hideProgress();

        // 显示结果
        let html = `<div style="padding: 20px;">`;
        html += `<h3>成功导出 ${result.total_images} 张高清图片</h3>`;
        html += `<p style="color: #10b981; margin: 10px 0;">✅ DPI: ${dpi} | 格式: ${format.toUpperCase()}</p>`;

        if (result.images && result.images.length > 0) {
            html += `<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 20px; margin-top: 20px;">`;
            result.images.forEach(img => {
                const imgSrc = `/api/images/${img.filename}`;
                html += `
                <div style="border: 1px solid #eee; border-radius: 8px; padding: 15px; background: #f9fafb;">
                    <div style="height: 150px; display: flex; align-items: center; justify-content: center; background: #e5e7eb; border-radius: 4px; margin-bottom: 10px; overflow: hidden;">
                        <img src="${imgSrc}" style="max-width: 100%; max-height: 100%; object-fit: contain; cursor: pointer;" 
                             alt="${img.filename}" 
                             onclick="window.open('${imgSrc}', '_blank')"
                             title="点击查看原图">
                    </div>
                    <p style="font-size: 12px; margin: 5px 0;"><strong>页码:</strong> ${img.page}</p>
                    <p style="font-size: 12px; margin: 5px 0;"><strong>分辨率:</strong> ${img.width}×${img.height}</p>
                    <p style="font-size: 12px; margin: 5px 0;"><strong>大小:</strong> ${(img.size / 1024).toFixed(2)} KB</p>
                    <a href="/api/download-image?path=${encodeURIComponent(img.path)}" download style="display: inline-block; margin-top: 8px; padding: 6px 12px; background: #667eea; color: white; text-decoration: none; border-radius: 4px; font-size: 12px;">
                        💾 下载
                    </a>
                </div>`;
            });
            html += `</div>`;
        }

        html += `</div>`;
        showResult('导出的高清图片', html);
        showToast(`成功导出${result.total_images}张${dpi} DPI图片！`, 'success');

    } catch (error) {
        hideProgress();
        showToast(error.message, 'error');
    }
}

console.log('✅ 页面导出为图片功能已加载');

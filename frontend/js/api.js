/**
 * API接口封装
 */

// 获取API基础URL
const API_BASE = window.location.protocol + '//' + window.location.hostname +
    (window.location.port !== '80' && window.location.port !== '' ? ':' + window.location.port : '') + '/api';

class API {
    /**
     * 通用请求方法
     */
    static async request(url, options = {}) {
        try {
            const response = await fetch(API_BASE + url, {
                ...options,
                headers: {
                    ...options.headers
                }
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || `HTTP ${response.status}`);
            }

            // 如果是文件下载
            if (options.download) {
                return response.blob();
            }

            return await response.json();
        } catch (error) {
            throw error;
        }
    }

    /**
     * 健康检查
     */
    static async healthCheck() {
        return await this.request('/health');
    }

    /**
     * 上传PDF文件
     */
    static async uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(API_BASE + '/upload', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || '上传失败');
        }

        return await response.json();
    }

    /**
     * 获取PDF页面预览
     */
    static getPreviewUrl(fileId, page = 1) {
        return `${API_BASE}/preview/${fileId}?page=${page}`;
    }

    /**
     * 提取文字
     */
    static async extractText(fileId, pages = []) {
        return await this.request('/extract-text', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ file_id: fileId, pages })
        });
    }

    /**
     * 提取图片
     */
    static async extractImages(fileId, pages = [], exportPath = null) {
        return await this.request('/extract-images', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                file_id: fileId,
                pages,
                export_path: exportPath
            })
        });
    }

    /**
     * 旋转页面
     */
    static async rotatePages(fileId, rotations) {
        return await this.request('/rotate-pages', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ file_id: fileId, rotations })
        });
    }

    /**
     * 加密PDF
     */
    static async encryptPDF(fileId, userPassword, ownerPassword = null) {
        return await this.request('/encrypt', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                file_id: fileId,
                user_password: userPassword,
                owner_password: ownerPassword
            })
        });
    }

    /**
     * 解密PDF
     */
    static async decryptPDF(fileId, password) {
        return await this.request('/decrypt', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ file_id: fileId, password })
        });
    }

    /**
     * 查询任务状态
     */
    static async getTaskStatus(taskId) {
        return await this.request(`/task-status/${taskId}`);
    }

    /**
     * 下载文件
     */
    static getDownloadUrl(fileId, folder = 'processed') {
        return `${API_BASE}/download/${fileId}?folder=${folder}&delete_after=true`;
    }

    /**
     * 轮询任务状态直到完成
     */
    static async pollTaskStatus(taskId, onProgress = null) {
        return new Promise((resolve, reject) => {
            const interval = setInterval(async () => {
                try {
                    const status = await this.getTaskStatus(taskId);

                    if (onProgress) {
                        onProgress(status);
                    }

                    if (status.status === 'COMPLETED') {
                        clearInterval(interval);
                        resolve(status.result);
                    } else if (status.status === 'FAILED') {
                        clearInterval(interval);
                        reject(new Error(status.error || '任务失败'));
                    }
                } catch (error) {
                    clearInterval(interval);
                    reject(error);
                }
            }, 300); // 每300ms轮询一次
        });
    }
}

"""PDF在线处理工具 - Flask主应用"""
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
import os

from config import Config
from task_manager import task_manager
from services.pdf_service import PDFService
from tasks import pdf_tasks
from utils.file_handler import (
    allowed_file, validate_pdf, save_upload_file,
    get_file_path, delete_file, cleanup_old_files, get_disk_usage
)

# 初始化Flask应用
app = Flask(__name__, static_folder='../frontend', static_url_path='')
app.config.from_object(Config)
CORS(app, resources={r"/api/*": {"origins": Config.CORS_ORIGINS}})

# 初始化目录
Config.init_app()

# ==================== 根路径和静态文件 ====================

@app.route('/')
def index():
    """首页"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """静态文件服务"""
    file_path = os.path.join(app.static_folder, path)
    if os.path.exists(file_path):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

# ==================== 健康检查 ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    import psutil
    process = psutil.Process()
    
    return jsonify({
        'status': 'ok',
        'port': Config.PORT,
        'memory_usage_mb': round(process.memory_info().rss / 1024 / 1024, 2),
        'disk_usage': get_disk_usage(),
        'config': {
            'max_workers': Config.MAX_WORKERS,
            'max_file_size_mb': Config.MAX_CONTENT_LENGTH / 1024 / 1024,
            'ocr_enabled': Config.ENABLE_OCR
        }
    })

# ==================== 文件上传 ====================

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """上传PDF文件"""
    if 'file' not in request.files:
        return jsonify({'error': '未找到文件'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': '文件名为空'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': '仅支持PDF文件'}), 400
    
    # 验证PDF
    if not validate_pdf(file.stream):
        return jsonify({'error': '无效的PDF文件'}), 422
    
    try:
        # 保存文件
        file_info = save_upload_file(file)
        file_id = file_info['file_id']
        
        # 获取PDF元数据
        metadata = PDFService.get_metadata(file_id)
        file_info.update(metadata)
        
        return jsonify({
            'status': 'success',
            'file_id': file_id,
            'filename': file_info['original_filename'],
            'size': file_info['file_size'],
            'pages': metadata['page_count'],
            'is_encrypted': metadata['is_encrypted']
        })
    except Exception as e:
        return jsonify({'error': f'上传失败: {str(e)}'}), 500

# ==================== 文件预览 ====================

@app.route('/api/preview/<file_id>', methods=['GET'])
def preview_page(file_id):
    """预览PDF页面"""
    page_num = request.args.get('page', 1, type=int)
    dpi = request.args.get('dpi', Config.PREVIEW_DPI, type=int)
    
    try:
        img_bytes = PDFService.render_page_preview(file_id, page_num, dpi)
        
        from io import BytesIO
        return send_file(
            BytesIO(img_bytes),
            mimetype='image/png',
            as_attachment=False
        )
    except FileNotFoundError:
        return jsonify({'error': '文件不存在'}), 404
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'预览失败: {str(e)}'}), 500

# ==================== 文字提取 ====================

@app.route('/api/extract-text', methods=['POST'])
def extract_text():
    """提取PDF文字(基础版)"""
    data = request.json
    file_id = data.get('file_id')
    pages = data.get('pages', [])
    
    if not file_id:
        return jsonify({'error': '缺少file_id参数'}), 400
    
    try:
        task_id = task_manager.submit_task(
            pdf_tasks.extract_text_task,
            file_id,
            pages if pages else None
        )
        
        return jsonify({
            'status': 'processing',
            'task_id': task_id
        }), 202
    except Exception as e:
        return jsonify({'error': str(e)}), 503

@app.route('/api/extract-text-enhanced', methods=['POST'])
def extract_text_enhanced():
    """提取PDF文字(增强版-保留排版和表格)"""
    data = request.json
    file_id = data.get('file_id')
    pages = data.get('pages', [])
    
    if not file_id:
        return jsonify({'error': '缺少file_id参数'}), 400
    
    try:
        task_id = task_manager.submit_task(
            pdf_tasks.extract_text_enhanced_task,
            file_id,
            pages if pages else None
        )
        
        return jsonify({
            'status': 'processing',
            'task_id': task_id
        }), 202
    except Exception as e:
        return jsonify({'error': str(e)}), 503

@app.route('/api/extract-text-clean', methods=['POST'])
def extract_text_clean():
    """提取PDF文字(清理版-智能合并断行)"""
    data = request.json
    file_id = data.get('file_id')
    pages = data.get('pages', [])
    
    if not file_id:
        return jsonify({'error': '缺少file_id参数'}), 400
    
    try:
        task_id = task_manager.submit_task(
            pdf_tasks.extract_text_clean_task,
            file_id,
            pages if pages else None
        )
        
        return jsonify({
            'status': 'processing',
            'task_id': task_id
        }), 202
    except Exception as e:
        return jsonify({'error': str(e)}), 503

@app.route('/api/extract-tables', methods=['POST'])
def extract_tables():
    """提取PDF表格"""
    data = request.json
    file_id = data.get('file_id')
    pages = data.get('pages', [])
    
    if not file_id:
        return jsonify({'error': '缺少file_id参数'}), 400
    
    try:
        task_id = task_manager.submit_task(
            pdf_tasks.extract_tables_task,
            file_id,
            pages if pages else None
        )
        
        return jsonify({
            'status': 'processing',
            'task_id': task_id
        }), 202
    except Exception as e:
        return jsonify({'error': str(e)}), 503

# ==================== 图片提取 ====================

@app.route('/api/extract-images', methods=['POST'])
def extract_images():
    """提取PDF图片"""
    data = request.json
    file_id = data.get('file_id')
    pages = data.get('pages', [])
    
    export_path = data.get('export_path')
    
    if not file_id:
        return jsonify({'error': '缺少file_id参数'}), 400
    
    try:
        task_id = task_manager.submit_task(
            pdf_tasks.extract_images_task,
            file_id,
            pages if pages else None,
            export_path
        )
        
        return jsonify({
            'status': 'processing',
            'task_id': task_id
        }), 202
    except Exception as e:
        return jsonify({'error': str(e)}), 503

# ==================== 页面操作 ====================

@app.route('/api/delete-pages', methods=['POST'])
def delete_pages():
    """删除PDF页面"""
    data = request.json
    file_id = data.get('file_id')
    pages = data.get('pages', [])
    
    if not file_id or not pages:
        return jsonify({'error': '参数错误'}), 400
    
    try:
        task_id = task_manager.submit_task(
            pdf_tasks.delete_pages_task,
            file_id,
            pages
        )
        
        return jsonify({
            'status': 'processing',
            'task_id': task_id
        }), 202
    except Exception as e:
        return jsonify({'error': str(e)}), 503

@app.route('/api/rotate-pages', methods=['POST'])
def rotate_pages():
    """旋转PDF页面"""
    data = request.json
    file_id = data.get('file_id')
    rotations = data.get('rotations', {})
    
    if not file_id or not rotations:
        return jsonify({'error': '参数错误'}), 400
    
    # 转换为整数键
    rotations = {int(k): v for k, v in rotations.items()}
    
    try:
        task_id = task_manager.submit_task(
            pdf_tasks.rotate_pages_task,
            file_id,
            rotations
        )
        
        return jsonify({
            'status': 'processing',
            'task_id': task_id
        }), 202
    except Exception as e:
        return jsonify({'error': str(e)}), 503

@app.route('/api/merge-pdfs', methods=['POST'])
def merge_pdfs():
    """合并多个PDF"""
    data = request.json
    file_ids = data.get('file_ids', [])
    
    if not file_ids or len(file_ids) < 2:
        return jsonify({'error': '至少需要2个PDF文件'}), 400
    
    try:
        task_id = task_manager.submit_task(
            pdf_tasks.merge_pdfs_task,
            file_ids
        )
        
        return jsonify({
            'status': 'processing',
            'task_id': task_id
        }), 202
    except Exception as e:
        return jsonify({'error': str(e)}), 503

# ==================== 加解密 ====================

@app.route('/api/encrypt', methods=['POST'])
def encrypt_pdf():
    """加密PDF"""
    data = request.json
    file_id = data.get('file_id')
    user_password = data.get('user_password')
    owner_password = data.get('owner_password')
    
    if not file_id or not user_password:
        return jsonify({'error': '参数错误'}), 400
    
    try:
        task_id = task_manager.submit_task(
            pdf_tasks.encrypt_pdf_task,
            file_id,
            user_password,
            owner_password
        )
        
        return jsonify({
            'status': 'processing',
            'task_id': task_id
        }), 202
    except Exception as e:
        return jsonify({'error': str(e)}), 503

@app.route('/api/decrypt', methods=['POST'])
def decrypt_pdf():
    """解密PDF"""
    data = request.json
    file_id = data.get('file_id')
    password = data.get('password')
    
    if not file_id or not password:
        return jsonify({'error': '参数错误'}), 400
    
    try:
        task_id = task_manager.submit_task(
            pdf_tasks.decrypt_pdf_task,
            file_id,
            password
        )
        
        return jsonify({
            'status': 'processing',
            'task_id': task_id
        }), 202
    except Exception as e:
        return jsonify({'error': str(e)}), 503

# ==================== PDF转Word ====================

@app.route('/api/convert-to-word', methods=['POST'])
def convert_to_word():
    """PDF转Word(保持格式)"""
    data = request.json
    file_id = data.get('file_id')
    pages = data.get('pages', [])
    export_path = data.get('export_path')
    
    if not file_id:
        return jsonify({'error': '缺少file_id参数'}), 400
    
    try:
        task_id = task_manager.submit_task(
            pdf_tasks.convert_to_word_task,
            file_id,
            pages if pages else None,
            export_path
        )
        
        return jsonify({
            'status': 'processing',
            'task_id': task_id
        }), 202
    except Exception as e:
        return jsonify({'error': str(e)}), 503

# ==================== 任务状态查询 ====================

@app.route('/api/task-status/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """查询任务状态"""
    status = task_manager.get_task_status(task_id)
    
    if not status:
        return jsonify({'error': '任务不存在'}), 404
    
    return jsonify(status)

# ==================== 文件下载 ====================

@app.route('/api/download/<file_id>', methods=['GET'])
def download_file(file_id):
    """下载处理后的PDF或Word文件"""
    folder = request.args.get('folder', 'processed')
    filepath = get_file_path(file_id, folder)
    
    if not filepath or not os.path.exists(filepath):
        return jsonify({'error': '文件不存在'}), 404
    
    try:
        # 判断文件类型
        file_ext = os.path.splitext(filepath)[1].lower()
        
        # 检查是否是docx文件
        if file_ext != '.pdf' and file_ext != '.docx':
            # 尝试查找docx文件
            docx_path = os.path.join(Config.PROCESSED_FOLDER, f"{file_id}.docx")
            if os.path.exists(docx_path):
                filepath = docx_path
                file_ext = '.docx'
        
        # 设置正确的MIME类型
        if file_ext == '.docx':
            mimetype = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            download_name = f"{file_id}.docx"
        else:
            mimetype = 'application/pdf'
            download_name = f"{file_id}.pdf"
        
        # 删除标记
        delete_after = request.args.get('delete_after', 'false').lower() == 'true'
        
        response = send_file(
            filepath,
            mimetype=mimetype,
            as_attachment=True,
            download_name=download_name
        )
        
        if delete_after:
            @response.call_on_close
            def cleanup():
                try:
                    if os.path.exists(filepath):
                        os.remove(filepath)
                except:
                    pass
        
        return response
    except Exception as e:
        return jsonify({'error': f'下载失败: {str(e)}'}), 500

@app.route('/api/images/<filename>', methods=['GET'])
def serve_image(filename):
    """服务缩略图或处理后的图片"""
    return send_from_directory(Config.PROCESSED_FOLDER, filename)

@app.route('/api/download-image', methods=['GET'])
def download_image_by_path():
    """通过绝对路径下载图片"""
    image_path = request.args.get('path')
    if not image_path or not os.path.exists(image_path):
        return jsonify({'error': '文件不存在'}), 404
    
    try:
        return send_file(
            image_path,
            as_attachment=True,
            download_name=os.path.basename(image_path)
        )
    except Exception as e:
        return jsonify({'error': f'下载失败: {str(e)}'}), 500

# ==================== 系统管理 ====================

@app.route('/api/cleanup', methods=['POST'])
def manual_cleanup():
    """手动触发清理"""
    result = cleanup_old_files()
    return jsonify({
        'message': '清理完成',
        **result
    })

# ==================== 定时任务 ====================

def scheduled_cleanup():
    """定时清理任务"""
    print("[定时任务] 开始清理过期文件...")
    result = cleanup_old_files()
    print(f"[定时任务] 清理完成: 删除{result['deleted_count']}个文件, 释放{result['freed_space_mb']}MB")
    
    # 清理旧任务记录
    deleted_tasks = task_manager.cleanup_old_tasks(max_age_hours=3)
    print(f"[定时任务] 清理了{deleted_tasks}条任务记录")

# 启动定时调度器
scheduler = BackgroundScheduler()
scheduler.add_job(
    scheduled_cleanup,
    'interval',
    minutes=Config.CLEANUP_INTERVAL_MINUTES,
    id='cleanup_files'
)
scheduler.start()

# ==================== 系统设置 ====================

from utils.settings_manager import settings

@app.route('/api/settings', methods=['GET'])
def get_settings():
    """获取当前系统设置"""
    return jsonify(settings.get_all())

@app.route('/api/settings', methods=['POST'])
def update_settings():
    """更新系统设置"""
    data = request.json
    updated = False
    
    for key, value in data.items():
        if settings.set(key, value):
            updated = True
            
    if updated:
        return jsonify({'status': 'success', 'settings': settings.get_all()})
    else:
        return jsonify({'error': '无有效设置项被修改'}), 400

# ==================== 应用启动 ====================

if __name__ == '__main__':
    print(f"=== PDF在线处理工具 ===")
    print(f"端口: {Config.PORT}")
    print(f"内存限制: {Config.MAX_CONTENT_LENGTH / 1024 / 1024}MB")
    print(f"并发任务数: {Config.MAX_WORKERS}")
    print(f"OCR功能: {'开启' if Config.ENABLE_OCR else '关闭'}")
    print(f"文件清理周期: {Config.CLEANUP_INTERVAL_MINUTES}分钟")
    print(f"========================")
    
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        threaded=True,
        debug=False
    )

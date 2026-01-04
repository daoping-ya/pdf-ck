import os
import uuid
import magic
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from config import Config

def allowed_file(filename):
    """检查文件类型是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def validate_pdf(file_stream):
    """验证文件是否为PDF(魔数校验)"""
    try:
        # 读取文件头
        header = file_stream.read(1024)
        file_stream.seek(0)  # 重置指针
        
        # 检查PDF魔数
        if header.startswith(b'%PDF-'):
            return True
        return False
    except:
        return False

def save_upload_file(file, file_id=None):
    """保存上传的PDF文件"""
    if not file_id:
        file_id = str(uuid.uuid4())
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(Config.TEMP_FOLDER, f"{file_id}.pdf")
    
    file.save(filepath)
    
    return {
        'file_id': file_id,
        'original_filename': filename,
        'storage_path': filepath,
        'file_size': os.path.getsize(filepath),
        'upload_time': datetime.now().isoformat()
    }

def get_file_path(file_id, folder='temp'):
    """
    获取文件路径 - 支持PDF和DOCX文件
    
    优先级:
    1. {file_id}.docx - 标准DOCX文件
    2. {file_id}_word.docx - PDF转Word生成的文件
    3. {file_id}.pdf - PDF文件
    
    Args:
        file_id: 文件ID
        folder: 文件夹类型 ('temp' 或 'processed')
    
    Returns:
        str: 文件完整路径,如果文件存在返回实际路径,否则返回默认PDF路径
    """
    if folder == 'temp':
        base_path = Config.TEMP_FOLDER
    elif folder == 'processed':
        base_path = Config.PROCESSED_FOLDER
    else:
        return None
    
    # 按优先级查找文件
    # 支持多种文件格式和命名方式以适应不同场景
    candidates = [
        os.path.join(base_path, f"{file_id}.docx"),         # 标准DOCX
        os.path.join(base_path, f"{file_id}_word.docx"),    # PDF转Word
        os.path.join(base_path, f"{file_id}.pdf")           # PDF文件
    ]
    
    for path in candidates:
        if os.path.exists(path):
            return path
    
    # 如果都不存在,返回默认PDF路径(向后兼容)
    return os.path.join(base_path, f"{file_id}.pdf")

def delete_file(file_id, folder='temp'):
    """删除文件"""
    filepath = get_file_path(file_id, folder)
    if filepath and os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False

def cleanup_old_files(max_age_minutes=None):
    """清理过期文件"""
    if max_age_minutes is None:
        max_age_minutes = Config.FILE_MAX_AGE_MINUTES
    
    now = datetime.now()
    deleted_count = 0
    freed_space = 0
    
    for folder in [Config.TEMP_FOLDER, Config.PROCESSED_FOLDER]:
        if not os.path.exists(folder):
            continue
            
        for filename in os.listdir(folder):
            filepath = os.path.join(folder, filename)
            
            if not os.path.isfile(filepath):
                continue
            
            # 检查文件修改时间
            file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
            if now - file_mtime > timedelta(minutes=max_age_minutes):
                file_size = os.path.getsize(filepath)
                os.remove(filepath)
                deleted_count += 1
                freed_space += file_size
    
    return {
        'deleted_count': deleted_count,
        'freed_space_mb': round(freed_space / 1024 / 1024, 2)
    }

def get_disk_usage():
    """获取磁盘使用情况"""
    import shutil
    
    try:
        stat = shutil.disk_usage(Config.BASE_DIR)
        return {
            'total_gb': round(stat.total / 1024**3, 2),
            'used_gb': round(stat.used / 1024**3, 2),
            'free_gb': round(stat.free / 1024**3, 2),
            'used_percent': round((stat.used / stat.total) * 100, 1)
        }
    except:
        return None

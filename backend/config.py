import os

class Config:
    """极限资源VPS配置"""
    
    # 服务器配置
    PORT = int(os.environ.get('PDF_PROCESSOR_PORT', 5000))
    HOST = os.environ.get('PDF_PROCESSOR_HOST', '0.0.0.0')
    SECRET_KEY = os.environ.get('SECRET_KEY', os.urandom(24))
    
    # 路径配置
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    TEMP_FOLDER = os.path.join(UPLOAD_FOLDER, 'temp')
    PROCESSED_FOLDER = os.path.join(UPLOAD_FOLDER, 'processed')
    DATA_FOLDER = os.path.join(BASE_DIR, 'data')
    DB_PATH = os.path.join(DATA_FOLDER, 'tasks.db')
    
    # 资源限制(极限优化)
    MAX_WORKERS = 1  # 单worker避免内存溢出
    MAX_CONTENT_LENGTH = 20 * 1024 * 1024  # 20MB文件限制
    MAX_PAGES_PER_TASK = 30  # 最大处理页数
    
    # 功能开关
    ENABLE_OCR = False  # 禁用OCR节省内存
    ENABLE_LAYOUT_CONVERSION = False  # 禁用排版复刻
    ENABLE_WATERMARK_REMOVAL = True  # 水印去除
    
    # 性能优化
    PREVIEW_DPI = 96  # 预览图质量(降低节省内存)
    IMAGE_EXTRACT_QUALITY = 75  # 图片导出质量
    TASK_TIMEOUT = 120  # 任务超时时间(秒)
    
    # 文件清理
    CLEANUP_INTERVAL_MINUTES = 30  # 清理间隔
    FILE_MAX_AGE_MINUTES = 30  # 文件过期时间(30分钟)
    
    # CORS配置
    CORS_ORIGINS = ['*']
    
    # 允许的文件类型
    ALLOWED_EXTENSIONS = {'pdf'}
    
    @staticmethod
    def init_app():
        """初始化应用目录"""
        for folder in [Config.UPLOAD_FOLDER, Config.TEMP_FOLDER, 
                      Config.PROCESSED_FOLDER, Config.DATA_FOLDER]:
            os.makedirs(folder, exist_ok=True)

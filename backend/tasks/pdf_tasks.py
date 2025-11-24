"""PDF处理异步任务"""
from services.pdf_service import PDFService
from services.enhanced_pdf_service import EnhancedPDFService
from task_manager import task_manager

def _get_progress_callback(task_id):
    """生成进度回调函数"""
    def progress_callback(progress):
        task_manager.update_progress(task_id, progress)
    return progress_callback

def extract_text_task(task_id, file_id, pages=None):
    """文字提取任务(基础版)"""
    result = PDFService.extract_text(file_id, pages, progress_callback=_get_progress_callback(task_id))
    return result

def extract_text_enhanced_task(task_id, file_id, pages=None):
    """文字提取任务(增强版-保留排版)"""
    # 增强版暂不支持细粒度进度，先模拟
    cb = _get_progress_callback(task_id)
    cb(10)
    result = EnhancedPDFService.extract_structured_content(file_id, pages)
    cb(90)
    return result

def extract_text_clean_task(task_id, file_id, pages=None):
    """文字提取任务(清理版-移除多余换行)"""
    cb = _get_progress_callback(task_id)
    cb(10)
    result = EnhancedPDFService.extract_text_clean(file_id, pages)
    cb(90)
    return result

def extract_tables_task(task_id, file_id, pages=None):
    """表格提取任务"""
    cb = _get_progress_callback(task_id)
    cb(10)
    result = EnhancedPDFService.extract_tables_only(file_id, pages)
    cb(90)
    return result

def extract_images_task(task_id, file_id, pages=None, export_path=None):
    """图片提取任务"""
    result = PDFService.extract_images(file_id, pages, export_path, progress_callback=_get_progress_callback(task_id))
    return result

def delete_pages_task(task_id, file_id, pages_to_delete):
    """删除页面任务"""
    result = PDFService.delete_pages(file_id, pages_to_delete, progress_callback=_get_progress_callback(task_id))
    return result

def rotate_pages_task(task_id, file_id, rotations):
    """旋转页面任务"""
    result = PDFService.rotate_pages(file_id, rotations, progress_callback=_get_progress_callback(task_id))
    return result

def merge_pdfs_task(task_id, file_ids):
    """合并PDF任务"""
    result = PDFService.merge_pdfs(file_ids, progress_callback=_get_progress_callback(task_id))
    return result

def encrypt_pdf_task(task_id, file_id, user_password, owner_password=None):
    """加密PDF任务"""
    # 加密通常很快，简单处理
    cb = _get_progress_callback(task_id)
    cb(50)
    result = PDFService.encrypt_pdf(file_id, user_password, owner_password)
    return result

def decrypt_pdf_task(task_id, file_id, password):
    """解密PDF任务"""
    cb = _get_progress_callback(task_id)
    cb(50)
    result = PDFService.decrypt_pdf(file_id, password)
    return result

def convert_to_word_task(task_id, file_id, pages=None, export_path=None):
    """PDF转Word任务"""
    from services.pdf2word_service import PDF2WordService
    result = PDF2WordService.convert_to_word(file_id, pages, export_path, progress_callback=_get_progress_callback(task_id))
    return result

"""PDF转Word服务 - 保持原始格式"""
import fitz
import os
from config import Config
from utils.file_handler import get_file_path

class PDF2WordService:
    """PDF转Word服务,保持完整格式"""
    
    @staticmethod
    def convert_to_word(file_id, pages=None, export_path=None, progress_callback=None):
        """
        将PDF转换为Word文档,保持原始格式
        使用pdf2docx库实现1:1格式转换
        """
        # 延迟导入pdf2docx,避免启动时的导入错误
        try:
            from pdf2docx import Converter
        except ImportError:
            raise Exception("pdf2docx未安装,请运行: pip install pdf2docx==0.5.6")
        
        input_path = get_file_path(file_id)
        
        if not os.path.exists(input_path):
            raise FileNotFoundError("PDF文件不存在")
        
        try:
            # 确定导出路径: 优先使用参数,其次使用设置
            from utils.settings_manager import settings
            
            # 如果未提供参数,尝试从设置获取
            if not export_path:
                export_path = settings.get('export_path')
            
            if export_path and os.path.isdir(export_path):
                # 使用配置的导出路径
                output_filename = f"{os.path.splitext(os.path.basename(input_path))[0]}.docx"
                output_path = os.path.join(export_path, output_filename)
                saved_to_local = True
            else:
                # 使用默认处理目录
                output_id = f"{file_id}_word"
                output_path = os.path.join(Config.PROCESSED_FOLDER, f"{output_id}.docx")
                saved_to_local = False
            
            # 创建转换器
            cv = Converter(input_path)
            
            if progress_callback:
                progress_callback(5)
            
            # 转换PDF到Word
            # start和end参数:页码范围(0开始索引)
            if pages and len(pages) > 0:
                # 转换指定页面
                start_page = min(pages)
                end_page = max(pages)
                cv.convert(output_path, start=start_page, end=end_page+1)
            else:
                # 转换所有页面
                cv.convert(output_path)
            
            if progress_callback:
                progress_callback(100)
            
            cv.close()
            
            # 获取输出文件信息
            file_size = os.path.getsize(output_path)
            
            result = {
                'output_filename': os.path.basename(output_path),
                'file_size': file_size,
                'pages_converted': 'all' if not pages else len(pages),
                'saved_to_local': saved_to_local
            }
            
            if saved_to_local:
                result['saved_path'] = output_path
            else:
                result['output_file_id'] = output_id
                
            return result
            
        except Exception as e:
            raise Exception(f"PDF转Word失败: {str(e)}")
    
    @staticmethod
    def convert_with_options(file_id, options=None):
        """
        高级转换选项
        options: {
            'pages': [1,2,3],  # 指定页码
            'image_quality': 95,  # 图片质量
            'preserve_fonts': True  # 保留字体
        }
        """
        input_path = get_file_path(file_id)
        
        if not os.path.exists(input_path):
            raise FileNotFoundError("PDF文件不存在")
        
        if options is None:
            options = {}
        
        try:
            output_id = f"{file_id}_word"
            output_path = os.path.join(Config.PROCESSED_FOLDER, f"{output_id}.docx")
            
            cv = Converter(input_path)
            
            # 设置转换参数
            pages = options.get('pages', None)
            
            if pages and len(pages) > 0:
                start_page = min(pages)
                end_page = max(pages)
                cv.convert(output_path, start=start_page, end=end_page+1)
            else:
                cv.convert(output_path)
            
            cv.close()
            
            return {
                'output_file_id': output_id,
                'output_filename': f"{output_id}.docx",
                'file_size': os.path.getsize(output_path)
            }
            
        except Exception as e:
            raise Exception(f"转换失败: {str(e)}")

"""增强的PDF内容提取服务 - 保留排版和表格"""
import fitz
import pdfplumber
import os
from config import Config
from utils.file_handler import get_file_path
from utils.settings_manager import settings

class EnhancedPDFService:
    """增强版PDF提取服务,支持排版保留和表格识别"""
    
    @staticmethod
    def extract_structured_content(file_id, pages=None):
        """
        提取结构化内容(保留排版、表格、图片位置)
        返回HTML格式的内容
        """
        # 检查功能开关
        if not settings.get('enable_layout_preservation'):
            raise Exception("排版复刻功能已关闭(请在设置中开启)")

        filepath = get_file_path(file_id)
        
        if not os.path.exists(filepath):
            raise FileNotFoundError("PDF文件不存在")
        
        try:
            html_output = []
            html_output.append('<div class="pdf-content">')
            
            # 初始化OCR (如果开启)
            ocr_engine = None
            if settings.get('enable_ocr'):
                try:
                    from rapidocr_onnxruntime import RapidOCR
                    ocr_engine = RapidOCR()
                except ImportError:
                    print("Warning: rapidocr_onnxruntime not installed")
            
            with pdfplumber.open(filepath) as pdf:
                total_pages = len(pdf.pages)
                
                # 如果未指定页码,提取所有页
                if not pages:
                    pages = list(range(total_pages))
                
                # 限制页数
                if len(pages) > Config.MAX_PAGES_PER_TASK:
                    pages = pages[:Config.MAX_PAGES_PER_TASK]
                
                for page_num in pages:
                    if 0 <= page_num < total_pages:
                        page = pdf.pages[page_num]
                        
                        # 添加分页符(仅CSS样式,不显示文字)
                        if page_num > 0:
                            html_output.append('<div class="page-break"></div>')
                        
                        html_output.append(f'<div class="page" data-page="{page_num + 1}">')
                        
                        # 提取表格
                        tables = page.extract_tables()
                        if tables:
                            for table in tables:
                                html_output.append('<table class="pdf-table">')
                                for row_idx, row in enumerate(table):
                                    if row_idx == 0:
                                        html_output.append('<thead><tr>')
                                        for cell in row:
                                            cell_text = str(cell).strip() if cell else ''
                                            html_output.append(f'<th>{cell_text}</th>')
                                        html_output.append('</tr></thead><tbody>')
                                    else:
                                        html_output.append('<tr>')
                                        for cell in row:
                                            cell_text = str(cell).strip() if cell else ''
                                            html_output.append(f'<td>{cell_text}</td>')
                                        html_output.append('</tr>')
                                html_output.append('</tbody></table>')
                        
                        # 提取文字(使用layout模式保留排版)
                        text = page.extract_text(layout=True)
                        
                        # 如果没有提取到文字且开启了OCR，尝试OCR
                        if (not text or not text.strip()) and ocr_engine:
                            # 将页面转换为图片
                            # 注意: pdfplumber的to_image需要pdf2image和poppler支持，或者使用fitz
                            # 这里我们使用fitz来获取图片，因为fitz更轻量且已安装
                            doc = fitz.open(filepath)
                            pix = doc[page_num].get_pixmap(dpi=200)
                            img_data = pix.tobytes("png")
                            
                            ocr_result, _ = ocr_engine(img_data)
                            if ocr_result:
                                # RapidOCR返回格式: [[[[x1,y1],[x2,y2],[x3,y3],[x4,y4]], "text", score], ...]
                                # 简单拼接文字
                                text = "\n".join([line[1] for line in ocr_result])
                                html_output.append(f'<div class="ocr-badge">🔍 OCR识别内容</div>')
                            doc.close()

                        if text:
                            # 分段处理,保留段落结构
                            paragraphs = text.split('\n\n')
                            for para in paragraphs:
                                if para.strip():
                                    # 清理但保留必要的换行
                                    # 保留原始空格以维持排版(不要strip)
                                    lines = para.split('\n')
                                    # 仅去除空行,但不去除行首尾空格
                                    cleaned_lines = [line for line in lines if line.strip()]
                                    if cleaned_lines:
                                        para_text = '<br>'.join(cleaned_lines)
                                        html_output.append(f'<p>{para_text}</p>')
                        
                        # 标记图片位置(使用小图标)
                        images = page.images
                        if images:
                            html_output.append(f'<div class="image-marker">🖼️ 包含{len(images)}张图片</div>')
                        
                        html_output.append('</div>')
            
            html_output.append('</div>')
            
            # 添加优化的CSS样式
            css = """
            <style>
            .pdf-content { 
                font-family: 'Microsoft YaHei', 'PingFang SC', 'Hiragino Sans GB', Arial, sans-serif;
                max-width: 900px;
                margin: 0 auto;
                padding: 20px;
                background: white;
                color: #1a1a1a;
                line-height: 1.8;
            }
            .page {
                margin: 0;
                padding: 30px;
                background: white;
            }
            .page-break {
                page-break-after: always;
                border-top: 2px dashed #e0e0e0;
                margin: 40px 0;
                height: 1px;
            }
            .pdf-table {
                width: 100%;
                margin: 20px 0;
                border-collapse: collapse;
                background: white;
                font-size: 14px;
            }
            .pdf-table th {
                background: #f5f5f5;
                color: #333;
                font-weight: 600;
                text-align: left;
                padding: 12px;
                border: 1px solid #ddd;
            }
            .pdf-table td {
                background: white;
                color: #1a1a1a;
                padding: 10px 12px;
                border: 1px solid #ddd;
            }
            .pdf-content p {
                line-height: 2;
                text-align: justify;
                margin: 15px 0;
                color: #1a1a1a;
                font-size: 15px;
                text-indent: 0;
            }
            .image-marker {
                margin: 15px 0;
                padding: 10px 15px;
                background: #f0f9ff;
                border-left: 4px solid #3b82f6;
                color: #1e40af;
                font-size: 14px;
                border-radius: 4px;
            }
            </style>
            """
            
            return {
                'html': css + ''.join(html_output),
                'extracted_pages': len(pages)
            }
            
        except Exception as e:
            raise Exception(f"结构化提取失败: {str(e)}")
    
    @staticmethod
    def extract_text_clean(file_id, pages=None):
        """
        提取纯净文字(清理换行符和特殊字符)
        """
        filepath = get_file_path(file_id)
        
        if not os.path.exists(filepath):
            raise FileNotFoundError("PDF文件不存在")
        
        try:
            with pdfplumber.open(filepath) as pdf:
                total_pages = len(pdf.pages)
                
                if not pages:
                    pages = list(range(total_pages))
                
                if len(pages) > Config.MAX_PAGES_PER_TASK:
                    pages = pages[:Config.MAX_PAGES_PER_TASK]
                
                extracted_text = {}
                
                for page_num in pages:
                    if 0 <= page_num < total_pages:
                        page = pdf.pages[page_num]
                        text = page.extract_text()
                        
                        if text:
                            # 清理文本:合并断行,移除多余空格
                            lines = text.split('\n')
                            cleaned_lines = []
                            
                            for line in lines:
                                line = line.strip()
                                if line:
                                    cleaned_lines.append(line)
                            
                            # 智能合并:如果行末没有标点,与下一行合并
                            merged_text = []
                            i = 0
                            while i < len(cleaned_lines):
                                current_line = cleaned_lines[i]
                                
                                # 如果当前行以标点结尾,或是最后一行,直接添加
                                if i == len(cleaned_lines) - 1 or current_line.endswith(('。', '!', '?', ';', ':', '、', ',', '.', '！', '?', ';')):
                                    merged_text.append(current_line)
                                else:
                                    # 否则与下一行合并
                                    if i + 1 < len(cleaned_lines):
                                        current_line += cleaned_lines[i + 1]
                                        i += 1
                                    merged_text.append(current_line)
                                
                                i += 1
                            
                            extracted_text[str(page_num + 1)] = '\n'.join(merged_text)
                
                return {
                    'total_pages': total_pages,
                    'extracted_pages': len(extracted_text),
                    'text': extracted_text
                }
            
        except Exception as e:
            raise Exception(f"文字提取失败: {str(e)}")
    
    @staticmethod
    def extract_tables_only(file_id, pages=None):
        """仅提取表格数据"""
        filepath = get_file_path(file_id)
        
        if not os.path.exists(filepath):
            raise FileNotFoundError("PDF文件不存在")
        
        try:
            with pdfplumber.open(filepath) as pdf:
                total_pages = len(pdf.pages)
                
                if not pages:
                    pages = list(range(total_pages))
                
                if len(pages) > Config.MAX_PAGES_PER_TASK:
                    pages = pages[:Config.MAX_PAGES_PER_TASK]
                
                all_tables = {}
                total_table_count = 0
                
                for page_num in pages:
                    if 0 <= page_num < total_pages:
                        page = pdf.pages[page_num]
                        tables = page.extract_tables()
                        
                        if tables:
                            page_tables = []
                            for table in tables:
                                # 直接保留原始表格结构(二维数组)，不强制转换字典
                                # 过滤掉全空的行
                                cleaned_table = [row for row in table if any(cell and str(cell).strip() for cell in row)]
                                if cleaned_table:
                                    page_tables.append({
                                        'data': cleaned_table,
                                        'row_count': len(cleaned_table),
                                        'col_count': len(cleaned_table[0]) if cleaned_table else 0
                                    })
                            
                            if page_tables:
                                all_tables[str(page_num + 1)] = page_tables
                                total_table_count += len(page_tables)
                
                return {
                    'total_pages': total_pages,
                    'extracted_pages': len([p for p in all_tables if all_tables[p]]),
                    'total_tables': total_table_count,
                    'tables': all_tables
                }
            
        except Exception as e:
            raise Exception(f"表格提取失败: {str(e)}")

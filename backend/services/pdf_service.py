import fitz  # PyMuPDF
import pikepdf
import os
from PIL import Image
from io import BytesIO
from config import Config
from utils.file_handler import get_file_path

class PDFService:
    """PDF处理核心服务"""
    
    @staticmethod
    def get_metadata(file_id):
        """获取PDF元数据"""
        filepath = get_file_path(file_id)
        
        if not os.path.exists(filepath):
            raise FileNotFoundError("PDF文件不存在")
        
        try:
            doc = fitz.open(filepath)
            metadata = {
                'page_count': len(doc),
                'is_encrypted': doc.is_encrypted,
                'title': doc.metadata.get('title', ''),
                'author': doc.metadata.get('author', ''),
                'subject': doc.metadata.get('subject', ''),
                'creator': doc.metadata.get('creator', ''),
                'producer': doc.metadata.get('producer', ''),
                'creation_date': doc.metadata.get('creationDate', ''),
                'modification_date': doc.metadata.get('modDate', '')
            }
            doc.close()
            return metadata
        except Exception as e:
            raise Exception(f"读取PDF元数据失败: {str(e)}")
    
    @staticmethod
    def extract_text(file_id, pages=None, progress_callback=None):
        """提取PDF文字内容"""
        filepath = get_file_path(file_id)
        
        if not os.path.exists(filepath):
            raise FileNotFoundError("PDF文件不存在")
        
        try:
            doc = fitz.open(filepath)
            total_pages = len(doc)
            
            # 如果未指定页码,提取所有页
            if not pages:
                pages = list(range(total_pages))
            
            # 限制页数
            if len(pages) > Config.MAX_PAGES_PER_TASK:
                pages = pages[:Config.MAX_PAGES_PER_TASK]
            
            extracted_text = {}
            total_to_process = len(pages)
            
            for i, page_num in enumerate(pages):
                if 0 <= page_num < total_pages:
                    page = doc[page_num]
                    text = page.get_text()
                    extracted_text[str(page_num + 1)] = text  # 1-indexed
                
                if progress_callback:
                    progress_callback(int((i + 1) / total_to_process * 100))
            
            doc.close()
            
            return {
                'total_pages': total_pages,
                'extracted_pages': len(extracted_text),
                'text': extracted_text
            }
        except Exception as e:
            raise Exception(f"提取文字失败: {str(e)}")
    
    @staticmethod
    def extract_images(file_id, pages=None, export_path=None, progress_callback=None):
        """提取PDF中的图片"""
        filepath = get_file_path(file_id)
        
        if not os.path.exists(filepath):
            raise FileNotFoundError("PDF文件不存在")
        
        try:
            doc = fitz.open(filepath)
            total_pages = len(doc)
            
            if not pages:
                pages = list(range(total_pages))
            
            if len(pages) > Config.MAX_PAGES_PER_TASK:
                pages = pages[:Config.MAX_PAGES_PER_TASK]
            
            # 确定保存目录
            if export_path:
                if not os.path.exists(export_path):
                    os.makedirs(export_path)
                save_dir = export_path
                saved_to_custom_path = True
            else:
                save_dir = Config.PROCESSED_FOLDER
                saved_to_custom_path = False
            
            images = []
            image_count = 0
            total_to_process = len(pages)
            
            for i, page_num in enumerate(pages):
                if 0 <= page_num < total_pages:
                    page = doc[page_num]
                    image_list = page.get_images()
                    
                    for img_index, img in enumerate(image_list):
                        xref = img[0]
                        base_image = doc.extract_image(xref)
                        image_bytes = base_image["image"]
                        image_ext = base_image["ext"]
                        
                        # 保存图片
                        image_filename = f"{os.path.splitext(os.path.basename(filepath))[0]}_p{page_num+1}_{img_index+1}.{image_ext}"
                        image_path = os.path.join(save_dir, image_filename)
                        
                        with open(image_path, "wb") as img_file:
                            img_file.write(image_bytes)
                        
                        # 生成缩略图
                        thumbnail_filename = f"thumb_{image_filename}"
                        thumbnail_path = os.path.join(Config.PROCESSED_FOLDER, thumbnail_filename)
                        
                        try:
                            with Image.open(BytesIO(image_bytes)) as pil_img:
                                if pil_img.mode in ('RGBA', 'LA') or (pil_img.mode == 'P' and 'transparency' in pil_img.info):
                                    bg = Image.new('RGB', pil_img.size, (255, 255, 255))
                                    if pil_img.mode == 'P':
                                        pil_img = pil_img.convert('RGBA')
                                    bg.paste(pil_img, mask=pil_img.split()[3])
                                    pil_img = bg
                                elif pil_img.mode != 'RGB':
                                    pil_img = pil_img.convert('RGB')
                                
                                pil_img.thumbnail((600, 600))
                                pil_img.save(thumbnail_path, "JPEG", quality=90)
                        except Exception as e:
                            print(f"生成缩略图失败: {e}")
                            thumbnail_filename = None

                        images.append({
                            'filename': image_filename,
                            'path': image_path,
                            'thumbnail': thumbnail_filename,
                            'page': page_num + 1,
                            'format': image_ext,
                            'size': len(image_bytes)
                        })
                        image_count += 1
                
                if progress_callback:
                    progress_callback(int((i + 1) / total_to_process * 100))
            
            doc.close()
            
            return {
                'total_images': image_count,
                'images': images,
                'saved_to_custom_path': saved_to_custom_path,
                'export_path': save_dir if saved_to_custom_path else None
            }
        except Exception as e:
            raise Exception(f"提取图片失败: {str(e)}")
    
    @staticmethod
    def export_pages_as_images(file_id, pages=None, dpi=300, image_format='png', export_path=None, progress_callback=None):
        """将PDF页面导出为高质量图片
        
        Args:
            file_id: PDF文件ID
            pages: 页码列表（0-indexed），None表示所有页
            dpi: 分辨率，默认300（印刷质量），可选150/300/600
            image_format: 图片格式，'png'或'jpeg'
            export_path: 导出路径，None则使用默认处理目录
            progress_callback: 进度回调函数
        
        Returns:
            dict: {
                'total_images': 导出图片数量,
                'images': 图片信息列表,
                'saved_to_custom_path': 是否保存到自定义路径,
                'export_path': 导出路径
            }
        """
        filepath = get_file_path(file_id)
        
        if not os.path.exists(filepath):
            raise FileNotFoundError("PDF文件不存在")
        
        try:
            doc = fitz.open(filepath)
            total_pages = len(doc)
            
            if not pages:
                pages = list(range(total_pages))
            
            if len(pages) > Config.MAX_PAGES_PER_TASK:
                pages = pages[:Config.MAX_PAGES_PER_TASK]
            
            # 确定保存目录
            if export_path:
                if not os.path.exists(export_path):
                    os.makedirs(export_path)
                save_dir = export_path
                saved_to_custom_path = True
            else:
                save_dir = Config.PROCESSED_FOLDER
                saved_to_custom_path = False
            
            images = []
            total_to_process = len(pages)
            
            # 计算缩放比例
            zoom = dpi / 72  # 72 DPI是PDF默认值
            mat = fitz.Matrix(zoom, zoom)
            
            for i, page_num in enumerate(pages):
                if 0 <= page_num < total_pages:
                    page = doc[page_num]
                    
                    # 渲染页面为图片
                    pix = page.get_pixmap(matrix=mat)
                    
                    # 生成文件名
                    base_name = os.path.splitext(os.path.basename(filepath))[0]
                    if image_format.lower() == 'png':
                        image_filename = f"{base_name}_page{page_num+1}_{dpi}dpi.png"
                        img_bytes = pix.tobytes("png")
                    else:  # jpeg
                        image_filename = f"{base_name}_page{page_num+1}_{dpi}dpi.jpg"
                        img_bytes = pix.tobytes("jpeg", jpg_quality=95)
                    
                    image_path = os.path.join(save_dir, image_filename)
                    
                    # 保存图片
                    with open(image_path, "wb") as img_file:
                        img_file.write(img_bytes)
                    
                    images.append({
                        'filename': image_filename,
                        'path': image_path,
                        'page': page_num + 1,
                        'format': image_format.upper(),
                        'size': len(img_bytes),
                        'dpi': dpi,
                        'width': pix.width,
                        'height': pix.height
                    })
                
                if progress_callback:
                    progress_callback(int((i + 1) / total_to_process * 100))
            
            doc.close()
            
            return {
                'total_images': len(images),
                'images': images,
                'saved_to_custom_path': saved_to_custom_path,
                'export_path': save_dir if saved_to_custom_path else None
            }
        except Exception as e:
            raise Exception(f"导出页面为图片失败: {str(e)}")
    
    @staticmethod
    def convert_to_html(file_id, mode='text', progress_callback=None):
        """转换PDF为HTML格式
        
        Args:
            file_id: PDF文件ID
            mode: 转换模式 'text' | 'image' | 'hybrid'
            progress_callback: 进度回调函数
        
        Returns:
            dict: {
                'html_file': HTML文件名,
                'html_path': HTML文件路径,
                'mode': 转换模式,
                'total_pages': 总页数
            }
        """
        filepath = get_file_path(file_id)
        
        if not os.path.exists(filepath):
            raise FileNotFoundError("PDF文件不存在")
        
        try:
            doc = fitz.open(filepath)
            total_pages = len(doc)
            
            # 生成HTML文件名
            base_name = os.path.splitext(os.path.basename(filepath))[0]
            html_filename = f"{base_name}.html"
            html_path = os.path.join(Config.PROCESSED_FOLDER, html_filename)
            
            # 开始转换
            html_content = []
            
            # HTML头部
            html_content.append('<!DOCTYPE html>')
            html_content.append('<html lang="zh-CN">')
            html_content.append('<head>')
            html_content.append('    <meta charset="UTF-8">')
            html_content.append('    <meta name="viewport" content="width=device-width, initial-scale=1.0">')
            html_content.append(f'    <title>{base_name}</title>')
            html_content.append('    <style>')
            html_content.append('        body { font-family: Arial, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; background: #f5f5f5; }')
            html_content.append('        .page { background: white; padding: 40px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); page-break-after: always; }')
            html_content.append('        .page-number { text-align: center; color: #999; font-size: 12px; margin-top: 20px; }')
            html_content.append('        @media print { .page { box-shadow: none; margin: 0; } }')
            html_content.append('    </style>')
            html_content.append('</head>')
            html_content.append('<body>')
            
            # 转换每一页
            for page_num in range(total_pages):
                page = doc[page_num]
                
                html_content.append(f'<div class="page" id="page-{page_num + 1}">')
                
                if mode == 'text':
                    # 文字模式：提取文字和基本HTML结构
                    page_html = page.get_text("html")
                    html_content.append(page_html)
                    
                elif mode == 'image':
                    # 图片模式：渲染为高清图片
                    zoom = 2  # 2倍缩放以提高清晰度
                    mat = fitz.Matrix(zoom, zoom)
                    pix = page.get_pixmap(matrix=mat)
                    
                    # 转为base64嵌入
                    img_data = pix.tobytes("png")
                    import base64
                    img_base64 = base64.b64encode(img_data).decode()
                    
                    html_content.append(f'<img src="data:image/png;base64,{img_base64}" style="width: 100%; height: auto;" alt="Page {page_num + 1}">')
                    
                elif mode == 'hybrid':
                    # 混合模式：背景图片 + 文字层
                    zoom = 1.5
                    mat = fitz.Matrix(zoom, zoom)
                    pix = page.get_pixmap(matrix=mat)
                    
                    import base64
                    img_data = pix.tobytes("png")
                    img_base64 = base64.b64encode(img_data).decode()
                    
                    html_content.append(f'<div style="position: relative;">')
                    html_content.append(f'<img src="data:image/png;base64,{img_base64}" style="width: 100%; height: auto; position: absolute; top: 0; left: 0; z-index: 0;" alt="Background">')
                    html_content.append(f'<div style="position: relative; z-index: 1;">')
                    page_html = page.get_text("html")
                    html_content.append(page_html)
                    html_content.append('</div>')
                    html_content.append('</div>')
                
                html_content.append(f'<div class="page-number">第 {page_num + 1} 页 / 共 {total_pages} 页</div>')
                html_content.append('</div>')
                
                if progress_callback:
                    progress_callback(int((page_num + 1) / total_pages * 100))
            
            # HTML尾部
            html_content.append('</body>')
            html_content.append('</html>')
            
            # 写入文件
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(html_content))
            
            doc.close()
            
            return {
                'html_file': html_filename,
                'html_path': html_path,
                'mode': mode,
                'total_pages': total_pages,
                'file_size': os.path.getsize(html_path)
            }
        except Exception as e:
            raise Exception(f"转换HTML失败: {str(e)}")
    
    @staticmethod
    def render_page_preview(file_id, page_num=1, dpi=None):
        """渲染PDF页面预览图"""
        filepath = get_file_path(file_id)
        
        if not os.path.exists(filepath):
            raise FileNotFoundError("PDF文件不存在")
        
        if dpi is None:
            dpi = Config.PREVIEW_DPI
        
        try:
            doc = fitz.open(filepath)
            
            if page_num < 1 or page_num > len(doc):
                raise ValueError(f"页码超出范围(1-{len(doc)})")
            
            page = doc[page_num - 1]  # 0-indexed
            
            # 渲染为图片
            zoom = dpi / 72  # 72 DPI是默认值
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            
            # 转换为PNG字节
            img_bytes = pix.tobytes("png")
            
            doc.close()
            
            return img_bytes
        except Exception as e:
            raise Exception(f"渲染预览失败: {str(e)}")
    
    @staticmethod
    def delete_pages(file_id, pages_to_delete, progress_callback=None):
        """删除指定页面"""
        filepath = get_file_path(file_id)
        
        if not os.path.exists(filepath):
            raise FileNotFoundError("PDF文件不存在")
        
        try:
            doc = fitz.open(filepath)
            
            # 转换为0-indexed并排序(从后往前删除)
            pages_to_delete = sorted([p-1 for p in pages_to_delete], reverse=True)
            total = len(pages_to_delete)
            
            for i, page_num in enumerate(pages_to_delete):
                if 0 <= page_num < len(doc):
                    doc.delete_page(page_num)
                if progress_callback:
                    progress_callback(int((i + 1) / total * 100))
            
            # 保存为新文件
            output_id = f"{file_id}_deleted"
            output_path = get_file_path(output_id, 'processed')
            doc.save(output_path)
            doc.close()
            
            return {
                'output_file_id': output_id,
                'deleted_pages': len(pages_to_delete),
                'remaining_pages': fitz.open(output_path).page_count
            }
        except Exception as e:
            raise Exception(f"删除页面失败: {str(e)}")
    
    @staticmethod
    def rotate_pages(file_id, rotations, progress_callback=None):
        """旋转页面
        rotations: {page_num: angle} 例如 {1: 90, 3: 180}
        """
        filepath = get_file_path(file_id)
        
        if not os.path.exists(filepath):
            raise FileNotFoundError("PDF文件不存在")
        
        try:
            doc = fitz.open(filepath)
            total = len(rotations)
            
            for i, (page_num, angle) in enumerate(rotations.items()):
                if 1 <= page_num <= len(doc):
                    page = doc[page_num - 1]
                    page.set_rotation(angle)
                if progress_callback:
                    progress_callback(int((i + 1) / total * 100))
            
            output_id = f"{file_id}_rotated"
            output_path = get_file_path(output_id, 'processed')
            doc.save(output_path)
            doc.close()
            
            return {
                'output_file_id': output_id,
                'rotated_pages': len(rotations)
            }
        except Exception as e:
            raise Exception(f"旋转页面失败: {str(e)}")
    
    @staticmethod
    def merge_pdfs(file_ids, progress_callback=None):
        """合并多个PDF"""
        try:
            result_doc = fitz.open()
            total = len(file_ids)
            
            for i, file_id in enumerate(file_ids):
                filepath = get_file_path(file_id)
                if os.path.exists(filepath):
                    src_doc = fitz.open(filepath)
                    result_doc.insert_pdf(src_doc)
                    src_doc.close()
                if progress_callback:
                    progress_callback(int((i + 1) / total * 100))
            
            output_id = f"merged_{file_ids[0]}"
            output_path = get_file_path(output_id, 'processed')
            result_doc.save(output_path)
            total_pages = len(result_doc)
            result_doc.close()
            
            return {
                'output_file_id': output_id,
                'merged_files': len(file_ids),
                'total_pages': total_pages
            }
        except Exception as e:
            raise Exception(f"合并PDF失败: {str(e)}")
    
    @staticmethod
    def encrypt_pdf(file_id, user_password, owner_password=None):
        """加密PDF"""
        filepath = get_file_path(file_id)
        
        if not os.path.exists(filepath):
            raise FileNotFoundError("PDF文件不存在")
        
        try:
            with pikepdf.open(filepath) as pdf:
                output_id = f"{file_id}_encrypted"
                output_path = get_file_path(output_id, 'processed')
                
                pdf.save(
                    output_path,
                    encryption=pikepdf.Encryption(
                        user=user_password,
                        owner=owner_password or user_password
                    )
                )
            
            return {
                'output_file_id': output_id
            }
        except Exception as e:
            raise Exception(f"加密PDF失败: {str(e)}")
    
    @staticmethod
    def decrypt_pdf(file_id, password):
        """解密PDF"""
        filepath = get_file_path(file_id)
        
        if not os.path.exists(filepath):
            raise FileNotFoundError("PDF文件不存在")
        
        try:
            with pikepdf.open(filepath, password=password) as pdf:
                output_id = f"{file_id}_decrypted"
                output_path = get_file_path(output_id, 'processed')
                pdf.save(output_path)
            
            return {
                'output_file_id': output_id
            }
        except pikepdf.PasswordError:
            raise Exception("密码错误")
        except Exception as e:
            raise Exception(f"解密PDF失败: {str(e)}")

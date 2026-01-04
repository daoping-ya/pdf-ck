# PDF图片提取 - 完整重写版本
# 替换 pdf_service.py 中的 extract_images 方法（第81-177行）

@staticmethod
def extract_images(file_id, pages=None, export_path=None, progress_callback=None):
    """提取PDF图片并生成高清版本（600 DPI渲染）"""
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
                image_list = page.get_images(full=True)
                
                # 先渲染整页高清版本（600 DPI）备用
                zoom = 600 / 72
                mat = fitz.Matrix(zoom, zoom)
                full_page_pix = page.get_pixmap(matrix=mat)
                
                for img_index, img_info in enumerate(image_list):
                    xref = img_info[0]
                    
                    # 提取原始嵌入图片
                    try:
                        base_image = doc.extract_image(xref)
                        image_bytes = base_image["image"]
                        image_ext = base_image["ext"]
                        img_width = base_image.get("width", 0)
                        img_height = base_image.get("height", 0)
                    except:
                        continue
                    
                    base_name = os.path.splitext(os.path.basename(filepath))[0]
                    
                    # 保存原始图片
                    original_filename = f"{base_name}_p{page_num+1}_img{img_index+1}_orig.{image_ext}"
                    original_path = os.path.join(save_dir, original_filename)
                    
                    with open(original_path, "wb") as img_file:
                        img_file.write(image_bytes)
                    
                    # 生成高清PNG版本（直接使用整页渲染）
                    hq_filename = f"{base_name}_p{page_num+1}_img{img_index+1}_HQ.png"
                    hq_path = os.path.join(save_dir, hq_filename)
                    
                    # 使用已渲染的整页图片
                    full_page_pix.save(hq_path)
                    hq_size = os.path.getsize(hq_path)
                    hq_width = full_page_pix.width
                    hq_height = full_page_pix.height
                    
                    # 生成缩略图
                    thumbnail_filename = f"thumb_{original_filename}"
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
                            
                            pil_img.thumbnail((300, 300))
                            pil_img.save(thumbnail_path, "JPEG", quality=85)
                    except Exception as e:
                        print(f"生成缩略图失败: {e}")
                        thumbnail_filename = None
                    
                    # 返回数据
                    images.append({
                        'filename': original_filename,
                        'path': original_path,
                        'thumbnail': thumbnail_filename,
                        'page': page_num + 1,
                        'format': image_ext.upper(),
                        'size': len(image_bytes),
                        'width': img_width,
                        'height': img_height,
                        'quality': 'low',
                        'hq_version': {
                            'filename': hq_filename,
                            'path': hq_path,
                            'size': hq_size,
                            'width': hq_width,
                            'height': hq_height,
                            'dpi': 600,
                            'format': 'PNG'
                        }
                    })
                    image_count += 1
            
            if progress_callback:
                progress_callback(int((i + 1) / total_to_process * 100))
        
        doc.close()
        
        return {
            'total_images': image_count,
            'images': images,
            'saved_to_custom_path': saved_to_custom_path,
            'export_path': save_dir if saved_to_custom_path else None,
            'enhanced': True
        }
    except Exception as e:
        raise Exception(f"提取图片失败: {str(e)}")

"""
VPS部署兼容性测试脚本
用于验证代码修复后的功能是否正常
"""
import os
import sys
import unittest
import tempfile
import shutil

# 添加backend目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

from utils.file_handler import get_file_path
from config import Config


class TestFilePathCompatibility(unittest.TestCase):
    """测试文件路径查找兼容性"""
    
    def setUp(self):
        """测试前准备"""
        self.test_folder = tempfile.mkdtemp()
        self.original_processed = Config.PROCESSED_FOLDER
        Config.PROCESSED_FOLDER = self.test_folder
    
    def tearDown(self):
        """测试后清理"""
        Config.PROCESSED_FOLDER = self.original_processed
        if os.path.exists(self.test_folder):
            shutil.rmtree(self.test_folder)
    
    def test_find_standard_docx(self):
        """测试查找标准DOCX文件"""
        test_id = "test_standard"
        docx_path = os.path.join(self.test_folder, f"{test_id}.docx")
        
        # 创建测试文件
        with open(docx_path, 'w') as f:
            f.write("test")
        
        # 测试查找
        result = get_file_path(test_id, 'processed')
        self.assertEqual(result, docx_path)
        self.assertTrue(os.path.exists(result))
    
    def test_find_word_suffix_docx(self):
        """测试查找_word后缀的DOCX文件"""
        test_id = "test_word"
        docx_path = os.path.join(self.test_folder, f"{test_id}_word.docx")
        
        # 创建测试文件
        with open(docx_path, 'w') as f:
            f.write("test")
        
        # 测试查找
        result = get_file_path(test_id, 'processed')
        self.assertEqual(result, docx_path)
        self.assertTrue(os.path.exists(result))
    
    def test_find_pdf_fallback(self):
        """测试PDF文件兜底查找"""
        test_id = "test_pdf"
        pdf_path = os.path.join(self.test_folder, f"{test_id}.pdf")
        
        # 创建测试文件
        with open(pdf_path, 'w') as f:
            f.write("test")
        
        # 测试查找
        result = get_file_path(test_id, 'processed')
        self.assertEqual(result, pdf_path)
        self.assertTrue(os.path.exists(result))
    
    def test_priority_standard_over_word_suffix(self):
        """测试优先级: 标准DOCX > _word.docx"""
        test_id = "test_priority"
        standard_path = os.path.join(self.test_folder, f"{test_id}.docx")
        word_path = os.path.join(self.test_folder, f"{test_id}_word.docx")
        
        # 创建两个文件
        with open(standard_path, 'w') as f:
            f.write("standard")
        with open(word_path, 'w') as f:
            f.write("word_suffix")
        
        # 应该找到标准版本
        result = get_file_path(test_id, 'processed')
        self.assertEqual(result, standard_path)
    
    def test_nonexistent_file_returns_default(self):
        """测试不存在的文件返回默认PDF路径"""
        test_id = "nonexistent"
        result = get_file_path(test_id, 'processed')
        expected = os.path.join(self.test_folder, f"{test_id}.pdf")
        self.assertEqual(result, expected)


class TestDependenciesImport(unittest.TestCase):
    """测试关键依赖导入"""
    
    def test_import_flask(self):
        """测试Flask导入"""
        try:
            import flask
            self.assertIsNotNone(flask.__version__)
        except ImportError:
            self.fail("Flask导入失败")
    
    def test_import_pymupdf(self):
        """测试PyMuPDF导入"""
        try:
            import fitz
            self.assertIsNotNone(fitz.version)
        except ImportError:
            self.fail("PyMuPDF导入失败")
    
    def test_import_pdf2docx(self):
        """测试pdf2docx导入(允许失败但提示)"""
        try:
            from pdf2docx import Converter
            self.assertTrue(True)
        except ImportError:
            print("\n警告: pdf2docx未安装,Word转换功能不可用")
            print("安装命令: pip install pdf2docx")
    
    def test_import_magic(self):
        """测试python-magic导入"""
        try:
            import magic
            self.assertTrue(True)
        except ImportError:
            self.fail("python-magic导入失败。Linux请安装: apt install libmagic1 && pip install python-magic")


class TestCrossPlatformCompatibility(unittest.TestCase):
    """测试跨平台兼容性"""
    
    def test_path_handling(self):
        """测试路径处理"""
        # os.path.join应该在所有平台正常工作
        test_path = os.path.join('backend', 'uploads', 'test.pdf')
        self.assertIn('backend', test_path)
        self.assertIn('uploads', test_path)
        self.assertIn('test.pdf', test_path)
    
    def test_platform_detection(self):
        """测试平台检测"""
        import platform
        system = platform.system()
        self.assertIn(system, ['Windows', 'Linux', 'Darwin'])
        print(f"\n当前平台: {system}")


def run_diagnostics():
    """运行诊断报告"""
    import platform
    
    print("\n" + "="*60)
    print("VPS部署兼容性诊断报告")
    print("="*60)
    
    # 系统信息
    print(f"\n系统平台: {platform.system()} {platform.release()}")
    print(f"Python版本: {platform.python_version()}")
    
    # 检查关键模块
    print("\n关键模块检查:")
    modules_to_check = [
        ('flask', 'Flask'),
        ('fitz', 'PyMuPDF'),
        ('pikepdf', 'pikepdf'),
        ('PIL', 'Pillow'),
        ('magic', 'python-magic'),
        ('pdf2docx', 'pdf2docx'),
    ]
    
    for module_name, display_name in modules_to_check:
        try:
            mod = __import__(module_name)
            version = getattr(mod, '__version__', 'Unknown')
            print(f"  ✓ {display_name}: {version}")
        except ImportError:
            print(f"  ✗ {display_name}: 未安装")
    
    # 检查系统工具(Linux)
    if platform.system() == 'Linux':
        print("\n系统工具检查:")
        import subprocess
        
        tools = [
            ('pdftoppm', 'poppler-utils'),
            ('tesseract', 'tesseract-ocr'),
        ]
        
        for tool, package in tools:
            try:
                subprocess.run(['which', tool], capture_output=True, check=True)
                print(f"  ✓ {tool}: 已安装")
            except subprocess.CalledProcessError:
                print(f"  ✗ {tool}: 未安装 (运行: apt install {package})")
    
    # 检查目录权限
    print("\n目录权限检查:")
    backend_path = os.path.join(os.path.dirname(__file__), 'backend')
    upload_paths = [
        os.path.join(backend_path, 'uploads'),
        os.path.join(backend_path, 'uploads', 'temp'),
        os.path.join(backend_path, 'uploads', 'processed'),
        os.path.join(backend_path, 'data'),
    ]
    
    for path in upload_paths:
        if os.path.exists(path):
            writable = os.access(path, os.W_OK)
            status = "✓ 可写" if writable else "✗ 不可写"
            print(f"  {status}: {path}")
        else:
            print(f"  ✗ 不存在: {path}")
    
    print("\n" + "="*60)
    print("诊断完成")
    print("="*60 + "\n")


if __name__ == '__main__':
    # 先运行诊断
    run_diagnostics()
    
    # 然后运行单元测试
    print("\n开始运行单元测试...\n")
    unittest.main(verbosity=2)

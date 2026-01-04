#!/bin/bash
# VPS Linux环境一键部署脚本
# 适用于 Debian/Ubuntu 系统

set -e  # 遇到错误立即退出

echo "========================================"
echo "  PDF在线处理工具 - VPS部署脚本"
echo "========================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查是否为root用户
if [ "$EUID" -eq 0 ]; then 
    echo -e "${YELLOW}警告: 建议使用普通用户运行此脚本${NC}"
    read -p "按Enter继续,或Ctrl+C取消..."
fi

echo -e "${GREEN}[1/6] 检查系统环境${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}错误: Python3 未安装${NC}"
    echo "请先安装: sudo apt install python3 python3-pip"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "Python版本: $PYTHON_VERSION"

echo ""
echo -e "${GREEN}[2/6] 安装系统依赖${NC}"
echo "正在检查并安装必需的系统库..."

# 检查是否有sudo权限
if command -v sudo &> /dev/null; then
    SUDO="sudo"
else
    SUDO=""
fi

# 安装系统级依赖
PACKAGES_TO_INSTALL=""

# 检查libmagic1
if ! dpkg -l | grep -q libmagic1; then
    PACKAGES_TO_INSTALL="$PACKAGES_TO_INSTALL libmagic1"
fi

# 检查poppler-utils
if ! command -v pdftoppm &> /dev/null; then
    PACKAGES_TO_INSTALL="$PACKAGES_TO_INSTALL poppler-utils"
fi

# 检查OpenCV依赖
if ! ldconfig -p | grep -q libGL.so.1; then
    PACKAGES_TO_INSTALL="$PACKAGES_TO_INSTALL libgl1"
fi

if ! ldconfig -p | grep -q libglib-2.0; then
    PACKAGES_TO_INSTALL="$PACKAGES_TO_INSTALL libglib2.0-0"
fi

# 检查Python venv
if ! python3 -m venv --help &> /dev/null; then
    PACKAGES_TO_INSTALL="$PACKAGES_TO_INSTALL python${PYTHON_VERSION}-venv"
fi

if [ -n "$PACKAGES_TO_INSTALL" ]; then
    echo -e "${YELLOW}需要安装: $PACKAGES_TO_INSTALL${NC}"
    echo "运行命令: $SUDO apt update && $SUDO apt install -y $PACKAGES_TO_INSTALL"
    
    if [ -n "$SUDO" ]; then
        $SUDO apt update
        $SUDO apt install -y $PACKAGES_TO_INSTALL
    else
        echo -e "${RED}错误: 需要sudo权限安装系统依赖${NC}"
        echo "请手动运行: sudo apt install -y $PACKAGES_TO_INSTALL"
        exit 1
    fi
else
    echo -e "${GREEN}✓ 所有系统依赖已满足${NC}"
fi

echo ""
echo -e "${GREEN}[3/6] 创建Python虚拟环境${NC}"
cd backend

if [ -d "venv" ]; then
    echo -e "${YELLOW}虚拟环境已存在,跳过创建${NC}"
else
    python3 -m venv venv
    echo -e "${GREEN}✓ 虚拟环境创建成功${NC}"
fi

echo ""
echo -e "${GREEN}[4/6] 激活虚拟环境并安装Python依赖${NC}"
source venv/bin/activate

# 升级pip
pip install --upgrade pip > /dev/null

# 使用Linux专用的requirements文件
if [ -f "requirements-linux.txt" ]; then
    echo "使用Linux专用依赖文件: requirements-linux.txt"
    pip install --no-cache-dir -r requirements-linux.txt
else
    echo -e "${YELLOW}未找到requirements-linux.txt,使用主requirements.txt并修正...${NC}"
    # 创建临时文件
    sed 's/python-magic-bin/python-magic/g' requirements.txt > requirements-temp.txt
    pip install --no-cache-dir -r requirements-temp.txt
    rm requirements-temp.txt
fi

echo -e "${GREEN}✓ Python依赖安装完成${NC}"

echo ""
echo -e "${GREEN}[5/6] 验证关键库${NC}"
python3 << 'PYEOF'
import sys

errors = []

try:
    import flask
    print(f"✓ Flask {flask.__version__}")
except ImportError:
    errors.append("Flask")

try:
    import fitz
    print(f"✓ PyMuPDF (fitz) {fitz.version[0]}")
except ImportError:
    errors.append("PyMuPDF")

try:
    from pdf2docx import Converter
    import pdf2docx
    print(f"✓ pdf2docx {pdf2docx.__version__}")
except ImportError:
    errors.append("pdf2docx")

try:
    import magic
    print("✓ python-magic")
except ImportError:
    errors.append("python-magic")

if errors:
    print(f"\n❌ 以下库导入失败: {', '.join(errors)}")
    sys.exit(1)
else:
    print("\n✓ 所有关键库验证通过")
PYEOF

if [ $? -ne 0 ]; then
    echo -e "${RED}库验证失败,请检查错误信息${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}[6/6] 配置完成${NC}"

# 创建必要的目录
mkdir -p uploads/temp uploads/processed data

echo ""
echo -e "${GREEN}========================================"
echo "  部署成功!"
echo "========================================${NC}"
echo ""
echo "启动命令:"
echo -e "  ${YELLOW}cd backend && source venv/bin/activate && python app.py${NC}"
echo ""
echo "或使用nohup后台运行:"
echo -e "  ${YELLOW}cd backend && nohup venv/bin/python app.py > app.log 2>&1 &${NC}"
echo ""
echo "查看运行日志:"
echo -e "  ${YELLOW}tail -f backend/app.log${NC}"
echo ""
echo "默认访问地址: http://your-vps-ip:5000"
echo ""
echo -e "${YELLOW}提示: 建议使用Nginx反向代理并配置域名访问${NC}"

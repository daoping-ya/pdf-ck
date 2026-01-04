#!/bin/bash
#####################################
# PDF工具 - VPS首次部署脚本
# 项目路径: /root/pdf-ck
# 后端端口: 5000
# 前端端口: 8080
#####################################

set -e

echo "========================================"
echo "   PDF工具 - VPS首次部署"
echo "========================================"
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 配置变量
APP_DIR="/root/pdf-ck"
BACKEND_PORT=5000
FRONTEND_PORT=8080
PYTHON_VERSION="python3.10"

# 检查root权限
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}请使用root用户运行此脚本${NC}"
    exit 1
fi

# 1. 更新系统
echo -e "${YELLOW}[1/9] 更新系统包...${NC}"
apt update && apt upgrade -y

# 2. 安装Python和工具
echo -e "${YELLOW}[2/9] 安装Python 3.10和必要工具...${NC}"
apt install -y python3.10 python3.10-venv python3-pip git supervisor

# 3. 创建项目目录
echo -e "${YELLOW}[3/9] 创建项目目录...${NC}"
mkdir -p $APP_DIR
cd $APP_DIR

# 4. 克隆代码
echo -e "${YELLOW}[4/9] 克隆GitHub仓库...${NC}"
if [ -d ".git" ]; then
    echo "代码仓库已存在，拉取最新代码..."
    git pull origin main
else
    echo "克隆代码仓库..."
    git clone https://github.com/daoping-ya/pdf-ck.git .
fi

# 5. 创建虚拟环境
echo -e "${YELLOW}[5/9] 创建Python虚拟环境...${NC}"
if [ -d "venv" ]; then
    echo "虚拟环境已存在"
else
    $PYTHON_VERSION -m venv venv
fi

# 激活虚拟环境并安装依赖
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 确保pdf2docx版本正确
pip install pdf2docx==0.5.6

# 6. 创建必要目录
echo -e "${YELLOW}[6/9] 创建工作目录...${NC}"
mkdir -p backend/uploads/processed
mkdir -p uploads processed

# 7. 配置Supervisor（后端）
echo -e "${YELLOW}[7/9] 配置Supervisor管理后端服务...${NC}"
cat > /etc/supervisor/conf.d/pdf-tool-backend.conf <<EOF
[program:pdf-tool-backend]
directory=/root/pdf-ck/backend
command=/root/pdf-ck/venv/bin/python app.py
user=root
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/pdf-tool-backend.log
environment=PATH="/root/pdf-ck/venv/bin"
EOF

# 8. 配置Supervisor（前端）
echo -e "${YELLOW}[8/9] 配置Supervisor管理前端服务...${NC}"
cat > /etc/supervisor/conf.d/pdf-tool-frontend.conf <<EOF
[program:pdf-tool-frontend]
directory=/root/pdf-ck/frontend
command=/root/pdf-ck/venv/bin/python -m http.server $FRONTEND_PORT
user=root
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/pdf-tool-frontend.log
environment=PATH="/root/pdf-ck/venv/bin"
EOF

# 9. 启动服务
echo -e "${YELLOW}[9/9] 启动服务...${NC}"
supervisorctl reread
supervisorctl update
supervisorctl restart pdf-tool-backend
supervisorctl restart pdf-tool-frontend

# 等待服务启动
sleep 3

echo ""
echo -e "${GREEN}========================================"
echo -e "   ✓ 部署完成！"
echo -e "========================================${NC}"
echo ""
echo "服务信息:"
echo "  项目目录: $APP_DIR"
echo "  后端端口: $BACKEND_PORT"
echo "  前端端口: $FRONTEND_PORT"
echo "  Python版本: $PYTHON_VERSION"
echo ""
echo "访问地址:"
echo "  前端: http://your-server-ip:$FRONTEND_PORT"
echo "  后端API: http://your-server-ip:$BACKEND_PORT"
echo ""
echo "常用命令:"
echo "  查看后端日志: tail -f /var/log/pdf-tool-backend.log"
echo "  查看前端日志: tail -f /var/log/pdf-tool-frontend.log"
echo "  查看服务状态: supervisorctl status"
echo "  重启后端: supervisorctl restart pdf-tool-backend"
echo "  重启前端: supervisorctl restart pdf-tool-frontend"
echo ""

#!/bin/bash
#####################################
# PDF工具 - VPS一键更新脚本
# 项目路径: /root/pdf-ck
#####################################

set -e

echo "========================================"
echo "   PDF工具 - VPS一键更新"
echo "========================================"
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

APP_DIR="/root/pdf-ck"

cd $APP_DIR

# 1. 备份当前版本
echo -e "${YELLOW}[1/6] 备份当前版本...${NC}"
BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p ../backups
cp -r backend/uploads ../backups/$BACKUP_DIR/ 2>/dev/null || true
echo "数据已备份到: ../backups/$BACKUP_DIR"

# 2. 拉取最新代码
echo -e "${YELLOW}[2/6] 拉取最新代码...${NC}"
git fetch origin
git pull origin main

# 3. 激活虚拟环境
echo -e "${YELLOW}[3/6] 更新Python依赖...${NC}"
source venv/bin/activate

# 4. 更新依赖
pip install -r requirements.txt --upgrade
pip install pdf2docx==0.5.6  # 确保关键依赖版本正确

# 5. 清理缓存
echo -e "${YELLOW}[4/6] 清理Python缓存...${NC}"
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

# 6. 重启服务
echo -e "${YELLOW}[5/6] 重启服务...${NC}"
supervisorctl restart pdf-tool-backend
supervisorctl restart pdf-tool-frontend

# 等待服务启动
sleep 2

# 7. 检查服务状态
echo -e "${YELLOW}[6/6] 检查服务状态...${NC}"
echo ""
supervisorctl status

echo ""
echo -e "${GREEN}========================================"
echo -e "   ✓ 更新完成！"
echo -e "========================================${NC}"
echo ""
echo "查看日志:"
echo "  后端: tail -f /var/log/pdf-tool-backend.log"
echo "  前端: tail -f /var/log/pdf-tool-frontend.log"
echo ""

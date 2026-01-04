# VPS Linux部署指南

## 快速部署

### 方法1: 使用一键脚本 (推荐)

```bash
# 1. 上传项目到VPS
# 2. 赋予执行权限
chmod +x deploy_vps.sh

# 3. 运行部署脚本
./deploy_vps.sh

# 4. 启动应用
cd backend
source venv/bin/activate
python app.py
```

### 方法2: 手动部署

#### 步骤1: 安装系统依赖

```bash
# Debian/Ubuntu
sudo apt update
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    libmagic1 \
    poppler-utils \
    libgl1 \
    libglib2.0-0
```

#### 步骤2: 配置Python环境

```bash
cd backend

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 升级pip
pip install --upgrade pip

# 安装依赖(使用Linux专用配置)
pip install --no-cache-dir -r requirements-linux.txt
```

> **说明**: 
> - `requirements.txt` - Windows环境使用(包含`python-magic-bin`)
> - `requirements-linux.txt` - Linux环境使用(包含`python-magic`)
> - 部署脚本会自动选择正确的文件

#### 步骤3: 启动应用

```bash
# 前台运行(测试用)
python app.py

# 后台运行
nohup python app.py > app.log 2>&1 &

# 查看日志
tail -f app.log
```

---

## 生产环境配置

### 使用Systemd管理服务

创建服务文件 `/etc/systemd/system/pdf-processor.service`:

```ini
[Unit]
Description=PDF在线处理工具
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/your/project/backend
Environment="PATH=/path/to/your/project/backend/venv/bin"
ExecStart=/path/to/your/project/backend/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务:

```bash
sudo systemctl daemon-reload
sudo systemctl enable pdf-processor
sudo systemctl start pdf-processor
sudo systemctl status pdf-processor
```

### 使用Nginx反向代理

创建Nginx配置 `/etc/nginx/sites-available/pdf-processor`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 增加超时时间(Word转换可能需要时间)
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
    }
}
```

启用配置:

```bash
sudo ln -s /etc/nginx/sites-available/pdf-processor /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 配置HTTPS (可选)

使用Let's Encrypt免费证书:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## 故障排查

### 问题1: 导入错误 - No module named 'magic'

**原因**: Linux系统未安装libmagic或使用了错误的Python包

**解决**:
```bash
# 安装系统库
sudo apt install libmagic1

# 确保使用正确的Python包(不是-bin版本)
pip uninstall python-magic-bin
pip install python-magic
```

### 问题2: PDF转Word失败 - 找不到poppler

**原因**: 缺少poppler-utils系统工具

**解决**:
```bash
sudo apt install poppler-utils

# 验证安装
pdftoppm -v
```

### 问题3: OpenCV错误 - libGL.so.1找不到

**原因**: 缺少OpenGL库

**解决**:
```bash
sudo apt install libgl1 libglib2.0-0
```

### 问题4: Word文件下载404

**原因**: 文件路径查找失败

**检查**:
```bash
# 查看processed目录
ls -la backend/uploads/processed/

# 查看应用日志
tail -f backend/app.log

# 应该看到类似输出:
# [下载成功] file_id=xxx_word, filepath=/path/to/xxx_word.docx, download_name=xxx.docx
```

如果看到`[下载错误] 文件不存在`,说明文件未正确生成,检查转换过程日志。

### 问题5: 权限错误

**原因**: uploads目录权限不足

**解决**:
```bash
# 设置正确的目录权限
chmod 755 backend/uploads
chmod 755 backend/uploads/temp
chmod 755 backend/uploads/processed

# 如果使用www-data用户运行
sudo chown -R www-data:www-data backend/uploads
```

---

## 性能优化

### 内存优化

编辑 `backend/config.py`:

```python
MAX_WORKERS = 1  # VPS内存小于2GB建议设为1
MAX_CONTENT_LENGTH = 20 * 1024 * 1024  # 限制文件大小
```

### 磁盘空间管理

```python
FILE_MAX_AGE_MINUTES = 15  # 降低文件保留时间
CLEANUP_INTERVAL_MINUTES = 10  # 增加清理频率
```

手动清理:

```bash
# 通过API清理
curl http://localhost:5000/api/cleanup

# 或直接删除旧文件
find backend/uploads -type f -mmin +30 -delete
```

---

## 安全建议

1. **修改默认端口**
   ```python
   # config.py
   PORT = 8888  # 改为非标准端口
   ```

2. **配置防火墙**
   ```bash
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```

3. **限制文件类型**
   ```python
   # config.py
   ALLOWED_EXTENSIONS = {'pdf'}  # 仅允许PDF
   ```

4. **启用日志**
   ```python
   import logging
   logging.basicConfig(
       level=logging.INFO,
       format='%(asctime)s - %(levelname)s - %(message)s',
       filename='app.log'
   )
   ```

---

## 监控与维护

### 监控磁盘空间

```bash
# 添加到crontab
0 * * * * df -h | grep /dev/vda1 | awk '{if($5+0 > 80) print "Disk usage warning: " $5}'
```

### 自动重启脚本

创建 `check_and_restart.sh`:

```bash
#!/bin/bash
if ! pgrep -f "python app.py" > /dev/null; then
    echo "$(date): App not running, restarting..."
    cd /path/to/backend
    source venv/bin/activate
    nohup python app.py > app.log 2>&1 &
fi
```

添加到crontab:
```bash
*/5 * * * * /path/to/check_and_restart.sh
```

---

## 更新部署

```bash
# 1. 停止服务
sudo systemctl stop pdf-processor

# 2. 拉取新代码
git pull

# 3. 更新依赖
cd backend
source venv/bin/activate
pip install --no-cache-dir -r requirements.txt

# 4. 重启服务
sudo systemctl start pdf-processor
```

---

## 联系支持

如遇到问题:
1. 查看日志: `tail -f backend/app.log`
2. 检查系统日志: `sudo journalctl -u pdf-processor -f`
3. 运行诊断: `./deploy_vps.sh` 会显示详细检查信息

# PDF在线处理工具

一个轻量级的PDF在线处理工具,专为资源受限的VPS环境优化(1.5GB RAM, 7GB磁盘)。

## 平台支持

✅ **Windows** - 完全支持,开箱即用  
✅ **Linux (Debian/Ubuntu)** - VPS部署优化  
✅ **Docker** - 容器化部署

## 快速选择部署方式

- **Windows本地开发**: 参考下方[快速开始](#快速开始)
- **Linux VPS部署**: 查看 [VPS_DEPLOY.md](VPS_DEPLOY.md) 📖
- **Docker容器部署**: 查看 [CONTAINER_DEPLOY.md](CONTAINER_DEPLOY.md) 🐳

## 功能特性

✅ **文件上传** - 支持拖拽上传,最大20MB
✅ **实时预览** - PDF页面在线预览
✅ **文字提取** - 提取PDF文字内容
✅ **图片提取** - 提取PDF中的图片
✅ **页面旋转** - 旋转指定页面
✅ **PDF加密** - 密码保护PDF文件
✅ **PDF解密** - 解密受保护的PDF
✅ **自动清理** - 30分钟自动删除临时文件

## 技术栈

### 后端
- **Flask** - Web框架
- **PyMuPDF (fitz)** - PDF处理
- **pikepdf** - PDF加解密
- **ThreadPoolExecutor** - 异步任务处理
- **SQLite** - 任务状态存储

### 前端
- **原生HTML/CSS/JavaScript** - 无框架依赖
- **现代暗黑主题** - 渐变、动画、响应式

## 快速开始

### 1. 环境要求

- Python 3.8+
- 系统: Ubuntu/Debian/Windows
- 内存: 至少1.5GB
- 磁盘: 至少7GB

### 2. 安装依赖

```bash
# 进入后端目录
cd backend

# 创建虚拟环境(推荐)
python -m venv venv

# Windows激活
venv\Scripts\activate

# Linux激活
source venv/bin/activate

# 安装依赖(使用--no-cache-dir节省磁盘)
pip install --no-cache-dir -r requirements.txt
```

### 3. 配置端口

```bash
# 方法1: 环境变量
set PDF_PROCESSOR_PORT=9527  # Windows
export PDF_PROCESSOR_PORT=9527  # Linux

# 方法2: 修改config.py
# 修改 PORT 的默认值
```

### 4. 启动应用

```bash
python app.py
```

应用将启动在配置的端口(默认5000)。

### 5. 访问应用

打开浏览器访问: `http://localhost:5000` (或您配置的端口)

## 配置说明

编辑 `backend/config.py` 可调整以下参数:

```python
# 端口配置
PORT = 5000  # 修改为您的端口

# 资源限制
MAX_WORKERS = 1  # 并发任务数(1.5GB内存建议保持1)
MAX_CONTENT_LENGTH = 20 * 1024 * 1024  # 文件大小限制

# 功能开关
ENABLE_OCR = False  # OCR功能(消耗大量内存,建议关闭)

# 清理策略
CLEANUP_INTERVAL_MINUTES = 30  # 清理间隔
FILE_MAX_AGE_MINUTES = 30  # 文件过期时间
```

## API接口

### 上传PDF
```http
POST /api/upload
Content-Type: multipart/form-data
Body: file=<pdf文件>
```

### 提取文字
```http
POST /api/extract-text
Content-Type: application/json
Body: {"file_id": "xxx", "pages": []}
```

### 提取图片
```http
POST /api/extract-images
Content-Type: application/json
Body: {"file_id": "xxx", "pages": []}
```

### 旋转页面
```http
POST /api/rotate-pages
Content-Type: application/json
Body: {"file_id": "xxx", "rotations": {"1": 90}}
```

### 加密PDF
```http
POST /api/encrypt
Content-Type: application/json
Body: {"file_id": "xxx", "user_password": "pass"}
```

### 查询任务状态
```http
GET /api/task-status/{task_id}
```

更多接口请参考 `backend/app.py`

## VPS部署

### Ubuntu/Debian系统

```bash
# 1. 安装系统依赖
sudo apt update
sudo apt install -y python3 python3-pip python3-venv poppler-utils

# 2. 克隆代码到VPS
# (上传代码或git clone)

# 3. 配置端口
export PDF_PROCESSOR_PORT=9527

# 4. 使用systemd管理服务
sudo nano /etc/systemd/system/pdf-processor.service
```

**systemd配置:**
```ini
[Unit]
Description=PDF Processor
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/backend
Environment="PATH=/path/to/backend/venv/bin"
Environment="PDF_PROCESSOR_PORT=9527"
ExecStart=/path/to/backend/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# 启动服务
sudo systemctl daemon-reload
sudo systemctl enable pdf-processor
sudo systemctl start pdf-processor
```

## 故障排查

### 端口被占用
```bash
# Windows
netstat -ano | findstr :5000

# Linux
lsof -i :5000
```

### 内存不足
- 降低 `MAX_WORKERS` 到 1
- 减小 `MAX_CONTENT_LENGTH`
- 禁用 `ENABLE_OCR`

### 磁盘空间不足
- 缩短 `FILE_MAX_AGE_MINUTES` 到 15 分钟
- 手动清理: `GET /api/cleanup`

## 许可证

MIT License

## 更新日志

### v1.1.0 - VPS兼容性优化 (2026-01-04)

**核心修复**:
- ✅ 修复Linux VPS环境Word文件下载404问题
- ✅ 智能文件路径查找,支持`_word.docx`后缀
- ✅ 移除pdf2docx版本强校验,兼容更多版本
- ✅ 依赖包跨平台适配(`python-magic` vs `python-magic-bin`)

**新增功能**:
- 📝 Linux VPS一键部署脚本 (`deploy_vps.sh`)
- 📚 详细VPS部署文档 (`VPS_DEPLOY.md`)
- 🧪 兼容性测试工具 (`test_vps_compatibility.py`)
- 📊 增强日志输出,便于问题诊断

**技术改进**:
- 优化文件查找优先级: `.docx` → `_word.docx` → `.pdf`
- 自动清理下载文件名中的`_word`后缀
- 跨平台路径处理增强

查看详细修复: [implementation_plan.md](.gemini/antigravity/brain/367f9962-e4ba-415a-8074-d0a14bc36ffc/implementation_plan.md)

### v1.0.0 - 初始版本

基础PDF处理功能发布

---

## 作者

Created for resource-constrained VPS environments.

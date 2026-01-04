# 快速启动指南

## 问题已修复 ✅

已修复 `requirements.txt` 的编码问题(移除了中文注释)。

## 三种启动方式

### 方式 1: 完整自动启动(首次推荐) 

**双击运行:** `start.bat`

这个脚本会自动:
1. 创建虚拟环境
2. 激活虚拟环境
3. 安装依赖包
4. 启动服务器(端口9527)

**全自动,无需手动操作!**

---

### 方式 2: 快速启动(已安装依赖后)

**双击运行:** `run.bat`

适用于已经运行过一次的情况,直接启动服务器。

---

### 方式 3: 手动启动(更多控制)

```powershell
# 1. 进入后端目录
cd f:\myjob\backend

# 2. 激活虚拟环境
venv\Scripts\activate

# 3. 设置端口(可选)
set PDF_PROCESSOR_PORT=9527

# 4. 启动
python app.py
```

---

## 修改端口

**双击运行:** `config_port.bat`

或直接编辑 `backend\config.py`,找到这一行:
```python
PORT = int(os.environ.get('PDF_PROCESSOR_PORT', 5000))
```
将 `5000` 改为您需要的端口号。

---

## 访问应用

启动成功后,打开浏览器访问:

**http://localhost:9527**

(或您配置的端口号)

---

## 常见问题

### Q: 提示 "Python不是内部或外部命令"
**A:** 需要先安装Python 3.8+,并添加到PATH
下载: https://www.python.org/downloads/

### Q: pip 安装很慢
**A:** 使用国内镜像:
```bash
pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
```

### Q: 端口被占用
**A:** 运行 `config_port.bat` 修改端口,或:
```powershell
# 查看占用
netstat -ano | findstr :9527
```

### Q: 内存不足
**A:** 编辑 `backend\config.py`:
- 减小 `MAX_CONTENT_LENGTH` 到 10MB
- 确保 `MAX_WORKERS = 1`

---

## 停止服务器

在运行窗口按 `Ctrl + C`

---

## 文件说明

- `start.bat` - 完整启动脚本(首次使用)
- `run.bat` - 快速启动脚本(后续使用)
- `config_port.bat` - 端口配置工具
- `backend/` - 后端代码
- `frontend/` - 前端代码

---

## 需要帮助?

查看 `README.md` 了解更多详情。

# 🚀 部署与启动指南

本指南将帮助您从零开始部署并启动 PDF 在线处理工具。

## 1. 环境准备

确保您的系统已安装以下软件：
*   **Python 3.8 或更高版本**: [下载地址](https://www.python.org/downloads/)
    *   *注意*: 安装时请务必勾选 **"Add Python to PATH"**。

## 2. 自动部署与启动 (推荐)

我们提供了自动脚本，可以一键完成环境配置和启动。

1.  进入项目目录 (例如 `F:\myjob`)。
2.  双击运行 **`start_app.bat`** (如果不存在，请运行 `debug.bat` 进行修复和启动)。
    *   脚本会自动创建虚拟环境。
    *   自动安装所有依赖包。
    *   启动服务器并自动打开浏览器。

## 3. 手动部署步骤

如果您更喜欢手动操作，请按照以下步骤进行：

### 3.1 创建虚拟环境

打开 PowerShell 或 CMD，进入项目后端目录：

```powershell
cd f:\myjob\backend
python -m venv venv
```

### 3.2 激活虚拟环境

```powershell
# Windows
venv\Scripts\activate
```

### 3.3 安装依赖

```powershell
pip install -r requirements.txt
```

### 3.4 启动服务

```powershell
python app.py
```

启动成功后，访问浏览器: `http://127.0.0.1:5000`

---

# 🔧 启动问题排查指南

## 问题: bat启动后瞬间消失

这说明脚本遇到了错误并退出了。已创建调试工具帮您定位问题。

---

## 🔍 排查步骤

### 步骤 1: 运行调试脚本

**双击运行:** `debug.bat`

这会逐步检查:
1. ✅ Python是否安装
2. ✅ 虚拟环境是否创建
3. ✅ 依赖是否安装
4. ✅ 导入是否成功
5. ✅ 服务器启动

**如果某一步失败,会显示具体错误信息**

---

### 步骤 2: 测试Python导入

**双击运行:** `test_imports.bat`

检查核心库是否正确安装。

---

### 步骤 3: 手动启动(查看详细错误)

```powershell
# 1. 打开PowerShell或CMD
# 2. 进入项目目录
cd f:\myjob\backend

# 3. 激活虚拟环境
venv\Scripts\activate

# 4. 启动应用
python app.py
```

**这样可以看到完整的错误信息!**

---

## 常见问题及解决方案

### ❌ 问题 1: "Python不是内部或外部命令"

**原因:** 未安装Python或未添加到PATH

**解决:**
1. 下载Python 3.8+: https://www.python.org/downloads/
2. 安装时勾选 "Add Python to PATH"
3. 重启电脑
4. 重新运行 `debug.bat`

---

### ❌ 问题 2: "No module named 'flask'"

**原因:** 依赖未安装

**解决:**
```powershell
cd f:\myjob\backend
venv\Scripts\activate
pip install --no-cache-dir -r requirements.txt
```

或手动安装核心包:
```powershell
pip install Flask PyMuPDF pikepdf Pillow APScheduler psutil
```

---

### ❌ 问题 3: "ImportError: DLL load failed"

**原因:** Windows缺少C++运行库

**解决:**
下载安装: https://aka.ms/vs/17/release/vc_redist.x64.exe

---

### ❌ 问题 4: "Address already in use" (端口被占用)

**原因:** 端口5000已被其他程序使用

**解决方案 A - 更换端口:**
```powershell
# 编辑 backend\config.py
# 找到: PORT = int(os.environ.get('PDF_PROCESSOR_PORT', 5000))
# 改为: PORT = int(os.environ.get('PDF_PROCESSOR_PORT', 8888))
```

**解决方案 B - 查找占用进程:**
```powershell
netstat -ano | findstr :5000
# 记下最后一列的PID
taskkill /PID <PID号> /F
```

---

### ❌ 问题 5: 浏览器打不开

**可能原因:**
1. 服务器未启动成功
2. 端口不对
3. 防火墙阻止

**检查:**
1. 确认命令行窗口显示 "Running on http://..."
2. 尝试访问: http://127.0.0.1:5000
3. 检查防火墙设置

---

## ✅ 成功启动的标志

命令行窗口应该显示:

```
=== PDF在线处理工具 ===
端口: 5000
内存限制: 20.0MB
并发任务数: 1
OCR功能: 关闭
文件清理周期: 30分钟
========================
 * Serving Flask app 'app'
 * Debug mode: off
 * Running on http://0.0.0.0:5000
```

**看到这些信息说明成功了!**

---

## 🆘 需要进一步帮助

如果以上方法都不行,请:

1. 运行 `debug.bat`
2. 截图所有错误信息
3. 或手动运行并复制错误内容

具体错误信息能帮助快速定位问题!

---

## 快速命令参考

```powershell
# 检查Python
python --version

# 检查pip
pip --version

# 安装依赖
pip install Flask PyMuPDF pikepdf Pillow

# 查看已安装包
pip list

# 查看端口占用
netstat -ano | findstr :5000

# 启动服务器
cd f:\myjob\backend
venv\Scripts\activate
python app.py
```

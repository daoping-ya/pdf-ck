# 启动说明

## Windows系统快速启动

1. 确保已安装Python 3.8+
2. 打开命令提示符或PowerShell,进入backend目录
3. 执行以下命令:

```powershell
# 创建虚拟环境(首次运行)
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate

# 安装依赖(首次运行)
pip install --no-cache-dir -r requirements.txt

# 设置端口(可选,默认5000)
set PDF_PROCESSOR_PORT=9527

# 启动应用
python app.py
```

4. 打开浏览器访问 http://localhost:9527 (或您设置的端口)

## Linux系统快速启动

```bash
# 创建虚拟环境(首次运行)
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖(首次运行)
pip install --no-cache-dir -r requirements.txt

# 设置端口(可选,默认5000)
export PDF_PROCESSOR_PORT=9527

# 启动应用
python app.py
```

## 注意事项

- 首次启动需要下载安装依赖包,需要一定时间
- **Windows系统**需要额外安装 poppler-utils 才能使用pdf2image功能
  - 下载地址: https://github.com/oschwartz10612/poppler-windows/releases/
  - 解压后将bin目录添加到系统PATH
- 确保防火墙允许您设置的端口访问
- 极限配置(1.5GB内存)建议不要同时处理过大的PDF

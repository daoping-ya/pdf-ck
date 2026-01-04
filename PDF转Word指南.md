# PDF转Word功能使用指南

## 当前问题

您点击"导出Word"后提示"无法从站点上载文件"，这是因为pdf2docx库还未安装。

## 解决方法

### 快速安装(推荐)

**双击运行:** `install_pdf2word.bat`

### 手动安装

打开命令行:

```bash
cd f:\myjob\backend
venv\Scripts\activate
pip install --no-cache-dir pdf2docx==0.5.6
```

### 验证安装

```bash
pip show pdf2docx
```

应该看到:
```
Name: pdf2docx
Version: 0.5.6
```

## 安装后操作

1. **重启服务器** (重要!)
   - 在运行窗口按 `Ctrl+C`
   - 重新运行 `start.bat`

2. **重新上传PDF并点击"📄 导出Word"**

## 注意事项

- pdf2docx依赖较大,首次安装需要2-3分钟
- 安装后务必重启服务器才能生效
- 转换大文件可能需要等待30秒-2分钟

## 如果仍然失败

请截图错误信息,我会进一步排查问题。

常见错误:
- "No module named 'pdf2docx'" → 未安装或未重启
- "转换失败" → PDF可能已加密或损坏
- "下载失败" → 检查磁盘空间

## 替代方案

如果pdf2docx无法安装,可以使用:
1. **提取文字(增强)** - 保留格式的HTML输出
2. **提取表格** - 提取表格数据
3. 在线转换工具(第三方)

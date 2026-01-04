# PDF在线处理工具 - 项目结构

## 已创建的文件列表

```
f:\myjob/
├── README.md                    # 项目说明文档
├── START.md                     # 快速启动指南
├── backend/                     # 后端代码
│   ├── app.py                   # Flask主应用(API接口)
│   ├── config.py                # 配置文件(端口、资源限制等)
│   ├── task_manager.py          # 异步任务管理器(ThreadPool+SQLite)
│   ├── requirements.txt         # Python依赖列表
│   ├── tasks/                   # 任务模块
│   │   ├── __init__.py
│   │   └── pdf_tasks.py         # PDF处理任务函数
│   ├── services/                # 业务服务
│   │   ├── __init__.py
│   │   └── pdf_service.py       # PDF核心处理服务
│   ├── utils/                   # 工具函数
│   │   ├── __init__.py
│   │   └── file_handler.py      # 文件管理工具
│   ├── uploads/                 # 临时文件目录
│   │   ├── temp/                # 上传的PDF
│   │   └── processed/           # 处理后的PDF
│   └── data/                    # 数据目录
│       └── tasks.db             # SQLite数据库(运行时创建)
└── frontend/                    # 前端代码
    ├── index.html               # 主页面
    ├── css/
    │   └── style.css            # 现代暗黑主题样式
    ├── js/
    │   ├── api.js               # API接口封装
    │   └── app.js               # 主应用逻辑
    └── assets/                  # 静态资源(可选)
```

## 核心文件说明

### 后端

**app.py** - Flask主应用
- 提供10+个RESTful API接口
- 文件上传、PDF处理、任务查询、文件下载
- 定时清理任务(30分钟)
- 健康检查接口

**config.py** - 配置管理
- 端口配置(支持环境变量)
- 资源限制(单worker,20MB文件)
- 功能开关(OCR禁用)
- 路径和清理策略

**task_manager.py** - 任务管理器
- ThreadPoolExecutor异步执行
- SQLite状态存储
- 并发控制和进度追踪
- 自动清理旧任务

**pdf_service.py** - PDF处理核心
- 元数据提取
- 文字/图片提取
- 页面预览渲染
- 页面删除/旋转/合并
- PDF加解密

**file_handler.py** - 文件管理
- 文件验证(魔数校验)
- 上传保存
- 自动清理过期文件
- 磁盘使用监控

### 前端

**index.html** - 主页面
- 响应式单页应用
- 拖拽上传区
- 工具栏和预览窗口
- 进度提示和Toast通知

**style.css** - 样式
- 现代暗黑主题
- 渐变色和动画
- 响应式布局
- 自定义滚动条

**api.js** - API封装
- 所有后端接口调用
- 任务状态轮询
- 统一错误处理

**app.js** - 应用逻辑
- 文件上传处理
- PDF预览翻页
- 工具操作(提取、旋转、加解密)
- UI状态管理

## 技术亮点

### 1. 极限资源优化
- 单worker避免内存溢出
- ThreadPool替代Celery(节省Redis)
- SQLite替代独立数据库
- --no-cache-dir安装节省磁盘

### 2. 端口灵活配置
- 环境变量: `PDF_PROCESSOR_PORT=9527`
- config.py默认值
- systemd服务配置

### 3. 自动清理机制
- 30分钟定时清理
- 下载后即删选项
- 任务记录3小时后清除
- 磁盘使用监控

### 4. 现代前端设计
- 暗黑主题+渐变色
- 拖拽上传+实时预览
- 进度提示+Toast通知
- 完全响应式

## 下一步

### 测试
1. 启动后端: `cd backend && python app.py`
2. 访问前端: `http://localhost:5000`
3. 测试各功能模块

### 部署
参考 `C:\Users\Administrator\.gemini\antigravity\brain\...\deployment_guide.md`

### 扩展功能(可选)
- 水印去除(需要pikepdf高级API)
- OCR支持(需要Tesseract,消耗内存)
- 排版复刻(需要pdfplumber,消耗资源)
- 批量处理(需要增加worker数)

## 已知限制

- 文件大小≤20MB
- 页数建议≤30页
- 单任务模式(无并发)
- OCR功能禁用
- 排版复刻禁用

根据VPS实际性能可在`config.py`中调整。

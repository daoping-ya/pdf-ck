# 🐳 容器化部署指南

本指南将指导您如何将 PDF 处理工具部署到 GitHub，构建 Docker 镜像，并在其他容器环境（如 Docker, Kubernetes, 或云平台容器服务）中运行。

## 1. 推送到 GitHub

您可以选择使用 **命令行 (推荐)** 或 **网页上传 (简单)** 两种方式。

### 方式 A: 网页直接上传 (最简单)

如果您不熟悉 Git 命令，可以直接在 GitHub 网站操作：

1.  **创建仓库**:
    *   登录 [GitHub](https://github.com)。
    *   点击右上角的 "+" -> "New repository"。
    *   输入仓库名称 (例如 `pdf-processor`)，点击 "Create repository"。

2.  **上传文件**:
    *   在仓库页面，点击链接 **"uploading an existing file"**。
    *   直接将您电脑上的项目文件夹中的所有文件（`backend`, `frontend`, `Dockerfile` 等）拖拽到网页中。
    *   *注意*: 网页上传不支持空文件夹，但我们的代码不依赖空文件夹，直接拖拽即可。
    *   在底部 "Commit changes" 处点击绿色按钮提交。

### 方式 B: 命令行上传 (标准)

如果您熟悉 Git，可以使用以下命令：

1.  **初始化 Git 仓库**:
    ```bash
    git init
    git add .
    git commit -m "Initial commit"
    ```

2.  **推送到远程仓库**:
    ```bash
    # 将 <YOUR_USERNAME> 替换为您的 GitHub 用户名
    git remote add origin https://github.com/<YOUR_USERNAME>/pdf-processor.git
    git branch -M main
    git push -u origin main
    ```

## 2. 构建 Docker 镜像

您可以在本地构建镜像，也可以使用 GitHub Actions 自动构建（进阶）。这里介绍通用的手动构建方法。

### 2.1 本地构建

确保您已安装 [Docker Desktop](https://www.docker.com/products/docker-desktop/)。

```bash
# 构建镜像 (注意最后的点 .)
# 将 <your-dockerhub-username> 替换为您的 Docker Hub 用户名
docker build -t <your-dockerhub-username>/pdf-processor:latest .
```

### 2.2 测试镜像

构建完成后，在本地运行测试：

```bash
docker run -p 5000:5000 <your-dockerhub-username>/pdf-processor:latest
```

访问 `http://localhost:5000` 确认服务正常运行。

## 3. 推送到 Docker Hub

为了在其他机器上运行，您需要将镜像推送到镜像仓库（如 Docker Hub）。

1.  **登录 Docker Hub**:
    ```bash
    docker login
    ```

2.  **推送镜像**:
    ```bash
    docker push <your-dockerhub-username>/pdf-processor:latest
    ```

## 4. 在其他容器环境部署

现在，您可以在任何支持 Docker 的机器上运行该应用。

### 方式 A: 使用 Docker Compose (推荐 - 最简单)

我们已经为您准备了 `docker-compose.yml` 文件，这使得部署变得非常简单。

1.  **在目标机器上下载代码**:
    ```bash
    # 将 <YOUR_USERNAME> 替换为您的 GitHub 用户名
    git clone https://github.com/<YOUR_USERNAME>/pdf-processor.git
    cd pdf-processor
    ```

2.  **一键启动**:
    ```bash
    docker-compose up -d
    ```
    *   `-d`: 后台运行
    *   命令会自动构建镜像并启动服务。
    *   数据会自动保存在 `backend/data` 和 `backend/uploads` 目录中。

### 方式 B: 手动构建与运行 (传统方式)

如果您不使用 Docker Compose，可以手动操作：

1.  **拉取镜像**:
    ```bash
    docker pull <your-dockerhub-username>/pdf-processor:latest
    ```

2.  **运行容器**:
    ```bash
    docker run -d \
      --name pdf-processor \
      -p 5000:5000 \
      --restart always \
      -v pdf_data:/app/backend/data \
      -v pdf_uploads:/app/backend/uploads \
      <your-dockerhub-username>/pdf-processor:latest
    ```

## 5. 常见问题

*   **端口冲突**: 如果 5000 端口被占用，可以修改映射端口，例如 `-p 8080:5000`，然后通过 8080 访问。
*   **内存限制**: PDF 处理可能消耗较多内存。如果容器崩溃，尝试增加 Docker 分配的内存资源。

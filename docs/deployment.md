# SkyrisReward Docker 部署文档

本文档详细说明了如何使用 Docker 和 Docker Compose 部署 SkyrisReward 后端服务。

## 1. 环境要求

在开始部署之前，请确保服务器满足以下要求：

*   **操作系统**: Linux (推荐 Ubuntu 20.04/22.04), macOS, 或 Windows (WSL2)
*   **Docker**: 版本 20.10.0 或更高
*   **Docker Compose**: 版本 2.0.0 或更高
*   **Git**: 用于拉取代码

## 2. 项目结构

与部署相关的文件结构如下：

```text
SkyrisReward/
├── docker/
│   ├── Dockerfile              # 后端镜像构建文件
│   └── docker-compose.yml      # 容器编排配置
├── scripts/
│   └── deploy.sh               # 自动化部署脚本
├── .env                        # 环境变量配置文件
└── requirements.txt            # Python 依赖列表
```

## 3. 配置说明

### 环境变量 (.env)

在部署前，请确保项目根目录下存在 `.env` 文件。你可以复制 `.env.example` (如果有) 或手动创建。

关键配置项：

```ini
# Database
MYSQL_ROOT_PASSWORD=rootpass
MYSQL_DATABASE=reward_db
MYSQL_USER=reward_user
MYSQL_PASSWORD=reward_pass
MYSQL_HOST=db           # 在 Docker 网络中，使用服务名 'db'
MYSQL_PORT=3306

# App
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**注意**: `docker-compose.yml` 会自动加载根目录下的 `.env` 文件。

## 4. 快速部署 (推荐)

我们提供了一个自动化脚本 `scripts/deploy.sh`，它可以自动拉取最新代码、构建镜像并重启服务。

### 运行部署脚本

```bash
# 赋予脚本执行权限 (仅需一次)
chmod +x scripts/deploy.sh

# 运行脚本
./scripts/deploy.sh
```

脚本执行流程：
1.  拉取 Git 仓库最新代码。
2.  使用 `docker-compose` 构建并启动容器。
3.  自动清理旧的无用镜像。

## 5. 手动部署

如果你希望手动控制部署过程，可以使用以下 Docker Compose 命令。

### 启动服务

```bash
# 构建并后台启动所有服务
docker-compose -f docker/docker-compose.yml up -d --build
```

### 查看日志

```bash
# 查看所有服务日志
docker-compose -f docker/docker-compose.yml logs -f

# 查看特定服务日志 (如 backend)
docker-compose -f docker/docker-compose.yml logs -f backend
```

### 停止服务

```bash
# 停止并移除容器
docker-compose -f docker/docker-compose.yml down
```

## 6. 服务访问

部署成功后，服务将通过以下端口暴露：

*   **后端 API**: `http://localhost:8000` (或服务器 IP:8000)
*   **API 文档**: `http://localhost:8000/docs`
*   **MySQL 数据库**: `localhost:3307` (映射到了宿主机的 3307 端口以避免冲突)

## 7. 常见问题 (FAQ)

### Q1: 端口冲突 (Port already allocated)
**现象**: 启动时提示 `Bind for 0.0.0.0:3306 failed: port is already allocated`。
**解决**: 默认配置中，MySQL 映射到了宿主机的 `3307` 端口。如果仍然冲突，请修改 `docker/docker-compose.yml` 中的 `ports` 映射部分。

### Q2: 数据库连接失败
**现象**: 后端报错 `Can't connect to MySQL server on 'db'`.
**解决**:
1.  确保 `.env` 中的 `MYSQL_HOST` 设置为 `db` (Docker 服务名)，而不是 `localhost` 或 `127.0.0.1`。
2.  等待数据库完全启动（首次启动可能需要几秒钟初始化）。

### Q3: 权限问题
**现象**: `deploy.sh` 提示 `Permission denied`。
**解决**: 运行 `chmod +x scripts/deploy.sh`。

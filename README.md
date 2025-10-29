```markdown
# 悬赏任务接取面板后端服务

## 项目简介
本项目为悬赏任务接取面板的后端服务，基于 Python FastAPI 框架开发，主要负责任务管理、用户系统、消息通知、奖励结算、管理后台等核心业务逻辑。数据存储采用 MySQL，支持 OAuth2 认证，具备良好的扩展性和安全性。

## 技术栈
- 后端框架：FastAPI
- 数据库：MySQL
- 认证方案：OAuth2
- 其他组件：Redis、消息队列
- 部署与运维：Docker、GitHub Actions、主流云平台

## 主要功能
- 任务发布、浏览、接取与提交
- 用户注册、登录、个人中心
- 消息通知与任务状态变更
- 奖励发放与结算记录
- 管理后台（任务审核、用户管理、数据统计）
- 安全与风控（防刷机制、举报申诉）

## 目录结构
backend/
├── app/
│   ├── main.py                # FastAPI 应用入口
│   ├── api/                   # 路由与接口模块
│   │   ├── __init__.py
│   │   ├── tasks.py           # 任务相关接口
│   │   ├── users.py           # 用户相关接口
│   │   ├── auth.py            # 认证相关接口
│   │   ├── admin.py           # 管理后台接口
│   │   └── notifications.py   # 消息通知接口
│   ├── models/                # ORM模型定义
│   │   ├── __init__.py
│   │   ├── task.py
│   │   ├── user.py
│   │   ├── reward.py
│   │   └── ...                # 其他模型
│   ├── schemas/               # Pydantic数据校验模型
│   │   ├── __init__.py
│   │   ├── task.py
│   │   ├── user.py
│   │   ├── reward.py
│   │   └── ...
│   ├── crud/                  # 数据库操作封装
│   │   ├── __init__.py
│   │   ├── task.py
│   │   ├── user.py
│   │   ├── reward.py
│   │   └── ...
│   ├── core/                  # 核心配置、工具、依赖
│   │   ├── __init__.py
│   │   ├── config.py          # 配置管理
│   │   ├── security.py        # 安全相关
│   │   ├── database.py        # 数据库连接
│   │   └── utils.py           # 通用工具
│   ├── tests/                 # 单元测试与集成测试
│   │   ├── __init__.py
│   │   ├── test_task.py
│   │   ├── test_user.py
│   │   └── ...
│   └── dependencies.py        # 依赖注入
├── requirements.txt           # Python依赖列表
├── alembic/                   # 数据库迁移（可选）
│   └── ...
├── .env                       # 环境变量配置
├── README.md                  # 项目说明文档
└── scripts/                   # 启动、运维脚本
    └── ...

## 快速启动
1. 安装依赖
   ```zsh
   pip install -r requirements.txt
   ```

2. 启动服务
   ```zsh
   uvicorn app.main:app --reload
   ```
```

# SkyrisReward 单元测试文档

## 📋 概述

本目录包含 SkyrisReward 奖励管理系统的完整单元测试套件。测试套件使用 pytest 框架，覆盖所有 API 端点、CRUD 操作和核心工具函数。

## 📁 测试文件结构

```
unit_test/
├── __init__.py                  # Python 包初始化
├── conftest.py                  # Pytest 配置和公共 fixtures
├── README.md                    # 本文档
│
├── API 端点测试
   ├── test_user_api.py            # 用户注册、登录、信息获取
   ├── test_task_api.py            # 任务发布、列表、搜索
   ├── test_assignment_api.py      # 作业接受、提交、更新
   ├── test_review_api.py          # 审核提交、申诉
   ├── test_reward_api.py          # 奖励发放、查询
   ├── test_user_center_api.py     # 用户中心功能
   ├── test_notification_api.py    # 通知系统
   └── test_admin_api.py           # 管理员功能

```

## 🚀 运行测试

### 环境准备

```bash
# 安装测试依赖
pip install pytest pytest-cov pytest-asyncio

# 确保在项目根目录
cd /Users/skyrisbobo/skyris/SkyrisReward
```

### 基本运行命令

```bash
# 1. 运行所有测试
pytest unit_test/

# 2. 运行指定测试文件
pytest unit_test/test_user_api.py

# 3. 运行指定测试类
pytest unit_test/test_user_api.py::TestUserRegistration

# 4. 运行指定测试方法
pytest unit_test/test_user_api.py::TestUserRegistration::test_register_success

# 5. 运行包含特定关键字的测试
pytest unit_test/ -k "register"
```

### 高级运行选项

```bash
# 1. 详细输出模式
pytest unit_test/ -v

# 2. 显示详细失败信息
pytest unit_test/ -vv

# 3. 显示打印输出
pytest unit_test/ -s

# 4. 只运行失败的测试
pytest unit_test/ --lf

# 5. 先运行失败的测试
pytest unit_test/ --ff

# 6. 遇到第一个失败就停止
pytest unit_test/ -x

# 7. 遇到 N 个失败后停止
pytest unit_test/ --maxfail=3

# 8. 并行运行测试（需要 pytest-xdist）
pip install pytest-xdist
pytest unit_test/ -n auto

# 9. 生成 HTML 测试报告（需要 pytest-html）
pip install pytest-html
pytest unit_test/ --html=report.html --self-contained-html
```

### 代码覆盖率

```bash
# 1. 运行测试并生成覆盖率报告
pytest unit_test/ --cov=app

# 2. 生成 HTML 覆盖率报告
pytest unit_test/ --cov=app --cov-report=html

# 3. 生成 XML 覆盖率报告（用于 CI/CD）
pytest unit_test/ --cov=app --cov-report=xml

# 4. 显示缺失的测试行
pytest unit_test/ --cov=app --cov-report=term-missing

# 5. 查看 HTML 报告
open htmlcov/index.html  # macOS
```

## 📊 测试覆盖范围

### API 端点测试（100+ 测试用例）

#### 1. 用户 API (`test_user_api.py`) - 12 个测试用例

**TestUserRegistration** - 用户注册测试
- ✅ `test_register_success`: 测试成功注册新用户
  - 验证返回 200 状态码
  - 验证用户名和邮箱正确保存
  - 验证密码已加密
- ✅ `test_register_duplicate_username`: 测试重复用户名注册
  - 验证返回 400 错误
  - 验证错误消息
- ✅ `test_register_invalid_email`: 测试无效邮箱格式
  - 验证返回 422 验证错误
- ✅ `test_register_missing_fields`: 测试缺少必填字段
  - 验证返回 422 验证错误

**TestUserLogin** - 用户登录测试
- ✅ `test_login_success`: 测试成功登录
  - 验证返回 access_token
  - 验证 token_type 为 bearer
- ✅ `test_login_wrong_password`: 测试错误密码
  - 验证返回 401 未授权错误
- ✅ `test_login_nonexistent_user`: 测试不存在的用户
  - 验证返回 401 错误
- ✅ `test_login_missing_credentials`: 测试缺少登录凭据
  - 验证返回 422 验证错误

**TestUserInfo** - 用户信息获取测试
- ✅ `test_get_current_user`: 测试获取当前已认证用户信息
  - 验证返回正确的用户数据
- ✅ `test_get_current_user_unauthorized`: 测试未认证获取用户信息
  - 验证返回 401 错误
- ✅ `test_get_user_by_username`: 测试按用户名获取用户信息
  - 验证返回正确用户
- ✅ `test_get_nonexistent_username`: 测试获取不存在的用户
  - 验证返回 404 错误

#### 2. 任务 API (`test_task_api.py`) - 18 个测试用例

**TestTaskPublish** - 任务发布测试
- ✅ `test_publish_task_success`: 测试成功发布任务
  - 验证任务创建成功
  - 验证任务数据正确保存
- ✅ `test_publish_task_unauthorized`: 测试未认证发布任务
  - 验证返回 401 错误
- ✅ `test_publish_task_invalid_amount`: 测试负数奖励金额
  - 验证返回 422 验证错误
  - 验证金额必须大于 0

**TestTaskList** - 任务列表测试
- ✅ `test_list_tasks`: 测试获取任务列表
  - 验证返回所有任务
- ✅ `test_list_tasks_with_pagination`: 测试分页功能
  - 验证 skip 和 limit 参数工作正常
- ✅ `test_list_tasks_by_status`: 测试按状态筛选
  - 验证只返回指定状态的任务
- ✅ `test_list_tasks_with_order_by`: 测试排序功能
  - 验证按 reward_amount 升序排序
  - 验证按 created_at 排序

**TestTaskDetail** - 任务详情测试
- ✅ `test_get_task_detail`: 测试获取任务详情
  - 验证返回完整任务信息
- ✅ `test_get_nonexistent_task`: 测试获取不存在的任务
  - 验证返回 404 错误

**TestTaskSearch** - 任务搜索测试
- ✅ `test_search_tasks`: 测试关键词搜索
  - 验证搜索结果包含关键词
- ✅ `test_search_tasks_no_results`: 测试无结果搜索
  - 验证返回空列表
- ✅ `test_search_tasks_with_pagination`: 测试搜索分页
  - 验证搜索结果支持分页

**TestTaskUpdate** - 任务更新测试
- ✅ `test_update_task_as_publisher`: 测试发布者更新任务
  - 验证标题和金额更新成功
- ✅ `test_update_task_status`: 测试更新任务状态
  - 验证状态变更成功
- ✅ `test_update_task_unauthorized`: 测试非发布者更新
  - 验证返回 403 权限错误
- ✅ `test_update_nonexistent_task`: 测试更新不存在的任务
  - 验证返回 404 错误

**TestTaskAccept** - 任务接取测试
- ✅ `test_accept_task_success`: 测试成功接取任务
- ✅ `test_accept_task_unauthorized`: 测试未认证接取
  - 验证返回 401 错误
- ✅ `test_accept_nonexistent_task`: 测试接取不存在的任务
  - 验证返回 400 错误

#### 3. 作业 API (`test_assignment_api.py`) - 14 个测试用例

**TestAssignmentAccept** - 作业接受测试
- ✅ `test_accept_task_success`: 测试成功接受任务
  - 验证创建作业记录
  - 验证作业状态为 pending_review
- ✅ `test_accept_nonexistent_task`: 测试接受不存在的任务
  - 验证返回 404 错误
- ✅ `test_accept_task_unauthorized`: 测试未认证接受任务
  - 验证返回 401 错误

**TestAssignmentSubmit** - 作业提交测试
- ✅ `test_submit_assignment_text`: 测试提交文本内容
  - 验证文本内容保存成功
- ✅ `test_submit_assignment_file`: 测试上传文件
  - 验证文件上传成功
  - 验证文件路径保存
- ✅ `test_submit_assignment_unauthorized`: 测试非所有者提交
  - 验证返回 403 权限错误
- ✅ `test_submit_nonexistent_assignment`: 测试提交不存在的作业
  - 验证返回 404 错误

**TestAssignmentProgress** - 作业进度更新测试
- ✅ `test_update_progress_success`: 测试更新进度
  - 验证进度更新成功
- ✅ `test_update_progress_unauthorized`: 测试非所有者更新
  - 验证返回 403 错误
- ✅ `test_update_nonexistent_assignment`: 测试更新不存在的作业
  - 验证返回 404 错误

**TestAssignmentDetail** - 作业详情测试
- ✅ `test_get_assignment_detail`: 测试获取作业详情
  - 验证返回完整作业信息
- ✅ `test_get_nonexistent_assignment`: 测试获取不存在的作业
  - 验证返回 404 错误

**TestAssignmentList** - 作业列表测试
- ✅ `test_list_assignments_by_user`: 测试按用户获取作业列表
  - 验证返回用户的所有作业
- ✅ `test_list_assignments_empty`: 测试空作业列表
  - 验证返回空数组

#### 4. 审核 API (`test_review_api.py`) - 20 个测试用例

**TestReviewSubmit** - 审核提交测试
- ✅ `test_submit_review_success`: 测试成功提交审核（通过）
  - 验证审核记录创建
  - 验证审核结果为 approved
- ✅ `test_submit_review_rejected`: 测试提交拒绝审核
  - 验证审核结果为 rejected
  - 验证审核评论保存
- ✅ `test_submit_review_unauthorized`: 测试非管理员提交审核
  - 验证返回 403 权限错误
- ✅ `test_submit_review_nonexistent_assignment`: 测试审核不存在的作业
  - 验证返回 404 错误
- ✅ `test_submit_review_without_auth`: 测试未认证提交审核
  - 验证返回 401 错误
- ✅ `test_submit_review_duplicate`: 测试重复提交审核
  - 验证返回 409 冲突错误

**TestReviewAppeal** - 审核申诉测试
- ✅ `test_appeal_review`: 测试申诉被拒绝的作业
  - 验证申诉记录创建
  - 验证作业状态更新为 appealing
- ✅ `test_appeal_approved_assignment`: 测试申诉已批准的作业
  - 验证可以申诉已批准的作业
- ✅ `test_appeal_nonexistent_assignment`: 测试申诉不存在的作业
  - 验证返回 404 错误
- ✅ `test_appeal_not_owner`: 测试非所有者申诉
  - 验证返回 403 权限错误
- ✅ `test_appeal_without_auth`: 测试未认证申诉
  - 验证返回 401 错误
- ✅ `test_appeal_pending_assignment`: 测试申诉待审核作业
  - 验证返回 400 错误（状态不允许）

**TestReviewDetail** - 审核详情测试
- ✅ `test_get_review_detail`: 测试获取审核详情
  - 验证返回完整审核信息
- ✅ `test_get_nonexistent_review`: 测试获取不存在的审核
  - 验证返回 404 错误

**TestReviewList** - 审核列表测试
- ✅ `test_list_reviews_by_assignment`: 测试按作业获取审核列表
  - 验证返回该作业的所有审核
- ✅ `test_list_reviews_empty`: 测试空审核列表
  - 验证返回空数组
- ✅ `test_list_reviews_multiple`: 测试多条审核记录
  - 验证返回所有审核记录

**TestReviewUpdate** - 审核更新测试
- ✅ `test_update_review_success`: 测试更新审核评论
  - 验证评论更新成功
- ✅ `test_update_review_result`: 测试更新审核结果
  - 验证结果更新成功
- ✅ `test_update_review_unauthorized`: 测试非管理员更新
  - 验证返回 403 权限错误
- ✅ `test_update_nonexistent_review`: 测试更新不存在的审核
  - 验证返回 404 错误
- ✅ `test_update_review_without_auth`: 测试未认证更新
  - 验证返回 401 错误

#### 5. 奖励 API (`test_reward_api.py`) - 16 个测试用例

**TestRewardIssue** - 奖励发放测试
- ✅ `test_issue_reward_success`: 测试成功发放奖励
  - 验证奖励记录创建
  - 验证金额正确
- ✅ `test_issue_reward_unauthorized`: 测试非管理员发放奖励
  - 验证返回 403 权限错误

**TestRewardDetail** - 奖励详情测试
- ✅ `test_get_reward_detail`: 测试获取奖励详情
  - 验证返回完整奖励信息
- ✅ `test_get_nonexistent_reward`: 测试获取不存在的奖励
  - 验证返回 404 错误

**TestRewardList** - 奖励列表测试
- ✅ `test_list_rewards_by_user`: 测试按用户获取奖励列表
  - 验证返回用户的所有奖励
- ✅ `test_list_rewards_empty`: 测试空奖励列表
  - 验证返回空数组
- ✅ `test_list_rewards_multiple_statuses`: 测试多种奖励状态
  - 验证返回不同状态的奖励

**TestRewardUpdate** - 奖励更新测试
- ✅ `test_update_reward_status`: 测试更新奖励状态
  - 验证状态更新成功
- ✅ `test_update_reward_unauthorized`: 测试非管理员更新
  - 验证返回 403 权限错误
- ✅ `test_update_nonexistent_reward`: 测试更新不存在的奖励
  - 验证返回 404 错误
- ✅ `test_update_reward_without_auth`: 测试未认证更新
  - 验证返回 401 错误

**TestRewardEdgeCases** - 奖励边界情况测试
- ✅ `test_issue_reward_duplicate`: 测试重复发放奖励
  - 验证系统处理重复请求
- ✅ `test_issue_reward_negative_amount`: 测试负数金额
  - 验证返回 422 验证错误
- ✅ `test_issue_reward_without_auth`: 测试未认证发放
  - 验证返回 401 错误
- ✅ `test_get_reward_detail_without_auth`: 测试未认证查看详情
  - 验证可以查看（公开接口）

#### 6. 用户中心 API (`test_user_center_api.py`) - 13 个测试用例

**TestUserProfile** - 用户资料测试
- ✅ `test_get_profile`: 测试获取用户资料
  - 验证返回完整资料信息
- ✅ `test_update_profile`: 测试更新用户资料
  - 验证邮箱更新成功
- ✅ `test_get_profile_unauthorized`: 测试未认证获取资料
  - 验证返回 401 错误

**TestUserTasks** - 用户任务记录测试
- ✅ `test_get_task_records`: 测试获取任务记录
  - 验证返回用户的任务列表
- ✅ `test_get_task_records_with_status`: 测试按状态筛选
  - 验证只返回指定状态的任务
- ✅ `test_get_task_records_with_pagination`: 测试分页
  - 验证分页参数工作正常
- ✅ `test_get_task_records_unauthorized`: 测试未认证访问
  - 验证返回 401 错误

**TestUserPublishedTasks** - 用户发布任务测试
- ✅ `test_get_published_tasks`: 测试获取已发布任务
  - 验证返回用户发布的所有任务
- ✅ `test_get_published_tasks_unauthorized`: 测试未认证访问
  - 验证返回 401 错误

**TestUserRewards** - 用户奖励记录测试
- ✅ `test_get_reward_records`: 测试获取奖励记录
  - 验证返回用户的奖励列表
- ✅ `test_get_reward_records_with_status`: 测试按状态筛选
  - 验证只返回指定状态的奖励
- ✅ `test_get_reward_records_unauthorized`: 测试未认证访问
  - 验证返回 401 错误

**TestUserStatistics** - 用户统计测试
- ✅ `test_get_user_statistics`: 测试获取统计数据
  - 验证返回完整统计信息
  - 验证统计数据准确性

#### 7. 通知 API (`test_notification_api.py`) - 6 个测试用例

**TestNotificationSend** - 通知发送测试
- ✅ `test_send_notification_success`: 测试成功发送通知
  - 验证通知创建成功
  - 验证通知内容正确
- ✅ `test_send_notification_unauthorized`: 测试非管理员发送
  - 验证返回 403 权限错误
- ✅ `test_send_notification_nonexistent_user`: 测试发送给不存在的用户
  - 验证返回 404 错误

**TestNotificationList** - 通知列表测试
- ✅ `test_list_user_notifications`: 测试获取用户通知列表
  - 验证返回用户的所有通知
- ✅ `test_list_notifications_unauthorized`: 测试未认证访问
  - 验证返回 401 错误

**TestNotificationRead** - 通知已读测试
- ✅ `test_mark_notification_read`: 测试标记通知为已读
  - 验证 is_read 状态更新
- ✅ `test_mark_nonexistent_notification_read`: 测试标记不存在的通知
  - 验证返回 404 错误

#### 8. 管理员 API (`test_admin_api.py`) - 12 个测试用例

**TestAdminUsers** - 用户管理测试
- ✅ `test_list_users`: 测试获取用户列表
  - 验证管理员可以查看所有用户
- ✅ `test_list_users_with_pagination`: 测试分页
  - 验证分页参数工作正常
- ✅ `test_list_users_unauthorized`: 测试非管理员访问
  - 验证返回 403 权限错误
- ✅ `test_update_user_role`: 测试更新用户角色
  - 验证角色更新成功
- ✅ `test_update_user_unauthorized`: 测试非管理员更新
  - 验证返回 403 权限错误

**TestAdminTasks** - 任务管理测试
- ✅ `test_list_tasks`: 测试获取任务列表
  - 验证管理员可以查看所有任务
- ✅ `test_list_tasks_with_pagination`: 测试分页
  - 验证分页参数工作正常
- ✅ `test_update_task_status`: 测试更新任务状态
  - 验证状态更新成功
- ✅ `test_flag_task`: 测试标记风险任务
  - 验证任务被标记并关闭
- ✅ `test_admin_tasks_unauthorized`: 测试非管理员访问
  - 验证返回 403 权限错误

**TestAdminStatistics** - 站点统计测试
- ✅ `test_get_site_statistics`: 测试获取站点统计
  - 验证返回完整统计数据
  - 验证数据准确性
- ✅ `test_statistics_unauthorized`: 测试非管理员访问
  - 验证返回 403 权限错误

### 测试用例统计

| 模块 | 测试类数量 | 测试用例数量 | 覆盖场景 |
|-----|----------|------------|---------|
| test_user_api.py | 3 | 12 | 注册、登录、信息获取 |
| test_task_api.py | 6 | 18 | 发布、列表、详情、搜索、更新、接取 |
| test_assignment_api.py | 5 | 14 | 接受、提交、进度、详情、列表 |
| test_review_api.py | 5 | 20 | 提交、申诉、详情、列表、更新 |
| test_reward_api.py | 4 | 16 | 发放、详情、列表、更新、边界 |
| test_user_center_api.py | 5 | 13 | 资料、任务、发布、奖励、统计 |
| test_notification_api.py | 3 | 6 | 发送、列表、已读 |
| test_admin_api.py | 3 | 12 | 用户管理、任务管理、统计 |
| **总计** | **34** | **111** | **全面覆盖** |

### 测试覆盖的关键场景

✅ **成功场景（Happy Path）**
- 正常业务流程
- 标准数据输入
- 预期的用户行为

✅ **失败场景（Negative Cases）**
- 无效输入
- 数据不存在
- 业务规则违反

✅ **权限验证（Authorization）**
- 未认证访问
- 权限不足
- 角色验证

✅ **边界条件（Edge Cases）**
- 空值处理
- 最大/最小值
- 特殊字符
- 重复操作

✅ **状态转换（State Transitions）**
- 任务状态变更
- 作业状态流转
- 审核流程

### 测试覆盖率目标
- **总体覆盖率**: > 85%
- **API 端点**: > 90%
- **CRUD 操作**: > 80%
- **核心工具**: > 95%

## 🔧 Fixtures 说明

`conftest.py` 中定义了以下公共 fixtures：

### 数据库相关
- **`db_session`**: 为每个测试创建新的数据库会话
  - 使用 SQLite 内存数据库
  - 每个测试后自动清理
  - 完全隔离，互不影响

### 测试客户端
- **`client`**: FastAPI TestClient 实例
  - 模拟 HTTP 请求
  - 自动依赖注入
  - 支持所有 HTTP 方法

### 测试用户
- **`test_user`**: 普通用户账户
  - 用户名: `testuser`
  - 密码: `testpass`
  - 角色: `user`

- **`test_admin`**: 管理员账户
  - 用户名: `admin`
  - 密码: `adminpass`
  - 角色: `admin`

- **`test_publisher`**: 发布者账户
  - 用户名: `publisher`
  - 密码: `pubpass`
  - 角色: `publisher`

### 认证 Headers
- **`auth_headers`**: 普通用户的认证 headers
- **`admin_headers`**: 管理员的认证 headers
- **`publisher_headers`**: 发布者的认证 headers

### 使用示例

```python
def test_example(client, auth_headers, test_user):
    """测试示例，使用 fixtures。"""
    response = client.get("/api/user/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["data"]["username"] == "testuser"
```

## 💾 测试数据库

测试使用独立的 SQLite 数据库 (`test.db`)：

### 特点
- ✅ **隔离性**: 与生产数据库完全隔离
- ✅ **临时性**: 每个测试前创建，测试后销毁
- ✅ **快速**: 内存数据库，执行速度快
- ✅ **安全**: 不会影响真实数据

### 数据库配置
```python
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
```

### 注意事项
- 测试数据不会持久化
- 每个测试函数都有独立的数据库状态
- 不需要手动清理测试数据

## ✅ 测试最佳实践

### 1. 测试独立性
- ✅ 每个测试相互独立，不依赖执行顺序
- ✅ 使用 fixtures 准备测试数据
- ✅ 测试后自动清理，不留副作用

### 2. 命名规范
- **文件命名**: `test_<模块名>_api.py`
- **类命名**: `TestFeatureName`
- **方法命名**: `test_<动作>_<场景>`

```

### 5. 测试覆盖场景
对每个功能，测试以下场景：
- ✅ **成功场景**: 正常情况下的预期行为
- ✅ **失败场景**: 错误输入、异常情况
- ✅ **边界条件**: 空值、最大值、最小值
- ✅ **权限验证**: 认证、授权检查


## 🔄 CI/CD 集成

### GitHub Actions 配置

创建 `.github/workflows/test.yml`：

```yaml
name: Unit Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov pytest-asyncio
    
    - name: Run tests with coverage
      run: |
        pytest unit_test/ --cov=app --cov-report=xml --cov-report=term
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: true
    
    - name: Generate HTML coverage report
      if: always()
      run: |
        pytest unit_test/ --cov=app --cov-report=html
    
    - name: Upload coverage HTML
      if: always()
      uses: actions/upload-artifact@v3
      with:
        name: coverage-report
        path: htmlcov/
```

### GitLab CI 配置

创建 `.gitlab-ci.yml`：

```yaml
test:
  stage: test
  image: python:3.12
  
  before_script:
    - pip install -r requirements.txt
    - pip install pytest pytest-cov pytest-asyncio
  
  script:
    - pytest unit_test/ --cov=app --cov-report=xml --cov-report=term
  
  coverage: '/TOTAL.*\s+(\d+%)$/'
  
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
```

## 🐛 调试测试

### 使用 pytest 调试

```bash
# 1. 进入 Python 调试器（遇到失败时）
pytest unit_test/ --pdb

# 2. 在测试开始时就进入调试器
pytest unit_test/ --trace

# 3. 显示局部变量
pytest unit_test/ -l

# 4. 显示完整的 traceback
pytest unit_test/ --tb=long
```

### 在测试中添加断点

```python
def test_debug_example(client):
    """测试调试示例。"""
    response = client.get("/api/user/me")
    
    # 添加断点
    import pdb; pdb.set_trace()
    
    assert response.status_code == 200
```

### 查看日志输出

```bash
# 显示所有日志
pytest unit_test/ -s --log-cli-level=DEBUG

# 只显示失败测试的日志
pytest unit_test/ --log-cli-level=DEBUG
```

## 📈 持续改进

### 定期检查覆盖率
```bash
# 每周运行一次完整的覆盖率检查
pytest unit_test/ --cov=app --cov-report=html
open htmlcov/index.html
```

### 识别测试盲点
```bash
# 查看未测试的代码
pytest unit_test/ --cov=app --cov-report=term-missing
```

### 性能优化
```bash
# 找出最慢的 10 个测试
pytest unit_test/ --durations=10

# 使用并行测试加速
pytest unit_test/ -n auto
```

# 管理员审核功能 API 文档

## 概述

新增了两个管理员审核接口，用于处理任务接取申请和作业提交的审核。

**重要更新**：审核功能已从 `admin` 模块迁移到 `review` 模块，便于统一维护所有审核相关的功能。

### 为什么迁移到 review 模块？

1. **逻辑内聚性**：审核本身就是 review 的核心功能，所有审核操作应该集中管理
2. **代码组织**：review 模块专注于审核流程（接取审核、作业审核、申诉等）
3. **职责单一**：admin 模块专注于用户/任务管理和统计，职责更清晰
4. **维护便利**：所有审核相关的代码在一个模块中，方便维护和扩展

### API 路径变更

| 功能 | 旧路径 (已废弃) | 新路径 (当前) |
|------|----------------|---------------|
| 获取待审核列表 | `/api/admin/assignments/pending` | `/api/review/pending-assignments` |
| 审核接取申请 | `/api/admin/assignments/{id}/review-acceptance` | `/api/review/assignments/{id}/review-acceptance` |
| 审核作业提交 | `/api/admin/assignments/{id}/review-submission` | `/api/review/assignments/{id}/review-submission` |

## 架构说明

### 实现层次

1. **API 层** (`app/api/review.py`)
   - 定义 HTTP 端点
   - 权限验证（admin_only）
   - 请求/响应处理

2. **业务逻辑层** (`app/crud/review.py`)
   - 审核业务逻辑
   - 状态流转控制
   - 通知发送

3. **Schema 层** (`app/schemas/review.py`)
   - 请求/响应数据模型
   - 数据验证

## API 端点

### 1. 获取待审核列表

**端点**: `GET /api/review/pending-assignments`

**权限**: 仅管理员

**参数**:
- `skip`: 跳过记录数 (默认: 0)
- `limit`: 返回记录数 (默认: 20, 最大: 100)

**响应**:
```json
{
  "code": 200,
  "message": "获取成功",
  "data": [
    {
      "id": 1,
      "task_id": 1,
      "user_id": 2,
      "submit_content": null,
      "submit_time": null,
      "status": "task_pending",
      "review_time": null,
      "created_at": "2025-01-24T10:00:00"
    }
  ]
}
```

**说明**:
- `submit_content` 为 `null` → 接取申请待审核
- `submit_content` 有值 → 作业提交待审核

---

### 2. 审核接取申请

**端点**: `POST /api/review/assignments/{assignment_id}/review-acceptance`

**权限**: 仅管理员

**请求体**:
```json
{
  "approved": true,
  "comment": "符合条件，通过"
}
```

**参数说明**:
- `approved`: `true`=通过, `false`=拒绝
- `comment`: 审核备注（可选）

**业务逻辑**:

#### 通过（approved: true）
- Assignment: `task_pending` → `task_receive`
- Task: `open` → `in_progress`
- 发送通知: "您接取任务《xxx》的申请已通过，可以开始做任务了！"

#### 拒绝（approved: false）
- Assignment: `task_pending` → `task_receivement_rejected`
- Task: 保持 `open`
- 发送通知: "您接取任务《xxx》的申请被拒绝，原因：xxx"

**响应**:
```json
{
  "code": 200,
  "message": "审核成功",
  "data": {
    "id": 1,
    "task_id": 1,
    "user_id": 2,
    "status": "task_receive",
    "review_time": "2025-01-24T10:05:00"
  }
}
```

---

### 3. 审核作业提交

**端点**: `POST /api/review/assignments/{assignment_id}/review-submission`

**权限**: 仅管理员

**请求体**:
```json
{
  "approved": true,
  "comment": "质量优秀，符合要求"
}
```

**参数说明**:
- `approved`: `true`=通过, `false`=拒绝
- `comment`: 审核备注（可选）

**业务逻辑**:

#### 通过（approved: true）
- Assignment: `task_pending` → `task_completed`
- Task: `in_progress` → `completed`
- 创建 Reward 记录（状态: `pending`）
- 发送通知: "恭喜！您提交的任务《xxx》作业已通过审核，奖励发放中..."

#### 拒绝（approved: false）
- Assignment: `task_pending` → `task_reject`
- Task: `in_progress` → `open` (重新开放)
- 发送通知: "您提交的任务《xxx》作业未通过审核，原因：xxx，可以申诉"

**响应**:
```json
{
  "code": 200,
  "message": "审核成功",
  "data": {
    "id": 1,
    "task_id": 1,
    "user_id": 2,
    "status": "task_completed",
    "review_time": "2025-01-24T10:10:00"
  }
}
```

---

## 使用示例

### 场景1: 审核接取申请

```bash
# 1. 获取待审核列表
curl -X GET "http://localhost:8000/api/review/pending-assignments" \
  -H "Authorization: Bearer {admin_token}"

# 2. 通过接取申请
curl -X POST "http://localhost:8000/api/review/assignments/1/review-acceptance" \
  -H "Authorization: Bearer {admin_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "approved": true,
    "comment": "用户资质符合要求"
  }'

# 3. 拒绝接取申请
curl -X POST "http://localhost:8000/api/review/assignments/2/review-acceptance" \
  -H "Authorization: Bearer {admin_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "approved": false,
    "comment": "用户信用分不足"
  }'
```

### 场景2: 审核作业提交

```bash
# 1. 获取待审核列表（包含已提交作业的）
curl -X GET "http://localhost:8000/api/review/pending-assignments" \
  -H "Authorization: Bearer {admin_token}"

# 2. 通过作业审核
curl -X POST "http://localhost:8000/api/review/assignments/1/review-submission" \
  -H "Authorization: Bearer {admin_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "approved": true,
    "comment": "作业质量优秀"
  }'

# 3. 拒绝作业审核
curl -X POST "http://localhost:8000/api/review/assignments/2/review-submission" \
  -H "Authorization: Bearer {admin_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "approved": false,
    "comment": "作业质量不达标，请重新提交"
  }'
```

---

## 错误处理

### 常见错误

#### 1. 权限不足
```json
{
  "detail": "Admin privileges required"
}
```
**状态码**: 403

#### 2. Assignment 不存在
```json
{
  "detail": "Assignment not found"
}
```
**状态码**: 404

#### 3. 状态不正确
```json
{
  "detail": "Only task_pending assignments can be reviewed"
}
```
**状态码**: 400

#### 4. 审核类型错误
```json
{
  "detail": "This is a submission review, not an acceptance review. Use review_assignment_submission instead."
}
```
**状态码**: 400

---

## 状态流转图

### 接取申请审核流转

```
用户接取任务
    ↓
assignment: task_pending (submit_content = null)
task: open
    ↓
[管理员审核接取]
    ↓
    ├─ 通过 →  assignment: task_receive
    │          task: in_progress
    │          通知: "接取通过"
    │
    └─ 拒绝 →  assignment: task_receivement_rejected
               task: open
               通知: "接取拒绝"
```

### 作业提交审核流转

```
用户提交作业
    ↓
assignment: task_pending (submit_content != null)
task: in_progress
    ↓
[管理员审核作业]
    ↓
    ├─ 通过 →  assignment: task_completed
    │          task: completed
    │          reward: pending
    │          通知: "审核通过"
    │
    └─ 拒绝 →  assignment: task_reject
               task: open (重新开放)
               通知: "审核拒绝"
```

---

## 数据一致性

### 检查接取审核待处理

```sql
-- 查询所有待审核的接取申请
SELECT ta.id, ta.task_id, ta.user_id, ta.status, ta.submit_content
FROM task_assignments ta
WHERE ta.status = 'task_pending' AND ta.submit_content IS NULL;
```

### 检查作业审核待处理

```sql
-- 查询所有待审核的作业提交
SELECT ta.id, ta.task_id, ta.user_id, ta.status, ta.submit_content
FROM task_assignments ta
WHERE ta.status = 'task_pending' AND ta.submit_content IS NOT NULL;
```

### 检查审核后的数据一致性

```sql
-- 检查 task_receive 状态的 assignment 对应的 task 是否是 in_progress
SELECT ta.id, ta.status as assignment_status, t.status as task_status
FROM task_assignments ta
JOIN tasks t ON ta.task_id = t.id
WHERE ta.status = 'task_receive' AND t.status != 'in_progress';

-- 检查 task_completed 状态的 assignment 是否有对应的 reward
SELECT ta.id, ta.status, r.id as reward_id
FROM task_assignments ta
LEFT JOIN rewards r ON ta.id = r.assignment_id
WHERE ta.status = 'task_completed' AND r.id IS NULL;
```

---

## 注意事项

1. **接取审核和作业审核是两个独立的接口**，需要根据 `submit_content` 判断调用哪个
2. **Task 状态联动**：审核结果会自动更新 Task 的状态
3. **通知自动发送**：审核完成后会自动给用户发送通知
4. **Reward 自动创建**：作业审核通过会自动创建 Reward 记录
5. **任务重新开放**：作业审核拒绝会将 Task 重新变为 open，允许其他用户接取

---

## 测试建议

1. 测试接取审核通过/拒绝的状态流转
2. 测试作业审核通过/拒绝的状态流转
3. 测试 Task 状态的联动更新
4. 测试通知是否正确发送
5. 测试 Reward 是否正确创建
6. 测试错误处理（状态不对、权限不足等）
7. 测试并发审核的数据一致性

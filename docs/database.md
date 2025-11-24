# 数据库表结构设计

本项目核心数据表结构如下：

## 1. 表结构说明

### 用户表（users）
- id（主键，自增）
- username（唯一，索引）
- password_hash
- email
- role（普通用户/发布者/管理员）
- created_at（记录创建时间）
- updated_at（记录更新时间）

### 任务表（tasks）
- id（主键，自增）
- title（任务标题）
- description（任务描述）
- publisher_id（外键，关联 users.id）
- reward_amount（奖励金额）
- status（待接取/进行中/待审核/已完成/已关闭）
- created_at（任务创建时间）
- updated_at（任务更新时间）

### 任务接取表（task_assignments）中间表
- id（主键，自增）
- task_id（外键，关联 tasks.id）
- user_id（外键，关联 users.id）
- submit_content
- submit_time
- status（task_pending:进行中/待审核 | task_receive:接取被接收 | task_receivement_rejected:接取被拒绝 | task_completed:任务已完成 | task_reject:提交被拒绝 | appealing:申诉中）
- review_time

### 奖励结算表（rewards） 中间表
- id（主键，自增）
- assignment_id（外键，关联 task_assignments.id）
- amount（奖励金额）
- issued_time（发放时间）
- status（已发放/待发放/发放失败）
- created_at（奖励创建时间）

### 申诉/审核表（reviews）
- id（主键，自增）
- assignment_id（外键，关联 task_assignments.id） 中间表
- reviewer_id（外键，关联 users.id）
- review_result（通过/不通过/申诉中）
- review_comment（审核评语）
- review_time（审核时间）

### 消息通知表（notifications）
- id（主键，自增）
- user_id（外键，关联 users.id）
- content（通知内容）
- is_read（是否已读）
- created_at（通知创建时间）

---

## 2. 状态枚举详细说明

### 任务状态（tasks.status）
- `open` - 待接取：任务已发布，等待用户接取
- `in_progress` - 进行中：已有用户接取并正在执行
- `pending_review` - 待审核：用户已提交，等待审核
- `completed` - 已完成：任务已通过审核并结算
- `closed` - 已关闭：任务已结束或取消

### 任务接取状态（task_assignments.status）
- `pending_review` - 待审核：用户已提交任务成果，等待审核
- `approved` - 已通过：任务成果通过审核，等待奖励发放
- `rejected` - 未通过：任务成果未通过审核，可重新提交
- `appealing` - 申诉中：用户对审核结果有异议，正在申诉

### 审核结果（reviews.review_result）
- `pending` - 待审核：审核尚未开始
- `approved` - 通过：任务成果符合要求
- `rejected` - 未通过：任务成果不符合要求
- `appealing` - 申诉中：用户已发起申诉

### 奖励状态（rewards.status）
- `pending` - 待发放：奖励已创建，等待发放
- `issued` - 已发放：奖励已成功发放到用户账户
- `failed` - 发放失败：因系统或用户账户问题导致发放失败

---

## 3. ER 图（Mermaid 语法）

```mermaid
erDiagram
    USERS {
        int id PK
        string username
        string password_hash
        string email
        string role
        datetime created_at
        datetime updated_at
    }
    TASKS {
        int id PK
        string title
        string description
        int publisher_id FK
        float reward_amount
        string status
        datetime created_at
        datetime updated_at
    }
    TASK_ASSIGNMENTS {
        int id PK
        int task_id FK
        int user_id FK
        string submit_content
        datetime submit_time
        string status
        datetime review_time
        datetime created_at
    }
    REWARDS {
        int id PK
        int assignment_id FK
        float amount
        string status
        datetime issued_time
        datetime created_at
    }
    REVIEWS {
        int id PK
        int assignment_id FK
        int reviewer_id FK
        string review_result
        string review_comment
        datetime review_time
    }
    NOTIFICATIONS {
        int id PK
        int user_id FK
        string content
        bool is_read
        datetime created_at
    }

    USERS ||--o{ TASKS : publishes
    USERS ||--o{ TASK_ASSIGNMENTS : takes
    TASKS ||--o{ TASK_ASSIGNMENTS : has
    TASK_ASSIGNMENTS ||--o{ REWARDS : gets
    TASK_ASSIGNMENTS ||--o{ REVIEWS : reviewed_by
    USERS ||--o{ REVIEWS : reviews
    USERS ||--o{ NOTIFICATIONS : receives
```

---

## 3. 任务接取状态流转说明

### task_assignments 表状态枚举值

| 状态值 | 中文说明 | 业务含义 |
|-------|---------|---------|
| `task_pending` | 进行中/待审核 | 用户接取任务后的默认状态，包括正在做和已提交等待审核 |
| `task_receive` | 接取被接收 | 管理员审核接取申请通过，允许用户开始做任务 |
| `task_receivement_rejected` | 接取被拒绝 | 管理员拒绝用户接取任务的申请 |
| `task_completed` | 任务已完成 | 用户提交作业后，管理员审核通过，任务真正完成 |
| `task_reject` | 提交被拒绝 | 用户提交作业后，管理员认为质量不合格而拒绝 |
| `appealing` | 申诉中 | 用户对审核结果不满意，提出申诉 |

### 状态流转图

```
[用户接取任务]
    ↓
[task_pending] ← 默认初始状态
    ↓ (管理员审核接取申请)
    ├─ 接取通过 → [task_receive] ← 允许做任务
    │                   ↓ (用户提交作业)
    │              [等待审核]
    │                   ↓ (管理员审核作业)
    │                   ├─ 审核通过 → [task_completed] ← 真正完成
    │                   │                    ↓
    │                   │              (用户申诉) → [appealing]
    │                   │
    │                   └─ 审核拒绝 → [task_reject] ← 质量不合格
    │                                      ↓
    │                                (用户申诉) → [appealing]
    │
    └─ 接取拒绝 → [task_receivement_rejected] ← 不允许做任务
```

### 关键业务逻辑

1. **接取任务**: 用户接取任务时，状态初始化为 `task_pending`
2. **审核接取**: 
   - 通过 → `task_receive` (用户可以开始做任务)
   - 拒绝 → `task_receivement_rejected` (不允许做任务)
3. **提交作业**: 用户在 `task_receive` 状态下提交作业，等待管理员审核
4. **审核作业**:
   - 通过 → `task_completed` (任务完成，发放奖励)
   - 拒绝 → `task_reject` (作业不合格)
5. **申诉**: 只有 `task_completed` 或 `task_reject` 状态可以申诉，状态变为 `appealing`

---



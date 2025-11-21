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
- status（待审核/任务已接收/任务已拒绝/用户申诉/提交任务已通过/提交任务被拒绝/任务进行中）
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



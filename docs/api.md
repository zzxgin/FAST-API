# User & Auth API Documentation (F2-T1)

## 📋 统一响应格式

所有接口返回统一的标准化格式：

### 成功响应
```json
{
  "code": 0,
  "message": "操作成功",
  "data": { /* 实际数据 */ }
}
```

### 错误响应
```json
{
  "code": 400,  // HTTP 状态码
  "message": "错误描述",
  "data": null
}
```

**说明**：
- `code`: 0 表示成功，非 0 表示错误（通常为 HTTP 状态码）
- `message`: 操作结果的中文描述
- `data`: 实际返回的业务数据，失败时为 null

---

## User APIs

### POST /api/user/register
```
@openapi
summary: Register a new user
requestBody:
  required: true
  content:
    application/json:
      schema:
        $ref: '#/components/schemas/UserCreate'
responses:
  200:
    description: User registered successfully
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/UserRead'
  400:
    description: Username already registered
```

### POST /api/user/login
```
@openapi
summary: User login and get JWT token
requestBody:
  required: true
  content:
    application/json:
      schema:
        $ref: '#/components/schemas/UserLogin'
responses:
  200:
    description: Login successful, returns JWT token
    content:
      application/json:
        schema:
          type: object
          properties:
            access_token:
              type: string
            token_type:
              type: string
  401:
    description: Invalid credentials
```

### GET /api/user/me
```
@openapi
summary: Get current authenticated user's info
security:
  - bearerAuth: []
responses:
  200:
    description: Current user info
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/UserRead'
  401:
    description: Unauthorized
```

### GET /api/user/info/{username}
```
@openapi
summary: Get user info by username
parameters:
  - in: path
    name: username
    required: true
    schema:
      type: string
responses:
  200:
    description: User info
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/UserRead'
  404:
    description: User not found
```

## Task APIs

### POST /api/tasks/publish
```
@openapi
summary: Publish a new task
security:
  - bearerAuth: []
requestBody:
  required: true
  content:
    application/json:
      schema:
        $ref: '#/components/schemas/TaskCreate'
responses:
  200:
    description: Task published successfully
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/TaskRead'
  403:
    description: Only publisher can publish tasks
```

### GET /api/tasks/
```
@openapi
summary: List all tasks (paginated, filterable, sortable)
parameters:
  - in: query
    name: skip
    required: false
    schema:
      type: integer
  - in: query
    name: limit
    required: false
    schema:
      type: integer
  - in: query
    name: status
    required: false
    schema:
      type: string
  - in: query
    name: order_by
    required: false
    schema:
      type: string
responses:
  200:
    description: List of tasks
    content:
      application/json:
        schema:
          type: array
          items:
            $ref: '#/components/schemas/TaskRead'
```

### GET /api/tasks/search/
```
@openapi
summary: Search tasks by keyword
parameters:
  - in: query
    name: keyword
    required: true
    schema:
      type: string
  - in: query
    name: skip
    required: false
    schema:
      type: integer
  - in: query
    name: limit
    required: false
    schema:
      type: integer
responses:
  200:
    description: List of tasks
    content:
      application/json:
        schema:
          type: array
          items:
            $ref: '#/components/schemas/TaskRead'
```

### GET /api/tasks/{task_id}
```
@openapi
summary: Get task detail by ID
parameters:
  - in: path
    name: task_id
    required: true
    schema:
      type: integer
responses:
  200:
    description: Task detail
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/TaskRead'
  404:
    description: Task not found
```

### PUT /api/tasks/{task_id}
```
@openapi
summary: Update task info
security:
  - bearerAuth: []
parameters:
  - in: path
    name: task_id
    required: true
    schema:
      type: integer
requestBody:
  required: true
  content:
    application/json:
      schema:
        $ref: '#/components/schemas/TaskUpdate'
responses:
  200:
    description: Task updated successfully
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/TaskRead'
  403:
    description: Only publisher or admin can update tasks
  404:
    description: Task not found
```

### POST /api/tasks/accept/{task_id}
```
@openapi
summary: Accept a task
security:
  - bearerAuth: []
parameters:
  - in: path
    name: task_id
    required: true
    schema:
      type: integer
responses:
  200:
    description: Task accepted successfully
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/TaskRead'
  400:
    description: Task cannot be accepted
```

## Auth APIs

### GET /api/auth/role/{role}
```
@openapi
summary: Check if current user has the specified role
security:
  - bearerAuth: []
parameters:
  - in: path
    name: role
    required: true
    schema:
      type: string
responses:
  200:
    description: Permission granted, returns user info
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/UserRead'
  403:
    description: Insufficient permissions
```

---

# Reward APIs (F2-T4)

### POST /api/reward/issue
```
@openapi
summary: Issue a reward to a user for an assignment
security:
  - bearerAuth: []
requestBody:
  required: true
  content:
    application/json:
      schema:
        $ref: '#/components/schemas/RewardCreate'
responses:
  200:
    description: Reward issued successfully
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/RewardRead'
  403:
    description: Only admin can issue rewards
```

### GET /api/reward/{reward_id}
```
@openapi
summary: Get reward detail by ID
parameters:
  - in: path
    name: reward_id
    required: true
    schema:
      type: integer
responses:
  200:
    description: Reward detail
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/RewardRead'
  404:
    description: Reward not found
```

### GET /api/reward/user/{user_id}
```
@openapi
summary: List all rewards for a user
parameters:
  - in: path
    name: user_id
    required: true
    schema:
      type: integer
responses:
  200:
    description: List of rewards
    content:
      application/json:
        schema:
          type: array
          items:
            $ref: '#/components/schemas/RewardRead'
```

### GET /api/reward/lists
```
@openapi
summary: List all rewards (Admin only)
security:
  - bearerAuth: []
parameters:
  - in: query
    name: skip
    required: false
    schema:
      type: integer
  - in: query
    name: limit
    required: false
    schema:
      type: integer
responses:
  200:
    description: List of rewards
    content:
      application/json:
        schema:
          type: array
          items:
            $ref: '#/components/schemas/RewardRead'
  403:
    description: Only admin can list all rewards
```

### GET /api/reward/stats
```
@openapi
summary: Get reward statistics (Admin only)
security:
  - bearerAuth: []
responses:
  200:
    description: Reward statistics
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/RewardStats'
  403:
    description: Only admin can view reward statistics
```

### PUT /api/reward/{reward_id}
```
@openapi
summary: Update reward info (status, issued_time)
security:
  - bearerAuth: []
parameters:
  - in: path
    name: reward_id
    required: true
    schema:
      type: integer
requestBody:
  required: true
  content:
    application/json:
      schema:
        $ref: '#/components/schemas/RewardUpdate'
responses:
  200:
    description: Reward updated successfully
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/RewardRead'
  403:
    description: Only admin can update rewards
  404:
    description: Reward not found
```

# Review & Assignment APIs (F2-T3)

### POST /api/review/submit
```
@openapi
summary: Submit a review for a task assignment
description: |
  根据 review_type 执行不同业务逻辑：
  - acceptance_review（接取审核，管理员）：
    - approved: assignment -> task_receive, task -> in_progress
    - rejected: assignment -> task_receivement_rejected
  - submission_review（作业审核，管理员）：
    - approved: assignment -> task_completed, task -> completed, 创建 Reward(pending)
    - rejected: assignment -> task_reject，任务保持 in_progress（若之前标记为 completed 则回滚）
  - appeal_review（申诉，作业拥有者）：
    - assignment -> appealing
security:
  - bearerAuth: []
requestBody:
  required: true
  content:
    application/json:
      schema:
        $ref: '#/components/schemas/ReviewCreate'
responses:
  200:
    description: Review submitted successfully
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/ReviewRead'
  403:
    description: Permission denied (role or owner check failed)
  400:
    description: Invalid review type or business state
```

### GET /api/review/list
```
@openapi
summary: List reviews with filters (Admin only)
security:
  - bearerAuth: []
parameters:
  - in: query
    name: skip
    required: false
    schema:
      type: integer
  - in: query
    name: limit
    required: false
    schema:
      type: integer
  - in: query
    name: review_type
    required: false
    schema:
      type: string
  - in: query
    name: review_result
    required: false
    schema:
      type: string
responses:
  200:
    description: List of reviews
    content:
      application/json:
        schema:
          type: array
          items:
            $ref: '#/components/schemas/ReviewRead'
  403:
    description: Only admin can list reviews
```

### GET /api/review/assignment/{assignment_id}
```
@openapi
summary: List all reviews for a specific assignment
parameters:
  - in: path
    name: assignment_id
    required: true
    schema:
      type: integer
responses:
  200:
    description: List of reviews
    content:
      application/json:
        schema:
          type: array
          items:
            $ref: '#/components/schemas/ReviewRead'
```

### GET /api/review/{review_id}
```
@openapi
summary: Get review detail by ID
parameters:
  - in: path
    name: review_id
    required: true
    schema:
      type: integer
responses:
  200:
    description: Review detail
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/ReviewRead'
  404:
    description: Review not found
```

### PUT /api/review/{review_id}
```
@openapi
summary: Update review info and apply review result
description: |
  管理员更新审核结果（通过/拒绝），用于人工审核。
  - 仅允许更新当前为 pending 状态的 review
  - acceptance_review:
    - approved: assignment -> task_receive, task -> in_progress, 若无 Reward 则创建 Reward(pending)
    - rejected: assignment -> task_receivement_rejected
  - submission_review:
    - approved: assignment -> task_completed, task -> completed, Reward(pending|none) -> issued
    - rejected: assignment -> task_reject, task -> in_progress（如果之前标记为 completed）
  - appeal_review: 目前仅支持备注更新，不改变业务状态
security:
  - bearerAuth: []
parameters:
  - in: path
    name: review_id
    required: true
    schema:
      type: integer
requestBody:
  required: true
  content:
    application/json:
      schema:
        $ref: '#/components/schemas/ReviewUpdate'
responses:
  200:
    description: Review updated successfully and business state applied
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/ReviewRead'
  403:
    description: Only admin can update reviews
  404:
    description: Review not found
  400:
    description: Invalid review state or business rule violation
```

### POST /api/assignment/accept
```
@openapi
summary: Accept a task and create an assignment
security:
  - bearerAuth: []
requestBody:
  required: true
  content:
    application/json:
      schema:
        $ref: '#/components/schemas/AssignmentCreate'
responses:
  200:
    description: Assignment created successfully
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/AssignmentRead'
```

### GET /api/assignment/{assignment_id}
```
@openapi
summary: Get assignment detail by ID
parameters:
  - in: path
    name: assignment_id
    required: true
    schema:
      type: integer
responses:
  200:
    description: Assignment detail
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/AssignmentRead'
  404:
    description: Assignment not found
```

### GET /api/assignment/user/{user_id}
```
@openapi
summary: List all assignments for a user
parameters:
  - in: path
    name: user_id
    required: true
    schema:
      type: integer
responses:
  200:
    description: List of assignments
    content:
      application/json:
        schema:
          type: array
          items:
            $ref: '#/components/schemas/AssignmentRead'
```

### POST /api/assignment/submit/{assignment_id}
```
@openapi
summary: Submit assignment result (text or file)
parameters:
  - in: path
    name: assignment_id
    required: true
    schema:
      type: integer
requestBody:
  required: false
  content:
    multipart/form-data:
      schema:
        type: object
        properties:
          submit_content:
            type: string
            description: Submission text or file path
          file:
            type: string
            format: binary
            description: File upload
responses:
  200:
    description: Assignment submitted successfully
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/AssignmentRead'
  403:
    description: No permission to submit for this assignment
  404:
    description: Assignment not found
```

### PATCH /api/assignment/{assignment_id}/progress
```
@openapi
summary: Update assignment progress/status
parameters:
  - in: path
    name: assignment_id
    required: true
    schema:
      type: integer
requestBody:
  required: true
  content:
    application/json:
      schema:
        $ref: '#/components/schemas/AssignmentUpdate'
responses:
  200:
    description: Assignment progress updated successfully
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/AssignmentRead'
  403:
    description: No permission to update this assignment
  404:
    description: Assignment not found
```

### POST /api/assignment/redo/{assignment_id}
```
@openapi
summary: Redo a rejected assignment
security:
  - bearerAuth: []
parameters:
  - in: path
    name: assignment_id
    required: true
    schema:
      type: integer
responses:
  200:
    description: Assignment status reset to task_receive
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/AssignmentRead'
  400:
    description: Only rejected assignments can be redone
  403:
    description: Permission denied
  404:
    description: Assignment not found
```


---

# Notification APIs (F3-T3)

### POST /api/notifications/send
```
@openapi
summary: Send a notification to a user (manual)
security:
  - bearerAuth: []
requestBody:
  required: true
  content:
    application/json:
      schema:
        $ref: '#/components/schemas/NotificationCreate'
responses:
  200:
    description: Notification sent successfully
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/NotificationRead'
  403:
    description: No permission to send notification
```

### GET /api/notifications/user/{user_id}
```
@openapi
summary: List all notifications for a user
parameters:
  - in: path
    name: user_id
    required: true
    schema:
      type: integer
responses:
  200:
    description: List of notifications
    content:
      application/json:
        schema:
          type: array
          items:
            $ref: '#/components/schemas/NotificationRead'
```

### PATCH /api/notifications/{notification_id}/read
```
@openapi
summary: Mark notification as read
security:
  - bearerAuth: []
parameters:
  - in: path
    name: notification_id
    required: true
    schema:
      type: integer
responses:
  200:
    description: Notification marked as read
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/NotificationRead'
  403:
    description: Permission denied
  404:
    description: Notification not found
```

---

# User Center APIs (F3-T4)

### GET /api/user/profile
```
@openapi
summary: Get current user profile
security:
  - bearerAuth: []
responses:
  200:
    description: User profile information
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/UserProfileResponse'
  401:
    description: Unauthorized
  404:
    description: User not found
```

### PUT /api/user/profile
```
@openapi
summary: Update current user profile
security:
  - bearerAuth: []
requestBody:
  required: true
  content:
    application/json:
      schema:
        $ref: '#/components/schemas/UserProfileUpdate'
responses:
  200:
    description: Updated user profile
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/UserProfileResponse'
  401:
    description: Unauthorized
  404:
    description: User not found
```

### GET /api/user/tasks
```
@openapi
summary: Get current user's task records
security:
  - bearerAuth: []
parameters:
  - in: query
    name: status
    required: false
    schema:
      type: string
      enum: [pending_review, approved, rejected, appealing]
  - in: query
    name: skip
    required: false
    schema:
      type: integer
      minimum: 0
  - in: query
    name: limit
    required: false
    schema:
      type: integer
      minimum: 1
      maximum: 100
responses:
  200:
    description: List of user's task records
    content:
      application/json:
        schema:
          type: array
          items:
            $ref: '#/components/schemas/UserTaskRecord'
  401:
    description: Unauthorized
```

### GET /api/user/published-tasks
```
@openapi
summary: Get current user's published tasks
security:
  - bearerAuth: []
parameters:
  - in: query
    name: status
    required: false
    schema:
      type: string
      enum: [open, in_progress, pending_review, completed, closed]
  - in: query
    name: skip
    required: false
    schema:
      type: integer
      minimum: 0
  - in: query
    name: limit
    required: false
    schema:
      type: integer
      minimum: 1
      maximum: 100
responses:
  200:
    description: List of user's published tasks
    content:
      application/json:
        schema:
          type: array
          items:
            $ref: '#/components/schemas/UserPublishedTask'
  401:
    description: Unauthorized
```

### GET /api/user/rewards
```
@openapi
summary: Get current user's reward records
security:
  - bearerAuth: []
parameters:
  - in: query
    name: status
    required: false
    schema:
      type: string
      enum: [pending, issued, failed]
  - in: query
    name: skip
    required: false
    schema:
      type: integer
      minimum: 0
  - in: query
    name: limit
    required: false
    schema:
      type: integer
      minimum: 1
      maximum: 100
responses:
  200:
    description: List of user's reward records
    content:
      application/json:
        schema:
          type: array
          items:
            $ref: '#/components/schemas/UserRewardRecord'
  401:
    description: Unauthorized
```

### GET /api/user/statistics
```
@openapi
summary: Get current user statistics overview
security:
  - bearerAuth: []
responses:
  200:
    description: User statistics overview
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/UserStatistics'
  401:
    description: Unauthorized
```

### GET /api/user/task-stats
```
@openapi
summary: Get detailed user task statistics
security:
  - bearerAuth: []
responses:
  200:
    description: Detailed task statistics
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/UserTaskStats'
  401:
    description: Unauthorized
```

## Components (Schema Reference)

### UserCreate
```
@openapi
UserCreate:
  type: object
  properties:
    username:
      type: string
    email:
      type: string
      nullable: true
    password:
      type: string
    role:
      type: string
      enum: [user, publisher, admin]
```

### UserLogin
```
@openapi
UserLogin:
  type: object
  properties:
    username:
      type: string
    password:
      type: string
```

### UserRead
```
@openapi
UserRead:
  type: object
  properties:
    id:
      type: integer
    username:
      type: string
    email:
      type: string
    role:
      type: string
      enum: [user, publisher, admin]
    created_at:
      type: string
      format: date-time
    updated_at:
      type: string
      format: date-time
```

### TaskCreate
```
@openapi
TaskCreate:
  type: object
  properties:
    title:
      type: string
    description:
      type: string
    reward_amount:
      type: number
      format: float
```

### TaskUpdate
```
@openapi
TaskUpdate:
  type: object
  properties:
    title:
      type: string
    description:
      type: string
    reward_amount:
      type: number
      format: float
    status:
      type: string
      enum: [open, accepted, completed, closed]
```

### TaskRead
```
@openapi
TaskRead:
  type: object
  properties:
    id:
      type: integer
    title:
      type: string
    description:
      type: string
    reward_amount:
      type: number
      format: float
    publisher_id:
      type: integer
    status:
      type: string
      enum: [open, accepted, completed, closed]
    created_at:
      type: string
      format: date-time
    updated_at:
      type: string
      format: date-time
```

### UserProfileUpdate
```
@openapi
UserProfileUpdate:
  type: object
  properties:
    email:
      type: string
```

### UserProfileResponse
```
@openapi
UserProfileResponse:
  type: object
  properties:
    id:
      type: integer
    username:
      type: string
    email:
      type: string
    role:
      type: string
      enum: [user, publisher, admin]
    created_at:
      type: string
      format: date-time
    updated_at:
      type: string
      format: date-time
```

### UserTaskRecord
```
@openapi
UserTaskRecord:
  type: object
  properties:
    task_id:
      type: integer
    task_title:
      type: string
    task_status:
      type: string
      enum: [open, in_progress, pending_review, completed, closed]
    assignment_id:
      type: integer
    assignment_status:
      type: string
      enum: [pending_review, approved, rejected, appealing]
    reward_amount:
      type: number
      format: float
    submit_time:
      type: string
      format: date-time
    review_time:
      type: string
      format: date-time
    created_at:
      type: string
      format: date-time
```

### UserPublishedTask
```
@openapi
UserPublishedTask:
  type: object
  properties:
    task_id:
      type: integer
    title:
      type: string
    status:
      type: string
      enum: [open, in_progress, pending_review, completed, closed]
    reward_amount:
      type: number
      format: float
    total_assignments:
      type: integer
    pending_reviews:
      type: integer
    created_at:
      type: string
      format: date-time
    updated_at:
      type: string
      format: date-time
```

### UserRewardRecord
```
@openapi
UserRewardRecord:
  type: object
  properties:
    reward_id:
      type: integer
    assignment_id:
      type: integer
    task_title:
      type: string
    amount:
      type: number
      format: float
    status:
      type: string
      enum: [pending, issued, failed]
    issued_time:
      type: string
      format: date-time
    created_at:
      type: string
      format: date-time
```

### UserStatistics
```
@openapi
UserStatistics:
  type: object
  properties:
    total_tasks_taken:
      type: integer
    total_tasks_completed:
      type: integer
    total_tasks_published:
      type: integer
    total_rewards_earned:
      type: number
      format: float
    total_rewards_pending:
      type: number
      format: float
    success_rate:
      type: number
      format: float
    average_rating:
      type: number
      format: float
      nullable: true
```

### UserTaskStats
```
@openapi
UserTaskStats:
  type: object
  properties:
    taken_tasks:
      type: integer
    completed_tasks:
      type: integer
    pending_tasks:
      type: integer
    rejected_tasks:
      type: integer
    published_tasks:
      type: integer
    published_completed:
      type: integer
    published_in_progress:
      type: integer
    total_earned:
      type: number
      format: float
    total_pending:
      type: number
      format: float
    monthly_earned:
      type: number
      format: float
    monthly_completed:
      type: integer
```
### ReviewCreate
```
@openapi
ReviewCreate:
type: object
properties:
assignment_id:
type: integer
review_type:
type: string
enum: [acceptance_review, submission_review, appeal_review]
review_result:
type: string
enum: [pending, approved, rejected, appealing]
review_comment:
type: string
nullable: true
```
### ReviewUpdate
```
@openapi
ReviewUpdate:
type: object
properties:
review_result:
type: string
enum: [approved, rejected]
nullable: true
review_comment:
type: string
nullable: true
```
### ReviewRead
```
@openapi
ReviewRead:
type: object
properties:
id:
type: integer
assignment_id:
type: integer
reviewer_id:
type: integer
review_type:
type: string
enum: [acceptance_review, submission_review, appeal_review]
review_result:
type: string
enum: [pending, approved, rejected, appealing]
review_comment:
type: string
nullable: true
review_time:
type: string
format: date-time
```
### RewardCreate
```
@openapi
RewardCreate:
  type: object
  properties:
    assignment_id:
      type: integer
    amount:
      type: number
      format: float
    status:
      type: string
      enum: [pending, issued, failed]
```

### RewardUpdate
```
@openapi
RewardUpdate:
  type: object
  properties:
    status:
      type: string
      enum: [pending, issued, failed]
      nullable: true
    issued_time:
      type: string
      format: date-time
      nullable: true
```

### RewardRead
```
@openapi
RewardRead:
  type: object
  properties:
    id:
      type: integer
    assignment_id:
      type: integer
    amount:
      type: number
      format: float
    status:
      type: string
      enum: [pending, issued, failed]
    issued_time:
      type: string
      format: date-time
      nullable: true
    created_at:
      type: string
      format: date-time
```

### RewardStats
```
@openapi
RewardStats:
  type: object
  properties:
    pending_amount:
      type: number
      format: float
    issued_amount:
      type: number
      format: float
    failed_amount:
      type: number
      format: float
    total_amount:
      type: number
      format: float
```

# Admin APIs (管理后台)

## 用户管理

### GET /api/admin/users
```
@openapi
summary: Get users list (Admin only)
security:
  - bearerAuth: []
parameters:
  - in: query
    name: skip
    required: false
    schema:
      type: integer
      default: 0
  - in: query
    name: limit
    required: false
    schema:
      type: integer
      default: 100
responses:
  200:
    description: List of users
    content:
      application/json:
        schema:
          type: array
          items:
            $ref: '#/components/schemas/AdminUserItem'
  403:
    description: Admin privileges required
```

### PUT /api/admin/users/{user_id}
```
@openapi
summary: Update user info (role)
security:
  - bearerAuth: []
parameters:
  - in: path
    name: user_id
    required: true
    schema:
      type: integer
requestBody:
  required: true
  content:
    application/json:
      schema:
        $ref: '#/components/schemas/AdminUserUpdate'
responses:
  200:
    description: User updated successfully
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/AdminUserItem'
  403:
    description: Admin privileges required
  404:
    description: User not found
```

## 任务管理

### GET /api/admin/tasks
```
@openapi
summary: Get tasks list (Admin only)
security:
  - bearerAuth: []
parameters:
  - in: query
    name: skip
    required: false
    schema:
      type: integer
      default: 0
  - in: query
    name: limit
    required: false
    schema:
      type: integer
      default: 100
responses:
  200:
    description: List of tasks
    content:
      application/json:
        schema:
          type: array
          items:
            $ref: '#/components/schemas/AdminTaskItem'
  403:
    description: Admin privileges required
```

### PUT /api/admin/tasks/{task_id}
```
@openapi
summary: Update task status (Admin only)
security:
  - bearerAuth: []
parameters:
  - in: path
    name: task_id
    required: true
    schema:
      type: integer
requestBody:
  required: true
  content:
    application/json:
      schema:
        $ref: '#/components/schemas/AdminTaskUpdate'
responses:
  200:
    description: Task updated successfully
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/AdminTaskItem'
  400:
    description: No update fields provided
  403:
    description: Admin privileges required
  404:
    description: Task not found
```

### POST /api/admin/tasks/{task_id}/flag
```
@openapi
summary: Flag a task as risky (Admin only)
security:
  - bearerAuth: []
parameters:
  - in: path
    name: task_id
    required: true
    schema:
      type: integer
responses:
  200:
    description: Task flagged successfully
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/AdminTaskItem'
  403:
    description: Admin privileges required
  404:
    description: Task not found
```

## 统计数据

### GET /api/admin/statistics
```
@openapi
summary: Get site statistics (Admin only)
security:
  - bearerAuth: []
responses:
  200:
    description: Site statistics overview
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/SiteStatistics'
  403:
    description: Admin privileges required
```

---

## Admin Components (Schema Reference)

### AdminUserItem
```
@openapi
AdminUserItem:
  type: object
  properties:
    id:
      type: integer
    username:
      type: string
    email:
      type: string
    role:
      type: string
      enum: [user, publisher, admin]
    created_at:
      type: string
      format: date-time
    updated_at:
      type: string
      format: date-time
```

### AdminUserUpdate
```
@openapi
AdminUserUpdate:
  type: object
  properties:
    role:
      type: string
      enum: [user, publisher, admin]
      nullable: true
```

### AdminTaskItem
```
@openapi
AdminTaskItem:
  type: object
  properties:
    id:
      type: integer
    title:
      type: string
    description:
      type: string
    reward_amount:
      type: number
      format: float
    publisher_id:
      type: integer
    status:
      type: string
      enum: [open, in_progress, pending_review, completed, closed]
    flagged:
      type: boolean
    created_at:
      type: string
      format: date-time
    updated_at:
      type: string
      format: date-time
```

### AdminTaskUpdate
```
@openapi
AdminTaskUpdate:
  type: object
  properties:
    status:
      type: string
      enum: [open, in_progress, pending_review, completed, closed]
      nullable: true
```

### SiteStatistics
```
@openapi
SiteStatistics:
  type: object
  properties:
    total_users:
      type: integer
    total_tasks:
      type: integer
    open_tasks:
      type: integer
    in_progress_tasks:
      type: integer
    total_assignments:
      type: integer
    total_rewards_issued:
      type: number
      format: float
    pending_reviews:
      type: integer
```

---

### Security Schemes
```
@openapi
bearerAuth:
  type: http
  scheme: bearer
  bearerFormat: JWT
```

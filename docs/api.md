# User & Auth API Documentation (F2-T1)

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
summary: List all tasks (paginated)
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
    description: Only admin can submit reviews
  400:
    description: Duplicate or invalid review
```

### POST /api/review/appeal/{assignment_id}
```
@openapi
summary: Submit an appeal for a task assignment
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
    description: Appeal submitted successfully
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/ReviewRead'
  403:
    description: Only assignment owner can appeal
  400:
    description: Assignment not eligible for appeal or duplicate appeal
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
summary: Update review info
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
    description: Review updated successfully
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/ReviewRead'
  403:
    description: Only admin can update reviews
  404:
    description: Review not found
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


---

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

### Security Schemes
```
@openapi
bearerAuth:
  type: http
  scheme: bearer
  bearerFormat: JWT
```

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

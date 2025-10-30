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

### Security Schemes
```
@openapi
bearerAuth:
  type: http
  scheme: bearer
  bearerFormat: JWT
```

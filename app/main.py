from fastapi import FastAPI
from app.api import user, auth, tasks, assignment, review, reward, notifications, user_center, admin

# from app.core.exception_handler import global_exception_handler, custom_http_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi import status, HTTPException
from sqlalchemy.exc import IntegrityError
from app.core.exception_handler import (
    global_exception_handler,
    custom_http_exception_handler,
    validation_exception_handler,  # 导入 RequestValidationError 专属处理器
    db_integrity_exception_handler,  # 导入数据库完整性异常处理器
    business_exception_handler,  # 导入自定义业务异常处理器
    BusinessError  # 导入自定义业务异常类
)
app = FastAPI()
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(assignment.router)
app.include_router(review.router)
app.include_router(reward.router)
app.include_router(notifications.router)
app.include_router(user_center.router, prefix="/api/user", tags=["user-center"])
app.include_router(admin.router)

# Register global exception handlers
# app.add_exception_handler(Exception, global_exception_handler)
# app.add_exception_handler(HTTPException, custom_http_exception_handler)
# app.add_exception_handler(RequestValidationError, custom_http_exception_handler)
# 1. 请求数据验证失败（如邮箱格式错误）→ 专属处理器
app.add_exception_handler(RequestValidationError, validation_exception_handler)
# 2. 自定义业务异常（如手动抛出的 BusinessError）→ 专属处理器
app.add_exception_handler(BusinessError, business_exception_handler)
# 3. FastAPI 内置 HTTPException（如用户名已存在）→ 专属处理器
app.add_exception_handler(HTTPException, custom_http_exception_handler)
# 4. 数据库完整性异常（如唯一键冲突）→ 专属处理器
app.add_exception_handler(IntegrityError, db_integrity_exception_handler)
# 5. 所有未捕获的异常 → 兜底处理器（最后注册）
app.add_exception_handler(Exception, global_exception_handler)

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}


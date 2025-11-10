from fastapi import FastAPI
from app.api import user, auth, tasks, assignment, review, reward, notifications

from app.core.exception_handler import global_exception_handler, custom_http_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi import status, HTTPException

app = FastAPI()
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(assignment.router)
app.include_router(review.router)
app.include_router(reward.router)
app.include_router(notifications.router)

# Register global exception handlers
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(HTTPException, custom_http_exception_handler)
app.add_exception_handler(RequestValidationError, custom_http_exception_handler)

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}


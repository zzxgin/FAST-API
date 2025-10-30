from fastapi import FastAPI
from app.api import user, auth, tasks

app = FastAPI()
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(tasks.router)

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}
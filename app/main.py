from fastapi import FastAPI
from app.api import user, auth, tasks, assignment, review, reward

app = FastAPI()
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(assignment.router)
app.include_router(review.router)
app.include_router(reward.router)

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}


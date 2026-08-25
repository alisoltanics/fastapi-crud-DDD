from fastapi import FastAPI

from app.api.routes import auth, todos, users

app = FastAPI(
    title="Todo API",
    version="1.0.0",
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(todos.router, prefix="/api/v1")


@app.get("/health")
def health_check():
    return {"status": "ok"}

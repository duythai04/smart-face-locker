from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.health import router as health_router
from app.api.routes.face import router as face_router


app = FastAPI(
    title="Smart Face Locker API",
    description="AI-powered Smart Locker System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"]
)


# Đăng ký API
app.include_router(health_router)
app.include_router(face_router)


@app.get("/")
def root():
    return {
        "message": "Welcome to Smart Face Locker API"
    }
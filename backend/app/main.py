from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.health import router as health_router
from app.api.routes.face import router as face_router
from app.api.routes.lockers import router as lockers_router
from app.api.routes.enrollment import router as enrollment_router
from app.api.routes.session_maintenance import (
    router as session_maintenance_router,
)


# Initialize FastAPI
app = FastAPI(
    title="Smart Face Locker API",
    description="AI-powered Smart Locker System",
    version="1.0.0"
)


# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=[
        "Content-Type",
        "Authorization"
    ]
)


# Register API Routers
app.include_router(health_router)
app.include_router(face_router)
app.include_router(lockers_router)
app.include_router(enrollment_router)
app.include_router(session_maintenance_router)


# Root Endpoint
@app.get("/", tags=["Root"])
def root():
    return {
        "success": True,
        "message": "Welcome to Smart Face Locker API",
        "version": "1.0.0"
    }
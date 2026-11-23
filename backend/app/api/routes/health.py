from fastapi import APIRouter

router = APIRouter(
    prefix="/api",
    tags=["Health"]
)


@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "Smart Face Locker API",
        "version": "1.0.0"
    }
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.session_cleanup_service import SessionCleanupService


router = APIRouter(
    prefix="/api/internal/sessions",
    tags=["Internal Session Maintenance"],
)


@router.post("/cleanup-expired")
def cleanup_expired_sessions(
    db: Session = Depends(get_db),
):
    return SessionCleanupService.cleanup_expired(db)
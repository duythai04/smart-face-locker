from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.locker import Locker, LockerStatus


router = APIRouter(
    prefix="/api/lockers",
    tags=["Lockers"]
)


def serialize_locker(locker: Locker):
    return {
        "id": locker.id,
        "locker_number": locker.locker_number,
        "status": locker.status.value,
        "created_at": locker.created_at,
        "updated_at": locker.updated_at,
    }


@router.get("")
def get_lockers(db: Session = Depends(get_db)):
    lockers = db.scalars(
        select(Locker).order_by(Locker.locker_number)
    ).all()

    return {
        "success": True,
        "total": len(lockers),
        "lockers": [
            serialize_locker(locker)
            for locker in lockers
        ]
    }


@router.get("/available")
def get_available_lockers(db: Session = Depends(get_db)):
    lockers = db.scalars(
        select(Locker)
        .where(Locker.status == LockerStatus.AVAILABLE)
        .order_by(Locker.locker_number)
    ).all()

    return {
        "success": True,
        "total": len(lockers),
        "lockers": [
            serialize_locker(locker)
            for locker in lockers
        ]
    }


@router.get("/summary")
def get_locker_summary(db: Session = Depends(get_db)):
    rows = db.execute(
        select(Locker.status, func.count(Locker.id))
        .group_by(Locker.status)
    ).all()

    counts = {
        status.value: 0
        for status in LockerStatus
    }

    for status, count in rows:
        counts[status.value] = count

    return {
        "success": True,
        "total": sum(counts.values()),
        "available": counts["AVAILABLE"],
        "reserved": counts["RESERVED"],
        "occupied": counts["OCCUPIED"],
        "out_of_service": counts["OUT_OF_SERVICE"],
    }


@router.get("/{locker_number}")
def get_locker(
    locker_number: int,
    db: Session = Depends(get_db)
):
    locker = db.scalar(
        select(Locker)
        .where(Locker.locker_number == locker_number)
    )

    if locker is None:
        raise HTTPException(
            status_code=404,
            detail="Locker not found"
        )

    return {
        "success": True,
        "locker": serialize_locker(locker)
    }
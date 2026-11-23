import enum
from datetime import datetime, timezone

from sqlalchemy import (
    Integer,
    DateTime,
    Enum,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class LockerStatus(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    RESERVED = "RESERVED"
    OCCUPIED = "OCCUPIED"
    OUT_OF_SERVICE = "OUT_OF_SERVICE"


class Locker(Base):
    __tablename__ = "lockers"

    __table_args__ = (
        UniqueConstraint(
            "locker_number",
            name="uq_locker_number"
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    locker_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    status: Mapped[LockerStatus] = mapped_column(
        Enum(LockerStatus),
        nullable=False,
        default=LockerStatus.AVAILABLE
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )
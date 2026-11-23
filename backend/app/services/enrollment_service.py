from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.locker import Locker, LockerStatus
from app.models.locker_session import LockerSession, SessionStatus
from app.models.face_embedding import FaceEmbedding


class NoAvailableLockerError(Exception):
    pass


class EnrollmentService:

    @staticmethod
    def enroll(
        db: Session,
        embedding: list[float]
    ) -> dict:

        # ArcFace buffalo_l tạo embedding 512 chiều.
        if len(embedding) != 512:
            raise ValueError("Embedding must have 512 dimensions")

        try:
            # Tìm một tủ AVAILABLE và khóa hàng.
            statement = (
                select(Locker)
                .where(Locker.status == LockerStatus.AVAILABLE)
                .order_by(Locker.locker_number)
                .limit(1)
                .with_for_update(skip_locked=True)
            )

            locker = db.scalar(statement)

            if locker is None:
                raise NoAvailableLockerError(
                    "No available locker"
                )

            # Giữ tủ cho khách.
            locker.status = LockerStatus.RESERVED

            # Thời hạn giữ tủ: 5 phút.
            now = datetime.now(timezone.utc).replace(tzinfo=None)

            locker_session = LockerSession(
                locker_id=locker.id,
                status=SessionStatus.RESERVED,
                expires_at=now + timedelta(minutes=5),
            )

            db.add(locker_session)
            db.flush()

            # Lưu embedding của phiên gửi đồ.
            face_embedding = FaceEmbedding(
                session_id=locker_session.id,
                embedding=embedding,
            )

            db.add(face_embedding)

            # Lưu toàn bộ trong một transaction.
            db.commit()

            return {
                "session_id": locker_session.id,
                "locker_number": locker.locker_number,
                "status": SessionStatus.RESERVED.value,
                "expires_at": locker_session.expires_at.isoformat(),
            }

        except Exception:
            db.rollback()
            raise
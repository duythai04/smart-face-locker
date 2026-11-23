from datetime import datetime, timezone

from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from app.models.locker import Locker, LockerStatus
from app.models.locker_session import LockerSession, SessionStatus
from app.models.face_embedding import FaceEmbedding

from app.services.database_lock import locker_operation_lock


class SessionCleanupService:

    @staticmethod
    def _now_utc() -> datetime:
        return datetime.now(timezone.utc).replace(tzinfo=None)

    @staticmethod
    def cleanup_expired(db: Session | None = None) -> dict:
        """
        Dọn dẹp các phiên RESERVED đã hết hạn.

        Toàn bộ thao tác chạy trong MySQL advisory lock.

        db được giữ để tương thích với API hiện tại.
        Transaction thực tế sử dụng locked_db.
        """

        with locker_operation_lock() as locked_db:

            now = SessionCleanupService._now_utc()

            # 1. Khóa các tủ đang RESERVED.
            statement = (
                select(Locker)
                .where(
                    Locker.status == LockerStatus.RESERVED
                )
                .order_by(Locker.id)
                .with_for_update()
            )

            lockers = locked_db.scalars(statement).all()

            cleaned = 0

            # 2. Kiểm tra phiên của từng tủ.
            for locker in lockers:

                expired_statement = (
                    select(LockerSession)
                    .where(
                        LockerSession.locker_id == locker.id,
                        LockerSession.status == SessionStatus.RESERVED,
                        LockerSession.expires_at <= now,
                    )
                    .with_for_update()
                )

                expired_sessions = locked_db.scalars(
                    expired_statement
                ).all()

                for session in expired_sessions:

                    # Xóa embedding.
                    locked_db.execute(
                        delete(FaceEmbedding).where(
                            FaceEmbedding.session_id == session.id
                        )
                    )

                    # Hủy phiên.
                    session.status = SessionStatus.CANCELLED
                    session.completed_at = now

                    cleaned += 1

                if expired_sessions:

                    # Đẩy thay đổi xuống DB trước khi kiểm tra
                    # các phiên còn hiệu lực.
                    locked_db.flush()

                    remaining_session = locked_db.scalar(
                        select(LockerSession.id)
                        .where(
                            LockerSession.locker_id == locker.id,
                            LockerSession.status.in_([
                                SessionStatus.RESERVED,
                                SessionStatus.ACTIVE,
                            ]),
                        )
                        .limit(1)
                    )

                    if remaining_session is None:
                        locker.status = LockerStatus.AVAILABLE

            # Context manager tự commit khi thành công.
            # Nếu có exception, tự rollback.

            return {
                "success": True,
                "cleaned_sessions": cleaned,
            }
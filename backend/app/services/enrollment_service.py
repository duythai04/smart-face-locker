from datetime import datetime, timedelta, timezone

import numpy as np

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.face_recognizer import FaceRecognizer

from app.models.locker import (
    Locker,
    LockerStatus,
)

from app.models.locker_session import (
    LockerSession,
    SessionStatus,
)

from app.models.face_embedding import FaceEmbedding

from app.services.database_lock import (
    locker_operation_lock,
)


# CONFIGURATION

# Ngưỡng thử nghiệm, chưa được hiệu chuẩn cho production.
FACE_MATCH_THRESHOLD = 0.45

# Thời gian giữ tủ: 5 phút.
RESERVATION_MINUTES = 5


# CUSTOM EXCEPTIONS

class NoAvailableLockerError(Exception):
    """
    Không còn tủ AVAILABLE.
    """
    pass


class FaceAlreadyEnrolledError(Exception):
    """
    Khuôn mặt đã có phiên gửi đồ.
    """

    def __init__(self, locker_number: int):

        self.locker_number = locker_number

        super().__init__(
            "Face already enrolled"
        )


# ENROLLMENT SERVICE

class EnrollmentService:

    # 1. CURRENT UTC TIME

    @staticmethod
    def _now_utc() -> datetime:
        """
        Trả về UTC datetime không có timezone.

        Quy ước:
        MySQL DATETIME lưu thời gian UTC.
        """

        return datetime.now(
            timezone.utc
        ).replace(
            tzinfo=None
        )

    # 2. FIND EXISTING FACE

    @staticmethod
    def _find_existing_face(
        db: Session,
        embedding: list[float],
        now: datetime,
    ):
        """
        So sánh khuôn mặt mới với các phiên còn hiệu lực.

        Chỉ kiểm tra:
        - RESERVED chưa hết hạn.
        - ACTIVE.

        Không kiểm tra:
        - COMPLETED.
        - CANCELLED.
        """

        statement = (
            select(
                FaceEmbedding,
                LockerSession,
                Locker,
            )
            .join(
                LockerSession,
                FaceEmbedding.session_id == LockerSession.id,
            )
            .join(
                Locker,
                LockerSession.locker_id == Locker.id,
            )
            .where(
                (
                    (LockerSession.status == SessionStatus.ACTIVE)
                    |
                    (
                        (LockerSession.status == SessionStatus.RESERVED)
                        &
                        (LockerSession.expires_at > now)
                    )
                )
            )
        )

        records = db.execute(statement).all()

        new_embedding = np.asarray(
            embedding,
            dtype=np.float32,
        )

        for face_record, session, locker in records:

            stored_embedding = np.asarray(
                face_record.embedding,
                dtype=np.float32,
            )

            similarity = FaceRecognizer.cosine_similarity(
                new_embedding,
                stored_embedding,
            )

            if similarity >= FACE_MATCH_THRESHOLD:

                return {
                    "session_id": session.id,
                    "locker_number": locker.locker_number,
                    "similarity": similarity,
                }

        return None

    # 3. ENROLL FACE

    @staticmethod
    def enroll(
        db: Session,
        embedding: list[float],
    ) -> dict:
        """
        Đăng ký khuôn mặt và tự động cấp tủ.

        Quy trình:

        1. Validate embedding.
        2. Acquire MySQL advisory lock.
        3. Check duplicate face.
        4. Find available locker.
        5. Reserve locker.
        6. Create locker session.
        7. Save face embedding.
        8. Commit transaction.
        9. Release advisory lock.
        """

        # STEP 1: VALIDATE EMBEDDING

        embedding_array = np.asarray(
            embedding,
            dtype=np.float32,
        )

        if embedding_array.shape != (512,):
            raise ValueError(
                "Embedding must have 512 dimensions"
            )

        if not np.all(
            np.isfinite(embedding_array)
        ):
            raise ValueError(
                "Embedding contains invalid values"
            )

        # Chuyển về list Python để lưu JSON.
        embedding_list = embedding_array.tolist()
        # STEP 2: ACQUIRE DATABASE LOCK

        with locker_operation_lock() as locked_db:

            try:

                now = EnrollmentService._now_utc()

                # STEP 3: CHECK DUPLICATE FACE

                existing_face = (
                    EnrollmentService._find_existing_face(
                        db=db,
                        embedding=embedding_list,
                        now=now,
                    )
                )

                if existing_face is not None:

                    raise FaceAlreadyEnrolledError(
                        locker_number=existing_face[
                            "locker_number"
                        ]
                    )

                # STEP 4: FIND AVAILABLE LOCKER

                statement = (
                    select(Locker)
                    .where(
                        Locker.status
                        == LockerStatus.AVAILABLE
                    )
                    .order_by(
                        Locker.locker_number
                    )
                    .limit(1)
                    .with_for_update(
                        skip_locked=True
                    )
                )

                locker = db.scalar(statement)

                if locker is None:

                    raise NoAvailableLockerError(
                        "No available locker"
                    )

                # STEP 5: RESERVE LOCKER

                locker.status = LockerStatus.RESERVED

                # STEP 6: CREATE LOCKER SESSION

                locker_session = LockerSession(
                    locker_id=locker.id,
                    status=SessionStatus.RESERVED,
                    expires_at=(
                        now
                        + timedelta(
                            minutes=RESERVATION_MINUTES
                        )
                    ),
                )

                db.add(locker_session)

                # Tạo session ID trước khi lưu embedding.
                db.flush()

                # STEP 7: SAVE FACE EMBEDDING

                face_embedding = FaceEmbedding(
                    session_id=locker_session.id,
                    embedding=embedding_list,
                )

                db.add(face_embedding)

                # STEP 8: PREPARE RESPONSE

                result = {
                    "session_id": locker_session.id,
                    "locker_number": locker.locker_number,
                    "status": SessionStatus.RESERVED.value,
                    "expires_at": (
                        locker_session.expires_at.isoformat()
                        + "Z"
                    ),
                }


                db.commit()

                return result

            except Exception:

                # Rollback trước khi advisory lock được giải phóng.
                db.rollback()

                raise
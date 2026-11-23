from contextlib import contextmanager

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import engine


LOCK_NAME = "smart_face_locker_operations"
LOCK_TIMEOUT = 10


class DatabaseLockError(Exception):
    pass


@contextmanager
def locker_operation_lock():
    """
    Giữ MySQL advisory lock trên một connection cố định.

    Tạo SQLAlchemy Session sử dụng cùng connection.
    """

    with engine.connect() as connection:

        acquired = connection.execute(
            text("SELECT GET_LOCK(:name, :timeout)"),
            {
                "name": LOCK_NAME,
                "timeout": LOCK_TIMEOUT,
            },
        ).scalar()

        if acquired != 1:
            connection.rollback()
            raise DatabaseLockError(
                "Could not acquire locker operation lock"
            )

        # Kết thúc transaction do SELECT GET_LOCK khởi tạo.
        # Advisory lock vẫn được giữ trên MySQL connection.
        connection.rollback()

        try:
            with Session(
                bind=connection,
                join_transaction_mode="control_fully",
                expire_on_commit=False,
            ) as db:

                try:
                    yield db

                    # Commit trước khi giải phóng advisory lock.
                    db.commit()

                except Exception:
                    db.rollback()
                    raise

        finally:
            # Nếu còn transaction, kết thúc trước khi release.
            if connection.in_transaction():
                connection.rollback()

            released = connection.execute(
                text("SELECT RELEASE_LOCK(:name)"),
                {"name": LOCK_NAME},
            ).scalar()

            connection.rollback()

            if released != 1:
                raise DatabaseLockError(
                    "Could not release locker operation lock"
                )
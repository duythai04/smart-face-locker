import logging
import signal
import threading

from app.db.session import SessionLocal
from app.services.session_cleanup_service import (
    SessionCleanupService,
)


CLEANUP_INTERVAL_SECONDS = 30

stop_event = threading.Event()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger("cleanup-worker")


def stop_worker(signum, frame):
    logger.info("Stopping cleanup worker...")
    stop_event.set()


def run_cleanup():

    # Giữ tương thích với chữ ký service hiện tại.
    # Service tự tạo Session có advisory lock riêng.
    with SessionLocal() as db:

        result = SessionCleanupService.cleanup_expired(db)

        logger.info(
            "Cleanup completed: %s sessions",
            result["cleaned_sessions"],
        )


def main():

    logger.info(
        "Smart Face Locker Cleanup Worker started"
    )

    logger.info(
        "Cleanup interval: %s seconds",
        CLEANUP_INTERVAL_SECONDS,
    )

    while not stop_event.is_set():

        try:
            run_cleanup()

        except Exception:
            logger.exception("Cleanup failed")

        stop_event.wait(CLEANUP_INTERVAL_SECONDS)

    logger.info("Cleanup Worker stopped")


if __name__ == "__main__":

    signal.signal(signal.SIGINT, stop_worker)
    signal.signal(signal.SIGTERM, stop_worker)

    main()
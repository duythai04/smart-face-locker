from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.locker import Locker, LockerStatus


TOTAL_LOCKERS = 12


def seed_lockers():
    with SessionLocal() as db:
        existing_numbers = set(
            db.scalars(
                select(Locker.locker_number)
            ).all()
        )

        created = 0

        for number in range(1, TOTAL_LOCKERS + 1):
            if number in existing_numbers:
                continue

            db.add(
                Locker(
                    locker_number=number,
                    status=LockerStatus.AVAILABLE
                )
            )

            created += 1

        db.commit()

        print(f"Seed completed. Created {created} lockers.")


if __name__ == "__main__":
    seed_lockers()

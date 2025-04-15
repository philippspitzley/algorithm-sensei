import logging

from sqlmodel import Session

from app.core.db import create_super_user, engine, init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init() -> None:
    with Session(engine) as session:
        create_super_user(session)
        init_db(
            session
        )  # is used for table creation without migrations from alembic see dp.py


def main() -> None:
    logger.info("Creating initial data")
    init()
    logger.info("Initial data created")


if __name__ == "__main__":
    main()

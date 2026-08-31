from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


BASE_DIR = Path(__file__).resolve().parents[2]

DATABASE_DIR = BASE_DIR / "data"

DATABASE_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

DATABASE_PATH = DATABASE_DIR / "conflux.db"

DATABASE_URL = (
    f"sqlite:///{DATABASE_PATH}"
)


class Base(DeclarativeBase):
    pass


engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False
    },
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def get_db():
    """
    Provide a database session.
    """

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


def create_tables():
    """
    Create all database tables.
    """

    Base.metadata.create_all(
        bind=engine
    )
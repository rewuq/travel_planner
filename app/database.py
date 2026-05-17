from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = "sqlite:///./travel.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # потрібно для SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """
    Dependency для FastAPI — відкриває сесію БД на час запиту,
    потім закриває її автоматично.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Створює всі таблиці в БД (викликається при старті додатку)."""
    from models import Project, Place  # імпорт тут щоб уникнути циклічного імпорту
    Base.metadata.create_all(bind=engine)
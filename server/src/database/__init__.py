from fastapi import Request
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker, DeclarativeBase

url = URL.create(
    drivername="postgresql",
    username="domnuraul",
    password="1234",
    host="localhost",
    database="chessdb",
    port=5432,
)


class Base(DeclarativeBase):
    pass


engine = create_engine(url)
SessionLocal = sessionmaker(bind=engine)


def init_db():
    Base.metadata.create_all(engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

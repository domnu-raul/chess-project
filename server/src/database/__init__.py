from fastapi import Request
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import os

url = URL.create(
    drivername="postgresql",
    username="postgres",
    password="password",
    host="db",
    port="5432",
    database="chess_db"
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

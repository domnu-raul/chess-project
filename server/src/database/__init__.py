from fastapi import Request
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from google.cloud.sql.connector import Connector, IPTypes
import pg8000, os

class Base(DeclarativeBase):
    pass

instance_connection_name = os.environ[
    "INSTANCE_CONNECTION_NAME"
]  # e.g. 'project:region:instance'
db_user = os.environ["DB_USER"]  # e.g. 'my-db-user'
db_pass = os.environ["DB_PASS"]  # e.g. 'my-db-password'
db_name = os.environ["DB_NAME"]  # e.g. 'my-database'

ip_type = IPTypes.PUBLIC

connector = Connector()

def __getconn() -> pg8000.dbapi.Connection:
    conn: pg8000.dbapi.Connection = connector.connect(
        instance_connection_name,
        "pg8000",
        user=db_user,
        password=db_pass,
        db=db_name,
        ip_type=ip_type,
    )
    return conn


engine = create_engine(
    "postgresql+pg8000://",
    creator=__getconn,
)

SessionLocal = sessionmaker(bind=engine)


def init_db():
    Base.metadata.create_all(engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

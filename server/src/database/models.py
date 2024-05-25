from . import Base
from sqlalchemy import Column, Integer, String


class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(80))
    email = Column(String(255))
    password = Column(String(255))

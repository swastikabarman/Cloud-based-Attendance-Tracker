from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    email = Column(String(100), unique=True)
    password = Column(String(255))
    role = Column(String(20))


class Class(Base):
    __tablename__ = "classes"
    id = Column(Integer, primary_key=True, index=True)
    class_name = Column(String(100))
    teacher_id = Column(Integer, ForeignKey("users.id"))

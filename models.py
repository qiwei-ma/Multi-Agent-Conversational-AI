from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    phone = Column(String(20), unique=True, nullable=False)
    name = Column(String(50), nullable=False)
    create_time = Column(DateTime, default=datetime.datetime.now)
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")

class Session(Base):
    __tablename__ = 'sessions'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(50), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    create_time = Column(DateTime, default=datetime.datetime.now)
    user = relationship("User", back_populates="sessions")
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(50), ForeignKey('sessions.session_id'))
    content = Column(Text, nullable=False)
    type = Column(String(10), nullable=False)  # 'user' or 'system'
    create_time = Column(DateTime, default=datetime.datetime.now)
    session = relationship("Session", back_populates="messages")
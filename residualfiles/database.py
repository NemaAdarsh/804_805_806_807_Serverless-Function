# database.py
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime
import os

# Create SQLite database
DATABASE_URL = "sqlite:///./serverless_platform.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define database models
class Function(Base):
    __tablename__ = "functions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    route = Column(String, unique=True)
    language = Column(String)  # "python" or "javascript"
    code = Column(Text)
    timeout = Column(Integer, default=30)  # timeout in seconds
    memory_limit = Column(Integer, default=128)  # memory limit in MB
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    executions = relationship("FunctionExecution", back_populates="function")

class FunctionExecution(Base):
    __tablename__ = "function_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    function_id = Column(Integer, ForeignKey("functions.id"))
    execution_time = Column(Float)  # in seconds
    status = Column(String)  # "success" or "error"
    error_message = Column(Text, nullable=True)
    executed_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    function = relationship("Function", back_populates="executions")

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
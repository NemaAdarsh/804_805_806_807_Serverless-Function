from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./functions.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from fastapi import HTTPException
from backend.models import Function
from backend.schemas import FunctionCreate, FunctionResponse
from backend.docker_runner import execute_function
from typing import List, Dict
from backend.database import SessionLocal
from backend.schemas import FunctionResponse
from backend.docker_runner import execute_function
from backend.models import Function
from backend.schemas import FunctionCreate
from backend.database import SessionLocal
from backend.schemas import FunctionResponse
from backend.docker_runner import execute_function
from fastapi import HTTPException


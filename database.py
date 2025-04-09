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


def save_function(func: FunctionCreate) -> FunctionResponse:
    db = SessionLocal()
    db_func = Function(**func.dict())
    try:
        db.add(db_func)
        db.commit()
        db.refresh(db_func)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Function with this name already exists")
    finally:
        db.close()
    return FunctionResponse.from_orm(db_func)
def get_function(func_id: int) -> FunctionResponse:
    db = SessionLocal()
    func = db.query(Function).filter(Function.id == func_id).first()
    db.close()
    if func is None:
        raise HTTPException(status_code=404, detail="Function not found")
    return FunctionResponse.from_orm(func)
def list_functions() -> List[FunctionResponse]:
    db = SessionLocal()
    try:
        functions = db.query(Function).all()
        if not functions:
            raise HTTPException(status_code=404, detail="No functions found")
        return [FunctionResponse.from_orm(func) for func in functions]
    except:
        raise HTTPException(status_code=500, detail="Error retrieving functions")
    finally:
        db.close()



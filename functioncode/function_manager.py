from backend.database import SessionLocal
from backend.models import Function
from backend.schemas import FunctionCreate

def save_function(func: FunctionCreate):
    db = SessionLocal()
    db_function = Function(**func.dict())
    db.add(db_function)
    db.commit()
    db.refresh(db_function)
    db.close()
    return db_function

def get_function(func_id: int):
    db = SessionLocal()
    function = db.query(Function).filter(Function.id == func_id).first()
    db.close()
    return function

def list_functions():
    db = SessionLocal()
    functions = db.query(Function).all()
    db.close()
    return functions

def delete_function(func_id: int):
    db = SessionLocal()
    function = db.query(Function).filter(Function.id == func_id).first()
    if function:
        db.delete(function)
        db.commit()
    db.close()

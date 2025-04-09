from fastapi import FastAPI, HTTPException
from backend.database import SessionLocal, engine, Base
from backend.models import Function
from backend.schemas import FunctionCreate, FunctionResponse
from backend.function_manager import save_function, get_function, list_functions, delete_function
from backend.docker_runner import execute_function


app= FastAPI()

@app.post("/functions/", response_model=FunctionResponse)
def create_function(func: FunctionCreate):
    return save_function(func)


@app.get("/functions/{func_id}", response_model=FunctionResponse)
def write_function(func_id: int):
    func = get_function(func_id)
    if func is None:
        raise HTTPException(status_code=404, map="Function not found")
    return func


def read_function(func_id: int):
    func = get_function(func_id)
    if func is None:
        raise HTTPException(status_code=404, detail="Function not found")
    return func

@app.delete("/functions/{func_id}")
def delete_function_endpoint(func_id: int):
    delete_function(func_id)
    return {"message": "Function deleted"}

@app.get("/functions/", response_model=list[FunctionResponse])
def list_all_functions():
    return list_functions()


from backend.function_manager import save_function, get_function, list_functions, delete_function

save_function(func: FunctionCreate):
    db = SessionLocal()
    db_func = Function(**func.dict())
    db.add(db_func)
    db.commit()
    db.refresh(db_func)
    db.close()
    return db_func

def get_function(func_id: int):
    db = SessionLocal()
    func = db.query(Function).filter(Function.id == func_id).first()
    db.close()

    return func

#list functions
def list_functions():
    db = SessionLocal()
    functions = db.query(Function).all()
    db.close()
    return functions

def delete_function(func_id: int):
    db = SessionLocal()
    func = db.query(Function).filter(Function.id == func_id).first()
    if func:
        db.delete(func)
        db.commit()
    db.close()

    
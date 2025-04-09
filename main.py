from fastapi import FastAPI, HTTPException
from backend.database import SessionLocal, engine, Base
from backend.models import Function
from backend.schemas import FunctionCreate, FunctionResponse
from backend.function_manager import save_function, get_function, list_functions, delete_function
from backend.docker_runner import execute_function

app = FastAPI()

# Create database tables
Base.metadata.create_all(bind=engine)

@app.post("/functions/", response_model=FunctionResponse)
def create_function(func: FunctionCreate):
    return save_function(func)

@app.get("/functions/{func_id}", response_model=FunctionResponse)
def read_function(func_id: int):
    func = get_function(func_id)
    if func is None:
        raise HTTPException(status_code=404, detail="Function not found")
    return func

@app.get("/functions/", response_model=list[FunctionResponse])
def list_all_functions():
    return list_functions()

@app.delete("/functions/{func_id}")
def delete_function_endpoint(func_id: int):
    delete_function(func_id)
    return {"message": "Function deleted"}

@app.post("/execute/{func_id}")
def execute_function_endpoint(func_id: int, input_data: dict):
    result = execute_function(func_id, input_data)
    return {"result": result}



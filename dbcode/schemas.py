from pydantic import BaseModel

class FunctionCreate(BaseModel):
    name: str
    language: str
    code: str
    timeout: float

class FunctionResponse(FunctionCreate):
    id: int

    class Config:
        orm_mode = True

class FunctionExecuteRequest(BaseModel):
    input_data: dict

    timeout: float = 30.0  # default timeout in seconds
    memory_limit: int = 128  # default memory limit in MB
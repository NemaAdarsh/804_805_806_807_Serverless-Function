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

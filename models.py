from sqlalchemy import Column, Integer, String, Float
from backend.database import Base

class Function(Base):
    __tablename__ = "functions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    language = Column(String)
    code = Column(String)
    timeout = Column(Float)


    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    language = Column(String)
    timeout = Column(Integer)
    code = Column(String)


class BasicFunctionModel(Base):
    __tablename__ = "basic_function_model"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    language = Column(String)
    timeout = Column(Integer)


class AdvancedFunctionModel(AdvancedFunctionModel):
    __tablename__ = "advanced_function_model"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    language = Column(String)
    timeout = Column(Integer)
    code = Column(String)





class FunctionCreate(BaseModel):
    name: str
    language: str
    timeout: int
    code: str  # <-- ALSO add this here so you can accept code during creation

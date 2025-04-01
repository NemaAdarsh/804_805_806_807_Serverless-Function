from sqlalchemy import Column, Integer, String, Float
from backend.database import Base

class Function(Base):
    __tablename__ = "functions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    language = Column(String)
    code = Column(String)
    timeout = Column(Float)

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid
import docker
import os
import sqlite3
import traceback

app = FastAPI()

# Try to initialize Docker client with error handling
try:
    client = docker.from_env()
except Exception as e:
    print(f"Docker initialization error: {e}")
    client = None  # We'll check this later when needed

DB_FILE = "functions.db"

# Database setup
def init_db():
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS functions (
            id TEXT PRIMARY KEY,
            name TEXT UNIQUE,
            language TEXT,
            code TEXT,
            timeout INTEGER
        )
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Database initialization error: {e}")

init_db()

# Request Model
class FunctionCreate(BaseModel):
    name: str
    language: str  # "python" or "javascript"
    code: str
    timeout: int = 5  # Default timeout

@app.post("/functions/")
def create_function(func: FunctionCreate):
    func_id = str(uuid.uuid4())
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        # Check if function name already exists
        c.execute("SELECT name FROM functions WHERE name=?", (func.name,))
        if c.fetchone():
            conn.close()
            raise HTTPException(status_code=400, detail=f"Function name '{func.name}' already exists")
            
        c.execute("INSERT INTO functions VALUES (?, ?, ?, ?, ?)",
                  (func_id, func.name, func.language, func.code, func.timeout))
        conn.commit()
        conn.close()
        return {"id": func_id, "name": func.name}
    except sqlite3.Error as e:
        raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")
    except Exception as e:
        traceback.print_exc()  # Print the full traceback to help diagnose
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.get("/functions/{func_name}")
def get_function(func_name: str):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT * FROM functions WHERE name=?", (func_name,))
        result = c.fetchone()
        conn.close()
        
        if not result:
            raise HTTPException(status_code=404, detail="Function not found")
        
        return {"id": result[0], "name": result[1], "language": result[2], "timeout": result[4]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/execute/{func_name}")
def execute_function(func_name: str):
    # Check if Docker client is available
    if client is None:
        raise HTTPException(status_code=500, detail="Docker client is not available")
        
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT * FROM functions WHERE name=?", (func_name,))
        result = c.fetchone()
        conn.close()
       
        if not result:
            raise HTTPException(status_code=404, detail="Function not found")
       
        language, code, timeout = result[2], result[3], result[4]
       
        if language == "python":
            image = "python:3.9"
            command = f"python -c \"{code}\""
        elif language == "javascript":
            image = "node:14"
            command = f"node -e \"{code}\""
        else:
            raise HTTPException(status_code=400, detail="Unsupported language")
       
        try:
            container = client.containers.run(
                image, command, detach=False, remove=True,
                network_mode="none", mem_limit="128m", cpu_period=100000, cpu_quota=50000,
                stderr=True, stdout=True, timeout=timeout
            )
            return {"output": container.decode("utf-8").strip()}
        except docker.errors.ContainerError as e:
            raise HTTPException(status_code=500, detail=f"Execution failed: {e}")
        except docker.errors.APIError as e:
            raise HTTPException(status_code=500, detail=f"Docker API error: {e}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error during execution: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/functions/{func_name}")
def delete_function(func_name: str):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("DELETE FROM functions WHERE name=?", (func_name,))
        if c.rowcount == 0:
            conn.close()
            raise HTTPException(status_code=404, detail="Function not found")
        conn.commit()
        conn.close()
        return {"message": "Function deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
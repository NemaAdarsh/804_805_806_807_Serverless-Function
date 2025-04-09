# Project structure:
# serverless_platform/
# ├── app.py              # FastAPI application
# ├── database.py         # Database models
# ├── docker_manager.py   # Docker container management
# ├── function_service.py # Function CRUD operations
# ├── requirements.txt    # Python dependencies
# ├── templates/
# │   └── base_images/
# │       ├── python/
# │       │   ├── Dockerfile
# │       │   └── runner.py
# │       └── javascript/
# │           ├── Dockerfile
# │           └── runner.js

# app.py
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Body
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
import uvicorn
import json
import os
import time
from database import Function, init_db, get_db
from sqlalchemy.orm import Session
from docker_manager import DockerManager
from function_service import FunctionService

app = FastAPI(title="Serverless Function Platform")
docker_manager = DockerManager()

@app.on_event("startup")
async def startup_event():
    # Initialize database
    init_db()
    # Ensure Docker base images are built
    docker_manager.build_base_images()

@app.get("/")
async def root():
    return {"message": "Welcome to Serverless Function Platform"}

@app.post("/functions/", status_code=201)
async def create_function(
    function_data: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """Create a new function"""
    try:
        function_service = FunctionService(db, docker_manager)
        function = function_service.create_function(function_data)
        return {"id": function.id, "name": function.name, "route": function.route}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/functions/")
async def get_functions(db: Session = Depends(get_db)):
    """Get all functions"""
    function_service = FunctionService(db, docker_manager)
    functions = function_service.get_all_functions()
    return functions

@app.get("/functions/{function_id}")
async def get_function(function_id: int, db: Session = Depends(get_db)):
    """Get a specific function by ID"""
    function_service = FunctionService(db, docker_manager)
    function = function_service.get_function(function_id)
    if not function:
        raise HTTPException(status_code=404, detail="Function not found")
    return function

@app.put("/functions/{function_id}")
async def update_function(
    function_id: int,
    function_data: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """Update a function"""
    try:
        function_service = FunctionService(db, docker_manager)
        function = function_service.update_function(function_id, function_data)
        if not function:
            raise HTTPException(status_code=404, detail="Function not found")
        return function
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/functions/{function_id}")
async def delete_function(function_id: int, db: Session = Depends(get_db)):
    """Delete a function"""
    function_service = FunctionService(db, docker_manager)
    success = function_service.delete_function(function_id)
    if not success:
        raise HTTPException(status_code=404, detail="Function not found")
    return {"message": "Function deleted successfully"}

@app.post("/functions/{function_id}/invoke")
async def invoke_function(
    function_id: int,
    payload: Dict[str, Any] = Body(default={}),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    """Invoke a function with the given payload"""
    function_service = FunctionService(db, docker_manager)
    function = function_service.get_function(function_id)
    if not function:
        raise HTTPException(status_code=404, detail="Function not found")
    
    try:
        start_time = time.time()
        result = docker_manager.run_function(function, payload)
        execution_time = time.time() - start_time
        
        # Store metrics asynchronously
        background_tasks.add_task(
            function_service.record_execution,
            function_id,
            execution_time,
            result.get("status", "error"),
            result.get("error")
        )
        
        if "error" in result:
            return JSONResponse(
                status_code=500,
                content={"error": result["error"]}
            )
        
        return result["output"]
    except Exception as e:
        background_tasks.add_task(
            function_service.record_execution,
            function_id,
            time.time() - start_time,
            "error",
            str(e)
        )
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/execution-stats")
async def get_execution_stats(db: Session = Depends(get_db)):
    """Get execution statistics for all functions"""
    function_service = FunctionService(db, docker_manager)
    stats = function_service.get_execution_stats()
    return stats

@app.get("/base-images")
async def get_base_images():
    """Get available base images"""
    base_images = docker_manager.get_base_images()
    return {"base_images": base_images}

@app.post("/base-images/build")
async def build_base_images():
    """Build base images"""
    try:
        docker_manager.build_base_images()
        return {"message": "Base images built successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
#this endpoint is used to check the health of the serverless function platform
@app.get("/logs/{function_id}")
async def get_function_logs(function_id: int, db: Session = Depends(get_db)):
    """Get logs for a specific function"""
    function_service = FunctionService(db, docker_manager)
    logs = function_service.get_function_logs(function_id)
    if not logs:
        raise HTTPException(status_code=404, detail="Logs not found")
    return logs

@app.get("/logs/")
async def get_all_logs(db: Session = Depends(get_db)):
    """Get logs for all functions"""
    function_service = FunctionService(db, docker_manager)
    logs = function_service.get_all_logs()
    if not logs:
        raise HTTPException(status_code=404, detail="Logs not found")
    return logs

@app.get("/logs/{function_id}/download")
async def download_function_logs(function_id: int, db: Session = Depends(get_db)):
    """Download logs for a specific function"""
    function_service = FunctionService(db, docker_manager)
    logs = function_service.get_function_logs(function_id)
    if not logs:
        raise HTTPException(status_code=404, detail="Logs not found")
    
    while not logs:
        time.sleep(1)
        logs = function_service.get_function_logs(function_id)
    
    # Create a downloadable file from logs
    log_file_path = function_service.create_log_file(logs)
    
    return JSONResponse(
        content={"message": "Logs downloaded successfully", "file_path": log_file_path}
    )

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)


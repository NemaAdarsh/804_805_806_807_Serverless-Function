#this file will include the code to execute the functions through http requests

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse


def create_app():
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app

app = create_app()
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    response = await call_next(request)
    process_time = response.headers.get("X-Process-Time")
    if process_time is not None:
        process_time = float(process_time)
        if process_time:
            response.headers["X-Process-Time"] = process_time
        else:
            response.headers["X-Process-Time"] = "0"
        response.headers["X-Function-Execution"] = "Function executed successfully"
        return response
    else:
        response.headers["X-Process-Time"] = "0"
        response.headers["X-Function-Execution"] = "Function execution failed"
        return response

async def write_function(input_data, timeout, memory_limit):
    return {"status": "success", "message": "Function written successfully"}

async def execute_function(input_data, timeout, memory_limit):
    return {"status": "success", "message": "Function executed successfully"}
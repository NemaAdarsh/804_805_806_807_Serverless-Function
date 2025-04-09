#file is to connect to docker

import docker
from docker import DockerClient
from docker.errors import DockerException
from fastapi import HTTPException
from backend.models import Function
from backend.schemas import FunctionCreate
from backend.function_manager import save_function
from backend.database import SessionLocal
from backend.schemas import FunctionResponse
from backend.docker_runner import execute_function
from typing import List, Dict
from sqlalchemy.orm import Session



# Initialize Docker client
def dockerconnect():
    try:
        client = DockerClient(base_url='unix://var/run/docker.sock')
        return client
    except DockerException as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to Docker: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    return None


#now we will initialize the docker client for other functions
def initialize_docker_client():
    try:
        client = dockerconnect()
        if client is None:
            raise HTTPException(status_code=500, detail="Failed to connect to Docker")
        return client
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error initializing Docker client: {str(e)}")
    
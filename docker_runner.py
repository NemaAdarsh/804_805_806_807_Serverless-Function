import docker
import uuid
import os
from backend.function_manager import get_function

client = docker.from_env()

def execute_function(func_id: int, input_data: dict):
    func = get_function(func_id)
    if not func:
        return {"error": "Function not found"}

    container_name = f"func_{uuid.uuid4().hex}"
    file_path = f"/tmp/{container_name}.py"

    # Save function code to a temporary file
    with open(file_path, "w") as f:
        f.write(func.code)

    try:
        # Run in a Docker container with timeout
        result = client.containers.run(
            image="python:3.9",
            command=f"python {file_path}",
            volumes={file_path: {'bind': file_path, 'mode': 'ro'}},
            detach=False,
            remove=True,
            network_disabled=True
        )
        return {"output": result.decode()}
    except Exception as e:
        return {"error": str(e)}
    finally:
        os.remove(file_path)

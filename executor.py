#this file is used to execute the commands
# in the docker container
# it will be called by the main.py file
# and will execute the commands in the docker container
# and return the result
# it will also handle the errors and return the error message
# and the error code



import subprocess
import json
import os
import docker
from docker.errors import NotFound, APIError
from fastapi import HTTPException
from backend.models import Function
from backend.schemas import FunctionResponse
from backend.database import SessionLocal
from backend.function_manager import get_function


def execute_function(func_id: int, input_data: dict) -> dict:
    client = docker.from_env()
    session = SessionLocal()
    try:
        func = get_function(func_id)
        if func is None:
            raise HTTPException(status_code=404, detail="Function not found")

        temp_dir = f"/tmp/function_{func_id}"
        os.makedirs(temp_dir, exist_ok=True)
        # Copy the function code to the temporary directory
        # Assuming the function code is in a file named function.py

        # Save the function code to a file
        with open(os.path.join(temp_dir, "function.py"), "w") as f:
            f.write(func.code)

        # Build the Docker image
        image, build_logs = client.images.build(path=temp_dir, tag=f"function_{func_id}")
        for log in build_logs:
            if 'stream' in log:
                print(log['stream'].strip())

            elif 'error' in log:
                raise HTTPException(status_code=500, detail=log['error'].strip())
            
            else:
                print(log.strip())
                

        # Run the Docker container
        container = client.containers.run(image.id, detach=True, auto_remove=True)

        # Wait for the container to finish and get the logs
        container.wait()
        logs = container.logs()

        # Parse the output from the logs
        output = json.loads(logs.decode("utf-8"))

        if "error" in output:
            raise HTTPException(status_code=500, detail=output["error"])
        else:
            # Assuming the output is a JSON object, parse it
            output = json.loads(output)

        return output

    except NotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except APIError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up the temporary directory
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)
        session.close()
        client.close()
    
       
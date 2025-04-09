# docker_manager.py
import docker
import os
import tempfile
import json
import time
import uuid
import shutil
from pathlib import Path

class DockerManager:
    def __init__(self):
        self.client = docker.from_env()
        self.base_path = Path(os.path.dirname(os.path.abspath(__file__)))
        self.templates_path = self.base_path / "templates" / "base_images"
        self.python_image_name = "serverless-platform/python:latest"
        self.javascript_image_name = "serverless-platform/javascript:latest"
        
        # Create templates directory if it doesn't exist
        os.makedirs(self.templates_path / "python", exist_ok=True)
        os.makedirs(self.templates_path / "javascript", exist_ok=True)
        
        # Create base image Dockerfiles and runners if they don't exist
        self._create_base_files()
    
    def _create_base_files(self):
        # Python base image files
        python_dockerfile = self.templates_path / "python" / "Dockerfile"
        if not python_dockerfile.exists():
            with open(python_dockerfile, "w") as f:
                f.write("""FROM python:3.9-slim
WORKDIR /app
COPY runner.py /app/
RUN pip install --no-cache-dir requests
CMD ["python", "runner.py"]
""")
        
        python_runner = self.templates_path / "python" / "runner.py"
        if not python_runner.exists():
            with open(python_runner, "w") as f:
                f.write("""
import json
import sys
import time
import os
import traceback
from types import ModuleType

def main():
    # Load function code from file
    with open('/app/function.py', 'r') as f:
        function_code = f.read()
    
    # Load event data
    with open('/app/event.json', 'r') as f:
        event = json.load(f)
    
    # Create a module for the function
    mod = ModuleType('function_module')
    
    try:
        # Execute the function code in the module's namespace
        exec(function_code, mod.__dict__)
        
        # Ensure 'handler' function exists
        if not hasattr(mod, 'handler'):
            raise Exception("Function must contain a 'handler' function")
        
        # Call the handler function with the event
        start_time = time.time()
        result = mod.handler(event)
        execution_time = time.time() - start_time
        
        # Write the result to output file
        with open('/app/result.json', 'w') as f:
            json.dump({
                "output": result,
                "execution_time": execution_time,
                "status": "success"
            }, f)
        
    except Exception as e:
        error_msg = traceback.format_exc()
        with open('/app/result.json', 'w') as f:
            json.dump({
                "error": str(e),
                "traceback": error_msg,
                "status": "error"
            }, f)

if __name__ == '__main__':
    main()
""")
        
        # JavaScript base image files
        js_dockerfile = self.templates_path / "javascript" / "Dockerfile"
        if not js_dockerfile.exists():
            with open(js_dockerfile, "w") as f:
                f.write("""FROM node:16-alpine
WORKDIR /app
COPY runner.js /app/
CMD ["node", "runner.js"]
""")
        
        js_runner = self.templates_path / "javascript" / "runner.js"
        if not js_runner.exists():
            with open(js_runner, "w") as f:
                f.write("""
const fs = require('fs');
const path = require('path');

async function main() {
    try {
        // Load function code
        const functionCode = fs.readFileSync('/app/function.js', 'utf8');
        
        // Load event data
        const event = JSON.parse(fs.readFileSync('/app/event.json', 'utf8'));
        
        // Create a module from the function code
        const functionModule = new Function('exports', 'require', 'module', '__filename', '__dirname', functionCode);
        
        // Create module object
        const module = { exports: {} };
        
        // Execute the function module
        functionModule(module.exports, require, module, '/app/function.js', '/app');
        
        // Ensure handler function exists
        if (typeof module.exports.handler !== 'function') {
            throw new Error("Function must export a 'handler' function");
        }
        
        // Call the handler function with the event
        const startTime = Date.now();
        const result = await module.exports.handler(event);
        const executionTime = (Date.now() - startTime) / 1000;
        
        // Write the result to output file
        fs.writeFileSync('/app/result.json', JSON.stringify({
            output: result,
            execution_time: executionTime,
            status: 'success'
        }));
    } catch (error) {
        fs.writeFileSync('/app/result.json', JSON.stringify({
            error: error.message,
            traceback: error.stack,
            status: 'error'
        }));
    }
}

main();
""")
    
    def build_base_images(self):
        """Build base Docker images for Python and JavaScript functions"""
        try:
            # Build Python base image
            python_path = self.templates_path / "python"
            self.client.images.build(
                path=str(python_path),
                tag=self.python_image_name,
                rm=True
            )
            
            # Build JavaScript base image
            js_path = self.templates_path / "javascript"
            self.client.images.build(
                path=str(js_path),
                tag=self.javascript_image_name,
                rm=True
            )
            
            print("Base images built successfully")
        except Exception as e:
            print(f"Error building base images: {str(e)}")
            raise
    
    def run_function(self, function, event_data):
        """Run a function in a Docker container"""
        # Create a temporary directory to store function code and event data
        temp_dir = tempfile.mkdtemp()
        try:
            # Write function code to file
            if function.language == "python":
                function_file = os.path.join(temp_dir, "function.py")
                image_name = self.python_image_name
            elif function.language == "javascript":
                function_file = os.path.join(temp_dir, "function.js")
                image_name = self.javascript_image_name
            else:
                raise ValueError(f"Unsupported language: {function.language}")
            
            with open(function_file, "w") as f:
                f.write(function.code)
            
            # Write event data to file
            event_file = os.path.join(temp_dir, "event.json")
            with open(event_file, "w") as f:
                json.dump(event_data, f)
            
            # Create a unique container name
            container_name = f"function-{function.id}-{str(uuid.uuid4())[:8]}"
            
            # Run the function in a Docker container
            container = self.client.containers.run(
                image=image_name,
                name=container_name,
                volumes={
                    temp_dir: {"bind": "/app", "mode": "rw"}
                },
                mem_limit=f"{function.memory_limit}m",
                detach=True
            )
            
            # Wait for the container to complete or timeout
            start_time = time.time()
            status = None
            while time.time() - start_time < function.timeout:
                container.reload()
                status = container.status
                if status != "running":
                    break
                time.sleep(0.1)
            
            # If the container is still running after timeout, kill it
            if status == "running":
                container.kill()
                container.remove()
                return {"error": "Function execution timed out", "status": "timeout"}
            
            # Read the result
            result_file = os.path.join(temp_dir, "result.json")
            if os.path.exists(result_file):
                with open(result_file, "r") as f:
                    result = json.load(f)
            else:
                result = {"error": "Function execution failed", "status": "error"}
            
            # Clean up the container
            container.remove()
            
            return result
        except Exception as e:
            return {"error": str(e), "status": "error"}
        finally:
            # Clean up temporary directory
            shutil.rmtree(temp_dir)
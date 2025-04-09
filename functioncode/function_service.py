from database import Function,FunctionExecution
import datetime


class FunctionService:
    def __init__(self,db: Session,docker_manager):
        self.db = db
        self.docker_manager = docker_manager


    def edit_function(self,function_data):
        """Edit an existing function in the database"""
        # Validate required fields
        required_fields = ["id", "name", "route", "language", "code"]
        for field in required_fields:
            if field not in function_data:
                raise ValueError(f"Missing required field: {field}")

        # Validate language
        if function_data["language"] not in ["python", "javascript"]:
            raise ValueError("Language must be either 'python' or 'javascript'")

        # Update function object
        function = self.db.query(Function).filter(Function.id == function_data["id"]).first()
        if not function:
            raise ValueError("Function not found")

        function.name = function_data["name"]
        function.route = function_data["route"]
        function.language = function_data["language"]
        function.code = function_data["code"]
        function.timeout = function_data.get("timeout", 30)
        function.memory_limit = function_data.get("memory_limit", 128)

        self.db.commit()
        self.db.refresh(function)

        return function
    
    def function_data_validation(self,function_data):
        """Validate function data"""
        # Validate required fields
        required_fields = ["name", "route", "language", "code"]
        for field in required_fields:
            if field not in function_data:
                raise ValueError(f"Missing required field: {field}")

        

    if function_data_validation["language"] not in ["python", "javascript"]:
        raise ValueError("Language must be either 'python' or 'javascript'")
    

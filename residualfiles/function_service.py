# function_service.py
from database import Function, FunctionExecution
from sqlalchemy.orm import Session
from sqlalchemy import func
import datetime

class FunctionService:
    def __init__(self, db: Session, docker_manager):
        self.db = db
        self.docker_manager = docker_manager
    
    def create_function(self, function_data):
        """Create a new function in the database"""
        # Validate required fields
        required_fields = ["name", "route", "language", "code"]
        for field in required_fields:
            if field not in function_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate language
        if function_data["language"] not in ["python", "javascript"]:
            raise ValueError("Language must be either 'python' or 'javascript'")
        
        # Create function object
        function = Function(
            name=function_data["name"],
            route=function_data["route"],
            language=function_data["language"],
            code=function_data["code"],
            timeout=function_data.get("timeout", 30),
            memory_limit=function_data.get("memory_limit", 128)
        )
        
        self.db.add(function)
        self.db.commit()
        self.db.refresh(function)
        
        return function
    
    def get_all_functions(self):
        """Get all functions from the database"""
        functions = self.db.query(Function).all()
        return [self._function_to_dict(f) for f in functions]
    
    def get_function(self, function_id):
        """Get a function by ID"""
        function = self.db.query(Function).filter(Function.id == function_id).first()
        if function:
            return self._function_to_dict(function)
        return None
    
    def update_function(self, function_id, function_data):
        """Update a function"""
        function = self.db.query(Function).filter(Function.id == function_id).first()
        if not function:
            return None
        
        # Update fields
        if "name" in function_data:
            function.name = function_data["name"]
        if "route" in function_data:
            function.route = function_data["route"]
        if "language" in function_data:
            if function_data["language"] not in ["python", "javascript"]:
                raise ValueError("Language must be either 'python' or 'javascript'")
            function.language = function_data["language"]
        if "code" in function_data:
            function.code = function_data["code"]
        if "timeout" in function_data:
            function.timeout = function_data["timeout"]
        if "memory_limit" in function_data:
            function.memory_limit = function_data["memory_limit"]
        
        function.updated_at = datetime.datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(function)
        
        return self._function_to_dict(function)
    
    def delete_function(self, function_id):
        """Delete a function"""
        function = self.db.query(Function).filter(Function.id == function_id).first()
        if not function:
            return False
        
        self.db.delete(function)
        self.db.commit()
        
        return True
    
    def record_execution(self, function_id, execution_time, status, error_message=None):
        """Record a function execution"""
        execution = FunctionExecution(
            function_id=function_id,
            execution_time=execution_time,
            status=status,
            error_message=error_message
        )
        
        self.db.add(execution)
        self.db.commit()
    
    def get_execution_stats(self):
        """Get execution statistics for all functions"""
        functions = self.db.query(Function).all()
        stats = []
        
        for function in functions:
            # Get total executions
            total_executions = self.db.query(func.count(FunctionExecution.id)) \
                .filter(FunctionExecution.function_id == function.id) \
                .scalar() or 0
            
            # Get successful executions
            successful_executions = self.db.query(func.count(FunctionExecution.id)) \
                .filter(FunctionExecution.function_id == function.id) \
                .filter(FunctionExecution.status == "success") \
                .scalar() or 0
            
            # Get average execution time
            avg_execution_time = self.db.query(func.avg(FunctionExecution.execution_time)) \
                .filter(FunctionExecution.function_id == function.id) \
                .scalar() or 0
            
            # Get recent executions
            recent_executions = self.db.query(FunctionExecution) \
                .filter(FunctionExecution.function_id == function.id) \
                .order_by(FunctionExecution.executed_at.desc()) \
                .limit(5) \
                .all()
            
            stats.append({
                "function_id": function.id,
                "function_name": function.name,
                "total_executions": total_executions,
                "successful_executions": successful_executions,
                "error_rate": 0 if total_executions == 0 else (total_executions - successful_executions) / total_executions,
                "avg_execution_time": avg_execution_time,
                "recent_executions": [
                    {
                        "executed_at": execution.executed_at.isoformat(),
                        "execution_time": execution.execution_time,
                        "status": execution.status
                    }
                    for execution in recent_executions
                ]
            })
        
        return stats
    
    def _function_to_dict(self, function):
        """Convert Function model to dictionary"""
        return {
            "id": function.id,
            "name": function.name,
            "route": function.route,
            "language": function.language,
            "timeout": function.timeout,
            "memory_limit": function.memory_limit,
            "created_at": function.created_at.isoformat(),
            "updated_at": function.updated_at.isoformat()
        }
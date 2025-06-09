from pydantic import BaseModel


class MiddlewareExecutor(BaseModel):
    """Middleware configuration for command execution.
    
    Middlewares can modify the behavior of commands, such as by iterating over
    multiple values for a single option, running in parallel, etc.
    """
    name: str

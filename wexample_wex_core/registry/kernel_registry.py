from pydantic import BaseModel


class KernelRegistry(BaseModel):
    env: str

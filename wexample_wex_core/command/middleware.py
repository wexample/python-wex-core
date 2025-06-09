from pydantic import BaseModel


class Middleware(BaseModel):
    name: str

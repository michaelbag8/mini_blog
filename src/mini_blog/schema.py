from pydantic import BaseModel

class PostCreate(BaseModel):
    title: str
    content: str

class PostReturn(BaseModel):
    title: str
    content: str
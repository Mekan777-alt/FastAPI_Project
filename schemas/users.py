from pydantic import BaseModel




class User(BaseModel):
    uuid: str
    email: str
    role: str




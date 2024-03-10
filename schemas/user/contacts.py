from pydantic import BaseModel


class Contact(BaseModel):
    name: str
    description: str
    phone: str
    email: str

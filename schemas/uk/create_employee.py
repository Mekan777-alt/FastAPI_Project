from pydantic import BaseModel


class CreateEmployee(BaseModel):
    object_id: int
    first_last_name: str
    email: str
    phone_number: str
    password: str

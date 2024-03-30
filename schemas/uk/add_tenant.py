from pydantic import BaseModel


class AddTenant(BaseModel):
    first_last_name: str
    phone_number: str
    email: str
    phone_number: str
    password: str


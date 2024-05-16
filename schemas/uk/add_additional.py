from pydantic import BaseModel


class Additionaly(BaseModel):
    id: int
    service_name: str

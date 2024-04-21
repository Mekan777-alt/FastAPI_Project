from pydantic import BaseModel


class Meters(BaseModel):
    id: int
    icon_path: str
    name: str

from pydantic import BaseModel


class CreateBathroom(BaseModel):
    characteristic: str

from pydantic import BaseModel
from typing import List


class Staff(BaseModel):
    firstname: str
    phone_number: str
    lastname: str
    photo_path: str
    id: int


class StaffList(BaseModel):
    staff_list: List[Staff]


class StaffInfo(BaseModel):
    firstname: str
    phone_number: str
    lastname: str
    photo_path: str
    object_name: str


class StaffDeleteList(BaseModel):
    firstname: str
    lastname: str
    id: int


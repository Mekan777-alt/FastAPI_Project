from typing import List
from pydantic import BaseModel


class Object(BaseModel):
    id: int
    object_name: str
    object_address: str


class ObjectSchemas(BaseModel):
    objects: List[Object]


class ObjectCreateSchema(BaseModel):
    object_name: str
    object_address: str

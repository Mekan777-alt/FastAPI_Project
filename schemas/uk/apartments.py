from pydantic import BaseModel
from typing import List


class Apartments(BaseModel):
    id: int
    apartment_name: str
    area: float


class ApartmentsList(BaseModel):
    apartments: List[Apartments]


class ApartmentSchemasCreate(BaseModel):
    apartment_name: str
    area: float
    key_holder: str
    internet_speed: int
    internet_fee: float
    internet_operator: str

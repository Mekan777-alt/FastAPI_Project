from typing import List, Dict
from pydantic import BaseModel
from typing_extensions import Literal


class AdditionalService(BaseModel):
    name: str
    price: float


class Service(BaseModel):
    name: str
    services: List[AdditionalService] = []


class Apartment(BaseModel):
    apartment_name: List[str]
    types_of_services: List[Literal["Cleaning", "Gardener", "Pool", "Trash removal", "Other"]]
    additional_services: Dict[Literal["Cleaning"], List[AdditionalService]]

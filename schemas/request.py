from pydantic import BaseModel
from typing import List
from models.models import Order


class ServiceCreate(BaseModel):
    name: str
    description: str
    price: float


class Service(ServiceCreate):
    id: int
    orders: List["Order"] = []

    class Config:
        orm_mode = True


class OrderCreate(BaseModel):
    service_id: int
    tenant_id: int
    dispatcher_id: int
    performer_id: int
    status: str
    execution_date: str


class Order(OrderCreate):
    id: int
    request_date: str
    service: Service
    tenant: ...
    dispatcher: ...
    performer: ...

    class Config:
        orm_mode = True

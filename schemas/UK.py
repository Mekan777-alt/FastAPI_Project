from typing import List
from pydantic import BaseModel


class PaymentDetails(BaseModel):
    id: int
    details: str


class Employee(BaseModel):
    id: int
    name: str


class UKCreate(BaseModel):
    name: str
    login: str
    password: str


class UK(UKCreate):
    id: int
    employees: List[Employee] = []
    payment_details: List[PaymentDetails] = []

    class Config:
        orm_mode = True

from pydantic import BaseModel, Field
from typing import List


class AdditionalServiceSchema(BaseModel):
    service: str = Field(..., example="Ironing")
    price: float = Field(..., example=5.0)
    countable: bool = Field(..., example=True)
    quantity: int = Field(..., example=2)


class DocumentSchema(BaseModel):
    file_name: str = Field(..., example="invoice.pdf")
    mime_type: str = Field(..., example="application/pdf")


class OrderCreateSchema(BaseModel):
    address: str = Field(..., example="122-Floor-2nd floor, Smart, 17")
    completion_date: str = Field(..., example="2023-07-25")
    completion_time: str = Field(..., example="12:05")
    selected_services: str = Field(..., example="Cleaning")
    notes: str = None
    status: str = "pending"
    additional_services: List[AdditionalServiceSchema] = Field(..., example=[
        {"service": "Ironing", "price": 5, "countable": True, "quantity": 2}])
    documents: List[DocumentSchema] = Field(..., example=[{"file_name": "invoice.pdf", "mime_type": "application/pdf"}])
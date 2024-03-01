from pydantic import BaseModel, Field
from typing import List
from schemas.new_order import AdditionalServiceSchema, DocumentSchema


class OrderGetSchema(BaseModel):
    order_id: str = Field(..., example="1")
    status: str = "pending"
    address: str = Field(..., example="122-Floor-2nd floor, Smart, 17")
    completion_date: str = Field(..., example="2023-07-25")
    completion_time: str = Field(..., example="12:05")
    selected_services: str = Field(..., example="Cleaning")
    notes: str = None
    additional_services: List[AdditionalServiceSchema] = Field(..., example=[
        {"service": "Ironing", "price": 5, "quantity": 2}])
    documents: List[DocumentSchema] = Field(..., example=[{"file_name": "invoice.pdf", "mime_type": "application/pdf"}])


class OrderListResponse(BaseModel):
    orders: List[OrderGetSchema]
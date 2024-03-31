from pydantic import BaseModel, Field
from typing import List


class AdditionalServiceSchema(BaseModel):
    additional_service_id: int = Field(..., example=1)
    quantity: int = Field(..., example=2)


class DocumentSchema(BaseModel):
    file_name: str = Field(..., example="invoice.pdf")
    mime_type: str = Field(..., example="application/pdf")


class OrderCreateSchema(BaseModel):
    apartment_id: int = Field(..., example=1)
    completion_date: str = Field(..., example="2023-07-25")
    completion_time: str = Field(..., example="12:05")
    selected_services: str = Field(..., example="Cleaning")
    notes: str = None
    additional_services: List[AdditionalServiceSchema] = Field(..., example=[
        {"service_id": 1, "quantity": 2}])
    documents: List[DocumentSchema] = Field(..., example=[{"file_name": "invoice.pdf", "mime_type": "application/pdf"}])
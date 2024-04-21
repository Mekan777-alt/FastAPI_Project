from datetime import date, time
from pydantic import BaseModel, Field
from typing import Optional, List


class DocumentSchema(BaseModel):
    file_name: str = Field(..., example="invoice.pdf")
    mime_type: str = Field(..., example="application/pdf")


class GuestPassModel(BaseModel):
    visit_date: date = Field(..., example="2021-08-01")
    visit_time: time = Field(..., example="08:00")
    full_name: str = Field(..., example="<NAME>")
    apartment_id: int = Field(..., example=1)
    note: str = Field(..., example="This is a note")
    documents: Optional[List[DocumentSchema]] = None

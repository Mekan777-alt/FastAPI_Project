from pydantic import BaseModel


class Invoice(BaseModel):
    service_name: str
    service_id: int
    bill_number: str
    amount: float
    comment: str

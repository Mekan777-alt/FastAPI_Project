from pydantic import BaseModel


class EnterMeters(BaseModel):
    apartment_id: int
    meter_id: int
    bill_number: str
    month_year: str
    meter_readings: str
    comment: str

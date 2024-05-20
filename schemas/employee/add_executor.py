from pydantic import BaseModel


class AddExecutor(BaseModel):
    first_name: str
    last_name: str
    specialization: str
    phone_number: str
    email: str
    recipient_name: str
    account: str
    contact_number: str
    purpose_of_payment: str
    bic: str
    correspondent_account: str
    bank_name: str
    inn: str
    kpp: str

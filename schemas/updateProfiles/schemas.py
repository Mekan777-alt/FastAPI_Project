from pydantic import BaseModel, EmailStr
from typing import Optional


class UpdateProfiles(BaseModel):
    first_last_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    name_of_company: Optional[str] = None
    unified_contact_phone_number: Optional[str] = None
    unified_contact_email: Optional[EmailStr] = None
    offers_email: Optional[EmailStr] = None
    mobile_application_phone_number: Optional[str] = None
    mobile_application_email: Optional[EmailStr] = None
    recipient_name: Optional[str] = None
    account: Optional[str] = None
    okpo: Optional[str] = None
    bic: Optional[str] = None
    correspondent_account: Optional[str] = None
    bank_name: Optional[str] = None
    inn: Optional[str] = None
    kpp: Optional[str] = None

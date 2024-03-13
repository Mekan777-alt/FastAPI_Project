from pydantic import BaseModel
from typing import List
from schemas.user.contacts import Contact


class UKProfile(BaseModel):
    uk_name: str
    contact: List[Contact]

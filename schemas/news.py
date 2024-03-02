from datetime import date
from typing import List

from pydantic import BaseModel


class News(BaseModel):
    id: int
    name: str
    description: str
    created_at: str


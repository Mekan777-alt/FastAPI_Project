from pydantic import BaseModel
from typing import Literal, Optional


class Additionally(BaseModel):
    pool: Optional[Literal[True, False]] = None
    garden: Optional[Literal[True, False]] = None

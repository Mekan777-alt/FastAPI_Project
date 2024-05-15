from pydantic import BaseModel
from fastapi import Form, File, UploadFile
from typing import List, Optional


class NewsSchema(BaseModel):
    name: str = Form(...)
    description: str = Form(...)
    photo: UploadFile = File(...)
    apartment_list: List[int]

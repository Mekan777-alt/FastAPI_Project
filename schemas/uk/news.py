from pydantic import BaseModel
from fastapi import Form, File, UploadFile


class NewsSchema(BaseModel):
    name: str = Form(...)
    description: str = Form(...)
    photo: UploadFile = File(...)

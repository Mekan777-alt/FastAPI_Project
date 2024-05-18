from pydantic import BaseModel


class Additionaly(BaseModel):
    id: int
    service_name: str

    def to_dict(self):
        return {
            "id": self.id,
            "service_name": self.service_name,
        }

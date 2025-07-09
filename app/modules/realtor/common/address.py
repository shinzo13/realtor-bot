from pydantic import BaseModel

class Address(BaseModel):
    text: str
    tag: str
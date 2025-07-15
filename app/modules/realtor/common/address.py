from pydantic import BaseModel
from enum import Enum

# TODO typechecking kind
class AddressKind(Enum):
    COUNTRY = "country"
    LOCALITY = "locality"
    PROVINCE = "province"
    DISTRICT = "district"
    AREA = "area"



class Address(BaseModel):
    text: str
    kind: str
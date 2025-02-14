from pydantic import BaseModel, Field, ValidationError, StrictInt, ConfigDict, field_validator
from typing import List, Optional

class Address(BaseModel):
    street: str = Field(...)
    city: str = Field(...)
    state: Optional[str] = None
    zip_code: Optional[int] = None

    @field_validator('zip_code')
    def zip_code_must_be_five_digits(cls, v):
        if v is not None and (v < 10000 or v > 99999):
            raise ValueError('zip_code must be a five-digit number')
        return v

class User(BaseModel):
    id: StrictInt = Field(...)
    name: str = Field(...)
    email: Optional[str] = None
    age: Optional[int] = None
    addresses: List[Address] = Field(...)

    model_config = ConfigDict(arbitrary_types_allowed = False)

    @field_validator('email')
    def email_must_contain_at_symbol(cls, v):
        if v is not None and '@' not in v:
            raise ValueError('email must contain @ symbol')
        return v


addresses = {
    1: { 'street': "123 Main St", 'city': "Anytown", 'zip_code': 12345 },
    2: { 'street': "123 Main St", 'city': "Anytown", 'zip_code': 123 }
}
users = {
    1: { 'id': 1, 'name': "John Doe", 'email': "johndoe@example.com", 'addresses': [addresses[1]]},
    2: { 'id': 2, 'name': "John Doe", 'email': "johndoeexample.com", 'addresses': [addresses[1]]}
}

for k, v in addresses.items():
    try:
        addresses[k] = Address(**v)
        print("OK: %s\n" % addresses[k])
    except ValidationError as e:
        print("FAIL: %s\n" %e.json())

for k, v in users.items():
    try:
        users[k] = User(**v)
        print("OK: %s\n" % users[k])
    except ValidationError as e:
        print("FAIL: %s\n" %e.json())

# Serialization and deserialization example
try:
    address = Address(street="123 Main St", city="Anytown", zip_code=12345)
    user = User(id=1, name="John Doe", email="johndoe@example.com", addresses=[address])
    print(user)
    
    # Serialization
    user_json = user.model_dump_json()
    print("Serialized User:", user_json)
    
    # Deserialization
    user_obj = User.model_validate_json(user_json)
    print("Deserialized User:", user_obj)
except ValidationError as e:
    print(e.json())


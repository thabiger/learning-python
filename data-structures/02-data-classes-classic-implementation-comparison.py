from pydantic import BaseModel, Field, ValidationError, StrictInt, ConfigDict
from typing import List, Optional

from dataclasses import dataclass, field

class OldschoolCar:
    def __init__(self, id, vendor, model = None):
        self.__id = id
        self.__vendor = vendor
        self.__model = model if model else "Just a car"

    # omit setters to make the attributes immutable
    @property
    def id(self):
        return self.__id

    @property
    def vendor(self):
        return self.__vendor

    @property
    def model(self):
        return self.__model

    # implement comparison method
    def __eq__(self, other):
        return self.vendor == other.vendor and self.model == other.model

    # implement string representation
    def __repr__(self):
        return f'OldschoolCar(id={self.id}, vendor={self.vendor}, model={self.model})'

@dataclass(frozen=True)
class Car:
    id: int = field(compare=False)
    vendor: str
    model: str = field(default="Just a car")

class SuperCar(BaseModel):
    id: StrictInt = Field(...)
    vendor: str = Field(...)
    model: str = Field(default="Just a car")

    class Config:
        extra = 'allow'

    model_config = ConfigDict(arbitrary_types_allowed = False)

car1 = Car(1, 'Honda', 'Civic')  # Correct type for id is int, not str
car2 = Car(2, 'Honda', 'Civic')

old_car1 = OldschoolCar( '1', 'Honda', 'Civic')
old_car2 = OldschoolCar( '2', 'Honda', 'Civic')

super_car1 = SuperCar( id=1, vendor='Honda', model='Civic', x="daf")
super_car2 = SuperCar( id=2, vendor='Honda', model='Civic')
print(super_car1.model_dump_json())

#Compare
print ("Cars are the same: %s" % (car1 == car2))
print ("Cars are the same: %s" % (old_car1 == old_car2))

#Print
print (car1)
print (old_car1)


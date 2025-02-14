from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Address:
    street: str
    city: str
    state: Optional[str] = None
    zip_code: Optional[int] = None

@dataclass
class Job:
    company_name: str
    position: str

@dataclass
class Cars:
    model: str
    vendor: str


@dataclass
class User:
    id: int
    name: str
    email: Optional[str] = None
    age: Optional[int] = None
    addresses: List[Address] = field(default_factory=list)
    job: Optional[Job] = field(default_factory=Job)
    cars: List[Cars] = []

address = Address(street="123 Main St", city="Anytown")
user = User(id=1, name="John Doe", addresses=[address], job=Job(company_name="ACME", position="Developer"))
print(user.id)
print(user.addresses[0].city)
print(user.job.company_name)

user = User(id=2, name="Jane Doe", addresses=[address], job=Job(company_name="UmbrellaCorp", position="Tester"))
print(user.id)
print(user.addresses[0].city)
print(user.job.company_name)
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class BuyerDTO:
    name: str
    surname: str
    birth_date: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    email: Optional[str] = None
    gsm_number: Optional[str] = None
    id: Optional[str] = None
    identity_number: Optional[str] = None
    ip: Optional[str] = None
    last_login_date: Optional[str] = None
    registration_address: Optional[str] = None
    registration_date: Optional[str] = None
    title: Optional[str] = None
    zip_code: Optional[str] = None


# TODO : Add other models for order
@dataclass
class OrderCreateDTO:
    amount: float
    currency: str
    locale: str
    buyer: BuyerDTO

    def to_dict(self) -> dict:
        return asdict(self)

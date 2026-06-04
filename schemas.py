from pydantic import BaseModel
from typing import Optional


class ClaimCreate(BaseModel):
    product_id: int
    buyer_name: str
    buyer_email: str
    reference_number: str


class PaymentNotificationCreate(BaseModel):
    reference_number: str
    amount: float
    sender_name: Optional[str] = None


class ProductCreate(BaseModel):
    name: str
    price: float
    filepath: str


class OCRResponse(BaseModel):
    reference_number: Optional[str]
    amount: Optional[float]

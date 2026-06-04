from pydantic import BaseModel, Field
from typing import Optional


class ClaimCreate(BaseModel):
    product_id: int
    buyer_name: str = Field(..., min_length=1, max_length=250)
    buyer_email: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$", max_length=254)
    reference_number: str = Field(..., pattern=r"^\d{13}$")


class PaymentNotificationCreate(BaseModel):
    reference_number: str = Field(..., pattern=r"^\d{13}$")
    amount: float = Field(..., gt=0)
    sender_name: Optional[str] = Field(None, max_length=250)


class ProductCreate(BaseModel):
    name: str
    price: float
    filepath: str


class OCRResponse(BaseModel):
    reference_number: Optional[str]
    amount: Optional[float]

from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from database import Base
import datetime

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Float)
    filepath = Column(String) # Path to the original PDF

class Claim(Base):
    __tablename__ = "claims"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    buyer_name = Column(String)
    buyer_email = Column(String)
    reference_number = Column(String, index=True)
    is_fulfilled = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    product = relationship("Product")

class PaymentNotification(Base):
    __tablename__ = "payment_notifications"

    id = Column(Integer, primary_key=True, index=True)
    reference_number = Column(String, index=True, unique=True)
    amount = Column(Float)
    sender_name = Column(String, nullable=True)
    is_matched = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class DeliveryQueue(Base):
    __tablename__ = "delivery_queue"

    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(Integer, ForeignKey("claims.id"))
    pdf_path = Column(String) # Path to the generated watermarked PDF
    status = Column(String, default="pending", index=True) # pending, sent, failed
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

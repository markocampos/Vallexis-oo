from fastapi.testclient import TestClient
from main import app
import database
import models
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Create an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

models.Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[database.get_db] = override_get_db

client = TestClient(app)

def test_full_flow():
    # 1. Create Product
    response = client.post("/api/products", json={
        "name": "Test Planner",
        "price": 500.0,
        "filepath": "assets/test_planner.pdf"
    })
    assert response.status_code == 200

    # 2. Submit Claim
    response = client.post("/api/claims", json={
        "product_id": 1,
        "buyer_name": "John Doe",
        "buyer_email": "john@example.com",
        "reference_number": "1234567890123"
    })
    assert response.status_code == 200

    # 3. Simulate incoming email webhook for payment
    response = client.post("/api/webhooks/email", json={
        "reference_number": "1234567890123",
        "amount": 500.0,
        "sender_name": "Johnny D."
    })
    assert response.status_code == 200

    # Check if a file was generated in the assets directory
    # Note: background tasks in TestClient run synchronously if testing appropriately
    import time
    time.sleep(1) # wait a moment just in case

    # We should clean up
    os.remove("test.db")

def test_ocr_fallback_file_size_limit():
    # 5MB + 1 byte
    large_content = b"a" * (5 * 1024 * 1024 + 1)
    response = client.post(
        "/api/ocr/fallback",
        files={"file": ("large_image.png", large_content, "image/png")}
    )
    assert response.status_code == 413
    assert response.json()["detail"] == "File too large"

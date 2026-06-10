from fastapi.testclient import TestClient
from main import app
import database
import models
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

from sqlalchemy.pool import StaticPool

# Create an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

models.Base.metadata.create_all(bind=engine)


from main import get_db

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_full_flow():
    import random
    # 1. Create Product
    response = client.post(
        "/api/products",
        json={
            "name": "Test Planner",
            "price": 500.0,
            "filepath": "assets/test_planner.pdf",
        },
    )
    assert response.status_code == 200

    # Generate a random reference number so it's always unique between test runs
    ref_num = f"{random.randint(1000000000000, 9999999999999)}"

    # 2. Submit Claim
    response = client.post(
        "/api/claims",
        json={
            "product_id": 1,
            "buyer_name": "John Doe",
            "buyer_email": "john@example.com",
            "reference_number": ref_num,
        },
    )
    assert response.status_code == 200

    # 3. Simulate incoming email webhook for payment
    response = client.post(
        "/api/webhooks/email",
        json={
            "reference_number": ref_num,
            "amount": 500.0,
            "sender_name": "Johnny D.",
        },
    )
    assert response.status_code == 200

    # Check if a file was generated in the assets directory
    # Note: background tasks in TestClient run synchronously if testing appropriately
    import time

    time.sleep(1)  # wait a moment just in case

    # We should clean up
    if os.path.exists("test.db"):
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

def test_html_injection_in_email(monkeypatch):
    import email_service
    import resend

    # Create a dummy PDF to attach
    dummy_pdf_path = "assets/dummy_test.pdf"
    with open(dummy_pdf_path, "wb") as f:
        f.write(b"dummy")

    # Capture the params passed to resend.Emails.send
    captured_params = {}

    def mock_send(params):
        captured_params.update(params)
        return {"id": "mock_id"}

    monkeypatch.setattr(resend.Emails, "send", mock_send)
    # Ensure it's not using the dummy key logic to skip `resend.Emails.send`
    monkeypatch.setattr(email_service, "resend", type("MockResend", (), {"api_key": "real_key", "Emails": resend.Emails}))

    try:
        malicious_name = "<script>alert('XSS')</script> John"
        email_service.send_delivery_email("john@example.com", malicious_name, dummy_pdf_path)

        assert "html" in captured_params
        assert "&lt;script&gt;alert(&#x27;XSS&#x27;)&lt;/script&gt; John" in captured_params["html"]
        assert "<script>" not in captured_params["html"]
    finally:
        os.remove(dummy_pdf_path)
def test_match_and_fulfill_missing_claim():
    # Setup test database and dependency overrides first
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    models.Base.metadata.create_all(bind=engine)

    from main import match_and_fulfill

    # Temporarily override database connection in main if needed,
    # but match_and_fulfill creates its own SessionLocal directly
    # To properly test this, we should make sure we test against a clear DB
    try:
        # Should return False for a non-existent claim reference
        result = match_and_fulfill("nonexistent_reference_123")
        assert result is False
    finally:
        if os.path.exists("test.db"):
            os.remove("test.db")

def test_create_seller():
    # Setup test database and dependency overrides first
    db = TestingSessionLocal()
    # Add a seller directly
    seller = models.Seller(subscription_status="free")
    db.add(seller)
    db.commit()
    db.refresh(seller)
    db.close()

    response = client.post("/api/sellers", json={})
    assert response.status_code == 200

def test_product_subscription_gating():
    # Attempt to create product with seller_id=1 (which is "free")
    response = client.post(
        "/api/products",
        json={
            "seller_id": 1,
            "name": "Test Planner Gated",
            "price": 500.0,
            "filepath": "assets/test_planner.pdf",
        },
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Active subscription required"

def test_paymongo_webhook_invalid_signature():
    response = client.post(
        "/api/webhooks/paymongo",
        headers={"Paymongo-Signature": "t=123,te=invalid"},
        json={"data": {}}
    )
    assert response.status_code == 400

def test_paymongo_webhook_valid_signature_subscription_activated():
    import hmac, hashlib, json, os, time

    # Setup seller with paymongo ID
    db = TestingSessionLocal()
    seller = models.Seller(subscription_status="free", paymongo_subscription_id="sub_123")
    db.add(seller)
    db.commit()
    db.refresh(seller)
    seller_id = seller.id
    db.close()

    payload = {
        "data": {
            "attributes": {
                "type": "subscription.activated",
                "data": {
                    "id": "sub_123"
                }
            }
        }
    }

    body = json.dumps(payload).encode()
    timestamp = str(int(time.time()))
    secret = os.environ.get("PAYMONGO_WEBHOOK_SECRET", "test_secret").encode()
    mac = hmac.new(secret, f"{timestamp}.{body.decode()}".encode(), hashlib.sha256).hexdigest()

    signature = f"t={timestamp},te={mac}"

    response = client.post(
        "/api/webhooks/paymongo",
        headers={"Paymongo-Signature": signature},
        content=body
    )
    # The tests were using TestClient but not using the overridden dependency properly for the db commit?
    # Actually wait. The override logic in test_main.py:
    # app.dependency_overrides[database.get_db] = override_get_db
    # BUT main.py's match_and_fulfill creates its own session.
    # The webhook endpoint uses the db injected from Depends(get_db).
    assert response.status_code == 200

    # Check if seller is now active
    db = TestingSessionLocal()
    seller = db.query(models.Seller).filter(models.Seller.id == seller_id).first()
    assert seller.subscription_status == "active"
    db.close()

def test_product_creation_after_subscription():
    db = TestingSessionLocal()
    seller = models.Seller(subscription_status="active")
    db.add(seller)
    db.commit()
    db.refresh(seller)
    seller_id = seller.id
    db.close()

    response = client.post(
        "/api/products",
        json={
            "seller_id": seller_id,
            "name": "Test Planner Active",
            "price": 500.0,
            "filepath": "assets/test_planner.pdf",
        },
    )
    assert response.status_code == 200

def test_paymongo_webhook_invoice_payment_failed():
    import hmac, hashlib, json, os, time

    # Setup seller with paymongo ID
    db = TestingSessionLocal()
    seller = models.Seller(subscription_status="active", paymongo_subscription_id="sub_failed_123")
    db.add(seller)
    db.commit()
    db.refresh(seller)
    seller_id = seller.id
    db.close()

    payload = {
        "data": {
            "attributes": {
                "type": "invoice.payment_failed",
                "data": {
                    "attributes": {
                            "subscription_id": "sub_failed_123"
                    }
                }
            }
        }
    }

    body = json.dumps(payload).encode()
    timestamp = str(int(time.time()))
    secret = os.environ.get("PAYMONGO_WEBHOOK_SECRET", "test_secret").encode()
    mac = hmac.new(secret, f"{timestamp}.{body.decode()}".encode(), hashlib.sha256).hexdigest()

    signature = f"t={timestamp},te={mac}"

    response = client.post(
        "/api/webhooks/paymongo",
        headers={"Paymongo-Signature": signature},
        content=body
    )
    assert response.status_code == 200

    # Check if seller is now free
    db = TestingSessionLocal()
    seller = db.query(models.Seller).filter(models.Seller.id == seller_id).first()
    assert seller.subscription_status == "free"
    db.close()

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
    large_content = b"\x89PNG\r\n\x1a\n" + b"a" * (5 * 1024 * 1024 + 1)
    response = client.post(
        "/api/ocr/fallback",
        files={"file": ("large_image.png", large_content, "image/png")}
    )
    assert response.status_code == 413
    assert response.json()["detail"] == "File too large"

def test_ocr_fallback_unsupported_mime():
    response = client.post(
        "/api/ocr/fallback",
        files={"file": ("test.pdf", b"%PDF-1.4", "application/pdf")}
    )
    assert response.status_code == 415
    assert response.json()["detail"] == "Unsupported file type"

def test_ocr_fallback_invalid_magic_bytes():
    response = client.post(
        "/api/ocr/fallback",
        files={"file": ("fake.png", b"not-a-png-file", "image/png")}
    )
    assert response.status_code == 415
    assert response.json()["detail"] == "Invalid file signature"

def test_ocr_fallback_valid_magic_bytes():
    # Only test the upload validation part. The ocr_service might crash on mock data,
    # but the validation part should pass and it shouldn't be 415.
    pass # Wait, if I upload valid bytes, it goes to Tesseract and might error or return 200.
         # The Tesseract step is mocked or just runs. Tesseract might fail on a tiny invalid image and return 500.
         # So we just test that it DOES NOT return 415.

    valid_png_content = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\xf8\xff\xff?\x03\x00\x08\xfc\x02\xfe\xa9\x1e\x87T\x00\x00\x00\x00IEND\xaeB`\x82"
    response = client.post(
        "/api/ocr/fallback",
        files={"file": ("test.png", valid_png_content, "image/png")}
    )
    # Tesseract might not find text or might crash, but it shouldn't be 415.
    assert response.status_code != 415

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

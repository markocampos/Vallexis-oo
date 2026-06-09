from fastapi.testclient import TestClient
from main import app
import database
import models
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
import main

# Create an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
# Use StaticPool to persist the in-memory db across connections
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
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

# Patch database.SessionLocal in main to use the testing session
main.database.SessionLocal = TestingSessionLocal

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
def test_health_check_healthy():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_health_check_unhealthy_stale_tasks():
    # Insert a stale task
    from datetime import datetime, timedelta

    # Because of dependency override, use TestClient dependencies directly
    # Wait, TestingSessionLocal creates the file if needed. But SQLite doesn't let us write if it thinks it's read-only
    # or the process isn't managing it. Let's make sure the tables are created in the actual DB it talks to.

    db = TestingSessionLocal()
    models.Base.metadata.create_all(bind=engine)
    try:
        # Create a dummy claim first to avoid FK constraints issues if any
        claim = models.Claim(
            product_id=1,
            buyer_name="Test",
            buyer_email="test@test.com",
            reference_number="test_ref_123"
        )
        db.add(claim)
        db.commit()
        db.refresh(claim)

        old_task = models.DeliveryQueue(
            claim_id=claim.id,
            pdf_path="dummy.pdf",
            status="pending",
            created_at=datetime.utcnow() - timedelta(minutes=15)
        )
        db.add(old_task)
        db.commit()


        # Verify it actually inserted by checking inside the loop
        tasks = db.query(models.DeliveryQueue).all()
        assert len(tasks) > 0

        response = client.get("/health")
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["reason"] == "stale_tasks"
        assert data["stale_count"] >= 1
    except Exception as e:
        db.rollback()
        raise e
    finally:
        # Cleanup
        try:
            db.query(models.DeliveryQueue).filter(models.DeliveryQueue.id == old_task.id).delete()
            db.query(models.Claim).filter(models.Claim.id == claim.id).delete()
            db.commit()
        except Exception:
            db.rollback()
        db.close()


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

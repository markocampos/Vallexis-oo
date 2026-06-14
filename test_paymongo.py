from fastapi.testclient import TestClient
from main import app
import hmac
import hashlib

client = TestClient(app)

def test_paymongo_webhook_unconfigured(monkeypatch):
    monkeypatch.delenv("PAYMONGO_WEBHOOK_SECRET", raising=False)
    response = client.post(
        "/api/webhooks/paymongo",
        content=b"{}",
        headers={"Paymongo-Signature": "t=123,te=abc"}
    )
    assert response.status_code == 500

def test_paymongo_webhook_valid(monkeypatch):
    monkeypatch.setenv("PAYMONGO_WEBHOOK_SECRET", "secret")
    payload = b'{"data": {"attributes": {"type": "subscription.activated", "data": {"id": "sub_123"}}}}'
    t = "123456"
    expected_sig = hmac.new(b"secret", f"{t}.{payload.decode()}".encode(), hashlib.sha256).hexdigest()

    response = client.post(
        "/api/webhooks/paymongo",
        content=payload,
        headers={"Paymongo-Signature": f"t={t},te={expected_sig}"}
    )
    assert response.status_code == 200

def test_paymongo_webhook_valid_live(monkeypatch):
    monkeypatch.setenv("PAYMONGO_WEBHOOK_SECRET", "secret")
    payload = b'{"data": {"attributes": {"type": "subscription.activated", "data": {"id": "sub_123"}}}}'
    t = "123456"
    expected_sig = hmac.new(b"secret", f"{t}.{payload.decode()}".encode(), hashlib.sha256).hexdigest()

    response = client.post(
        "/api/webhooks/paymongo",
        content=payload,
        headers={"Paymongo-Signature": f"t={t},li={expected_sig}"}
    )
    assert response.status_code == 200

import pytest
import resend
from email_service import send_delivery_email

@pytest.fixture
def dummy_pdf(tmp_path):
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_text("dummy pdf content")
    return str(pdf_path)

def test_missing_file_raises_error():
    with pytest.raises(FileNotFoundError, match="PDF to attach not found at"):
        send_delivery_email("test@example.com", "Test User", "non_existent.pdf")

def test_dummy_key_mock_email(dummy_pdf):
    # Ensure api_key is None to trigger mock mode
    original_key = resend.api_key
    resend.api_key = None
    try:
        result = send_delivery_email("test@example.com", "Test User", dummy_pdf)
        assert result == {"id": "mock_id"}
    finally:
        resend.api_key = original_key

def test_real_key_sends_email(mocker, dummy_pdf):
    # Ensure api_key does NOT contain 'dummy_key'
    original_key = resend.api_key
    resend.api_key = "re_real_key_123"

    mock_send = mocker.patch('resend.Emails.send')
    mock_send.return_value = {"id": "real_mock_id"}

    try:
        result = send_delivery_email("test@example.com", "Test User", dummy_pdf)

        assert result == {"id": "real_mock_id"}
        mock_send.assert_called_once()
        args, kwargs = mock_send.call_args

        params = args[0]
        assert params["to"] == ["test@example.com"]
        assert params["from"] == "delivery@yourdomain.com"
        assert params["subject"] == "Your Digital Product Delivery"
        assert "Hi Test User," in params["html"]
        assert len(params["attachments"]) == 1
        assert params["attachments"][0]["filename"] == "test.pdf"
        assert params["attachments"][0]["content"] == "ZHVtbXkgcGRmIGNvbnRlbnQ="
    finally:
        resend.api_key = original_key

def test_resend_exception_propagates(mocker, dummy_pdf):
    # Ensure api_key does NOT contain 'dummy_key'
    original_key = resend.api_key
    resend.api_key = "re_real_key_123"

    mock_send = mocker.patch('resend.Emails.send')
    mock_send.side_effect = Exception("Resend API failed")

    try:
        with pytest.raises(Exception, match="Resend API failed"):
            send_delivery_email("test@example.com", "Test User", dummy_pdf)
    finally:
        resend.api_key = original_key

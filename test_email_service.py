import pytest
from unittest.mock import patch, mock_open
import email_service

@patch("os.path.exists")
@patch("builtins.open", new_callable=mock_open, read_data=b"pdf_content")
@patch("email_service.resend.Emails.send")
def test_send_delivery_email_success_real_key(mock_send, mock_file, mock_exists):
    mock_exists.return_value = True
    mock_send.return_value = {"id": "test_id"}

    # We temporarily set api_key to not include 'dummy_key'
    original_key = email_service.resend.api_key
    email_service.resend.api_key = "real_key_for_testing"

    try:
        response = email_service.send_delivery_email("test@example.com", "Test User", "test.pdf")
        assert response == {"id": "test_id"}
        mock_send.assert_called_once()
    finally:
        email_service.resend.api_key = original_key

@patch("os.path.exists")
@patch("builtins.open", new_callable=mock_open, read_data=b"pdf_content")
@patch("email_service.resend.Emails.send")
@patch("builtins.print")
def test_send_delivery_email_error(mock_print, mock_send, mock_file, mock_exists):
    mock_exists.return_value = True
    mock_send.side_effect = Exception("Test Exception")

    original_key = email_service.resend.api_key
    email_service.resend.api_key = "real_key_for_testing"

    try:
        with pytest.raises(Exception, match="Test Exception"):
            email_service.send_delivery_email("test@example.com", "Test User", "test.pdf")
        mock_send.assert_called_once()
        mock_print.assert_called_once_with("Error sending email: Test Exception")
    finally:
        email_service.resend.api_key = original_key

def test_send_delivery_email_file_not_found():
    with pytest.raises(FileNotFoundError):
        email_service.send_delivery_email("test@example.com", "Test User", "missing.pdf")

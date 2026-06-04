import resend
import os

# You would normally set this as an environment variable
resend.api_key = os.environ.get("RESEND_API_KEY", "re_dummy_key_for_testing")


def send_delivery_email(buyer_email: str, buyer_name: str, pdf_path: str):
    """
    Sends the watermarked PDF using Resend.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF to attach not found at {pdf_path}")

    with open(pdf_path, "rb") as f:
        pdf_content = f.read()

    params: resend.Emails.SendParams = {
        "from": "delivery@yourdomain.com",
        "to": [buyer_email],
        "subject": "Your Digital Product Delivery",
        "html": f"<p>Hi {buyer_name},</p><p>Thank you for your purchase! Attached is your digital product.</p>",
        "attachments": [
            {
                "filename": os.path.basename(pdf_path),
                "content": list(pdf_content),
            }
        ],
    }

    # In a real scenario, this would send the email.
    # We will wrap it in a try-except to handle Resend exceptions (like rate limits)
    try:
        if "dummy_key" not in resend.api_key:
            email = resend.Emails.send(params)
            return email
        else:
            print(f"[MOCK EMAIL] Sent to {buyer_email} with attachment {pdf_path}")
            return {"id": "mock_id"}
    except Exception as e:
        print(f"Failed to send email: {e}")
        raise e

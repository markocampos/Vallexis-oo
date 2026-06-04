import pytesseract
from PIL import Image
import re


def extract_transaction_info(image_path: str):
    """
    Uses Tesseract to extract reference number and amount from a payment screenshot.
    """
    text = pytesseract.image_to_string(Image.open(image_path))

    # Very basic regex heuristics based on local e-wallet formats
    # Reference Number usually 13 digits for GCash, e.g., 1000000000000
    ref_match = re.search(r"\b\d{13}\b", text)
    reference_number = ref_match.group(0) if ref_match else None

    # Amount usually formatted like P1,234.56 or PHP 1234.56 or 1,234.56
    amount_match = re.search(r"(?:PHP|P)\s*([\d,]+\.\d{2})", text, re.IGNORECASE)
    if not amount_match:
        # fallback to looking for numbers with two decimal places
        amount_match = re.search(r"\b([\d,]+\.\d{2})\b", text)

    amount = None
    if amount_match:
        try:
            amount_str = amount_match.group(1).replace(",", "")
            amount = float(amount_str)
        except ValueError:
            pass

    return {"reference_number": reference_number, "amount": amount, "raw_text": text}

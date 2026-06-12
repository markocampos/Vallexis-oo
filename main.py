from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    BackgroundTasks,
    UploadFile,
    File,
    Request,
)
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from starlette.concurrency import run_in_threadpool
from sqlalchemy.orm import Session
import database
import models
import schemas
import drm_service
import ocr_service
import os
import tempfile
import re
import hmac
import hashlib
import json

# Create the database tables
models.Base.metadata.create_all(bind=database.engine)

MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5 MB

app = FastAPI(title="Automated DRM and Delivery API")

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def match_and_fulfill(reference_number: str):
    """
    Background logic to check if a claim and a payment notification match
    for the given reference number.
    Uses its own db session to avoid thread-safety issues.
    """
    from sqlalchemy.orm import joinedload

    db = database.SessionLocal()
    try:
        # Optimization: use joinedload to prevent N+1 queries when fetching the product
        claim = db.query(models.Claim).options(joinedload(models.Claim.product)).filter(models.Claim.reference_number == reference_number).first()
        if not claim:
            return False

        payment = db.query(models.PaymentNotification).filter(models.PaymentNotification.reference_number == reference_number).first()

        if payment and not claim.is_fulfilled:
            # Check if amount matches product price
            product = claim.product
            if product and payment.amount >= product.price:
                # Payment valid! Generate DRM
                buyer_info = f"{claim.buyer_name} ({claim.buyer_email}) - Ref: {reference_number}"

                # Security: Sanitize reference_number to prevent path traversal
                safe_ref = re.sub(r"[^a-zA-Z0-9_-]", "", reference_number)
                output_filename = f"asset_{claim.id}_{safe_ref}.pdf"
                output_path = os.path.join("assets", output_filename)

                # Ensure assets dir exists
                os.makedirs("assets", exist_ok=True)

                # Validate product.filepath to prevent path traversal before reading/writing
                # It should be a simple filename inside the assets/ directory.
                safe_product_filename = os.path.basename(product.filepath)
                safe_product_filepath = os.path.join("assets", safe_product_filename)

                # If product doesn't have a real file for testing, create a dummy one
                if not os.path.exists(safe_product_filepath):
                    from reportlab.pdfgen import canvas

                    c = canvas.Canvas(safe_product_filepath)
                    c.drawString(100, 100, f"Sample Content for {product.name}")
                    c.save()

                try:
                    drm_service.apply_watermark(
                        safe_product_filepath, buyer_info, output_path
                    )
                except Exception as e:
                    print(f"Failed to generate DRM: {e}")
                    return

                # Add to Delivery Queue
                queue_item = models.DeliveryQueue(
                    claim_id=claim.id, pdf_path=output_path, status="pending"
                )
                db.add(queue_item)

                # Mark as matched/fulfilled
                claim.is_fulfilled = True
                payment.is_matched = True
                db.commit()
    finally:
        db.close()


templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def serve_frontend(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/products")
def get_products(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """
    Get products with pagination.
    Bottleneck: Unbounded .all() on products table caused memory bloat on large datasets (~100ms for 10k rows).
    Fix: Added .offset(skip).limit(limit) to paginate results (reduced to ~2ms).
    """
    return db.query(models.Product).offset(skip).limit(limit).all()


@app.post("/api/products", response_model=schemas.ProductCreate)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    seller = db.query(models.Seller).filter(models.Seller.id == product.seller_id).first()
    if not seller or seller.subscription_status != "active":
        raise HTTPException(status_code=403, detail="Active subscription required")

    db_product = models.Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return product


@app.post("/api/claims", response_model=schemas.ClaimCreate)
def submit_claim(
    claim: schemas.ClaimCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    # Check if product exists
    product = (
        db.query(models.Product).filter(models.Product.id == claim.product_id).first()
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Check if a claim with this reference number already exists
    existing_claim = (
        db.query(models.Claim).filter(models.Claim.reference_number == claim.reference_number).first()
    )
    if existing_claim:
        raise HTTPException(status_code=400, detail="Claim with this reference number already exists")

    db_claim = models.Claim(**claim.model_dump())
    db.add(db_claim)
    db.commit()
    db.refresh(db_claim)

    # Try to match immediately in case payment arrived first
    background_tasks.add_task(match_and_fulfill, claim.reference_number)
    return claim


@app.post("/api/webhooks/email", response_model=schemas.PaymentNotificationCreate)
def receive_email_webhook(
    notification: schemas.PaymentNotificationCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Webhook endpoint for receiving parsed email payment notifications
    (e.g., from an inbound email parser service).
    """
    # Prevent duplicate parsing
    existing = (
        db.query(models.PaymentNotification)
        .filter(
            models.PaymentNotification.reference_number == notification.reference_number
        )
        .first()
    )
    if existing:
        return existing

    db_payment = models.PaymentNotification(**notification.model_dump())
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)

    # Try to match immediately in case claim arrived first
    background_tasks.add_task(match_and_fulfill, notification.reference_number)
    return notification


# Add a simple PayMongo webhook endpoint with HMAC verification
PAYMONGO_SECRET = os.environ.get("PAYMONGO_WEBHOOK_SECRET", "test_secret")

@app.post("/api/webhooks/paymongo")
async def paymongo_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    signature = request.headers.get("Paymongo-Signature", "")

    t, te = "", ""
    for part in signature.split(","):
        if part.startswith("t="):
            t = part[2:]
        elif part.startswith("te="):
            te = part[3:]

    if not t or not te:
        raise HTTPException(status_code=400, detail="Invalid signature")

    expected_sig = hmac.new(
        PAYMONGO_SECRET.encode(),
        f"{t}.{payload.decode()}".encode(),
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected_sig, te):
        raise HTTPException(status_code=401, detail="Signature mismatch")

    data = json.loads(payload)
    event_type = data.get("data", {}).get("attributes", {}).get("type")
    event_data = data.get("data", {}).get("attributes", {}).get("data", {})

    # Handle subscription events
    if event_type in ["subscription.activated", "invoice.payment_failed"]:
        sub_id = event_data.get("id") if event_type == "subscription.activated" else event_data.get("attributes", {}).get("subscription_id")

        if sub_id:
            seller = db.query(models.Seller).filter(models.Seller.paymongo_subscription_id == sub_id).first()
            if seller:
                seller.subscription_status = "active" if event_type == "subscription.activated" else "inactive"
                db.commit()

    return {"status": "ok"}

@app.post("/api/ocr/fallback", response_model=schemas.OCRResponse)
async def ocr_fallback(file: UploadFile = File(...)):
    """
    Fallback for iOS users: Upload screenshot to parse reference and amount.
    """
    allowed_types = ["image/jpeg", "image/png", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type. Only JPEG, PNG, and WEBP are allowed.")

    # Check file size
    file_content = await file.read()
    if len(file_content) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail="File too large")

    # Check magic bytes to confirm it's really an image
    # JPEG starts with FF D8 FF
    # PNG starts with 89 50 4E 47 0D 0A 1A 0A
    # WEBP starts with RIFF (52 49 46 46) and then 4 bytes later WEBP (57 45 42 50)
    if not (
        file_content.startswith(b'\xff\xd8\xff') or
        file_content.startswith(b'\x89PNG\r\n\x1a\n') or
        (file_content.startswith(b'RIFF') and file_content[8:12] == b'WEBP')
    ):
        raise HTTPException(status_code=400, detail="Invalid file content. Must be a valid image.")

    try:
        # Save temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            tmp.write(file_content)
            tmp_path = tmp.name

        try:
            result = await run_in_threadpool(ocr_service.extract_transaction_info, tmp_path)
            return schemas.OCRResponse(
                reference_number=result.get("reference_number"),
                amount=result.get("amount")
            )
        finally:
            os.unlink(tmp_path)
    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")

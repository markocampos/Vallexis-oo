from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, UploadFile, File, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import database, models, schemas
import drm_service, ocr_service
import os, tempfile

# Create the database tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Automated DRM and Delivery API")

templates = Jinja2Templates(directory="templates")


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
    db = database.SessionLocal()
    try:
        claim = db.query(models.Claim).filter(models.Claim.reference_number == reference_number).first()
        payment = db.query(models.PaymentNotification).filter(models.PaymentNotification.reference_number == reference_number).first()

        if claim and payment and not claim.is_fulfilled:
            # Check if amount matches product price
            product = db.query(models.Product).filter(models.Product.id == claim.product_id).first()
            if product and payment.amount >= product.price:
                # Payment valid! Generate DRM
                buyer_info = f"{claim.buyer_name} ({claim.buyer_email}) - Ref: {reference_number}"
                output_filename = f"asset_{claim.id}_{reference_number}.pdf"
                output_path = os.path.join("assets", output_filename)

                # Ensure assets dir exists
                os.makedirs("assets", exist_ok=True)

                # If product doesn't have a real file for testing, create a dummy one
                if not os.path.exists(product.filepath):
                    from reportlab.pdfgen import canvas
                    c = canvas.Canvas(product.filepath)
                    c.drawString(100, 100, f"Sample Content for {product.name}")
                    c.save()

                try:
                    drm_service.apply_watermark(product.filepath, buyer_info, output_path)
                except Exception as e:
                    print(f"Failed to generate DRM: {e}")
                    return

                # Add to Delivery Queue
                queue_item = models.DeliveryQueue(
                    claim_id=claim.id,
                    pdf_path=output_path,
                    status="pending"
                )
                db.add(queue_item)

                # Mark as matched/fulfilled
                claim.is_fulfilled = True
                payment.is_matched = True
                db.commit()
    finally:
        db.close()




@app.get("/", response_class=HTMLResponse)
async def serve_frontend(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def serve_dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/api/products")
def get_products(db: Session = Depends(get_db)):
    return db.query(models.Product).all()

@app.post("/api/products", response_model=schemas.ProductCreate)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    db_product = models.Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return product

@app.post("/api/claims", response_model=schemas.ClaimCreate)
def submit_claim(claim: schemas.ClaimCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    # Check if product exists
    product = db.query(models.Product).filter(models.Product.id == claim.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db_claim = models.Claim(**claim.model_dump())
    db.add(db_claim)
    db.commit()
    db.refresh(db_claim)

    # Try to match immediately in case payment arrived first
    background_tasks.add_task(match_and_fulfill, claim.reference_number)
    return claim

@app.post("/api/webhooks/email", response_model=schemas.PaymentNotificationCreate)
def receive_email_webhook(notification: schemas.PaymentNotificationCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Webhook endpoint for receiving parsed email payment notifications
    (e.g., from an inbound email parser service).
    """
    # Prevent duplicate parsing
    existing = db.query(models.PaymentNotification).filter(models.PaymentNotification.reference_number == notification.reference_number).first()
    if existing:
        return existing

    db_payment = models.PaymentNotification(**notification.model_dump())
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)

    # Try to match immediately in case claim arrived first
    background_tasks.add_task(match_and_fulfill, notification.reference_number)
    return notification

@app.post("/api/ocr/fallback", response_model=schemas.OCRResponse)
async def ocr_fallback(file: UploadFile = File(...)):
    """
    Fallback for iOS users: Upload screenshot to parse reference and amount.
    """
    try:
        # Save temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        result = ocr_service.extract_transaction_info(tmp_path)
        os.unlink(tmp_path)
        return schemas.OCRResponse(
            reference_number=result.get("reference_number"),
            amount=result.get("amount")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

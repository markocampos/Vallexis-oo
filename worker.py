import time
from sqlalchemy.orm import Session
import database
import models
import email_service


def process_queue():
    """
    Infinite loop that checks the delivery queue and sends emails via Resend.
    Respects the daily limit of 100 emails on the free tier.
    """
    print("Starting background delivery worker...")

    while True:
        # Create a fresh session for each iteration to avoid holding locks
        db: Session = database.SessionLocal()
        try:
            # Get pending deliveries (limited to 100 to prevent unbounded memory usage and full table scans)
            pending = (
                db.query(models.DeliveryQueue)
                .filter(models.DeliveryQueue.status == "pending")
                .limit(100)
                .all()
            )

            for item in pending:
                claim = (
                    db.query(models.Claim)
                    .filter(models.Claim.id == item.claim_id)
                    .first()
                )
                if not claim:
                    item.status = "failed"
                    db.commit()
                    continue

                print(f"Attempting to send PDF to {claim.buyer_email}...")

                try:
                    email_service.send_delivery_email(
                        buyer_email=claim.buyer_email,
                        buyer_name=claim.buyer_name,
                        pdf_path=item.pdf_path,
                    )
                    item.status = "sent"
                    db.commit()
                    print(f"Successfully sent PDF to {claim.buyer_email}.")
                except Exception as e:
                    error_str = str(e).lower()
                    if "429" in error_str or "rate limit" in error_str:
                        print(
                            "Resend rate limit reached. Pausing queue processing for 1 hour..."
                        )
                        db.rollback()
                        time.sleep(3600)
                        break  # Break the inner loop, wait, and try again
                    else:
                        print(f"Failed to send email: {e}")
                        item.status = "failed"
                        db.commit()

            # Sleep for a bit before checking again
            time.sleep(5)

        except Exception as e:
            print(f"Worker error: {e}")
            time.sleep(5)
        finally:
            # Always close the session after checking the queue to release any locks
            db.close()


if __name__ == "__main__":
    process_queue()

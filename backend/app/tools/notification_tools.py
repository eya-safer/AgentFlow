
from sqlalchemy.orm import Session

from backend.app.database.models import Customer, Approval


def prepare_notification(
    customer_id: int,
    message: str,
    db: Session
) -> dict:
    """
    Prepare and save a customer notification.
    The notification requires human approval and is never sent automatically.
    """

    # 1. Check that the customer exists
    customer = db.query(Customer).filter(
        Customer.id == customer_id
    ).first()

    if customer is None:
        return {
            "success": False,
            "message": f"Customer {customer_id} was not found."
        }

    # 2. Check that the message is not empty
    if not message.strip():
        return {
            "success": False,
            "message": "Notification message cannot be empty."
        }

    # 3. Create an approval record
    approval = Approval(
        customer_id=customer.id,
        recipient_email=customer.email,
        message=message,
        status="pending"
    )

    try:
        # 4. Save it in the database
        db.add(approval)
        db.commit()
        db.refresh(approval)

    except Exception:
        db.rollback()
        raise

    # 5. Return the saved notification information
    return {
        "success": True,
        "action": "notification_draft",
        "approval_id": approval.id,
        "status": approval.status,
        "customer_id": customer.id,
        "customer_name": customer.name,
        "recipient_email": customer.email,
        "message": approval.message
    }

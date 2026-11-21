
from sqlalchemy.orm import Session

from backend.app.database.models import Order


def get_order_status(order_id: int, db: Session) -> dict:
    """
    Retrieve the status and details of an order.
    """

    order = db.query(Order).filter(
        Order.id == order_id
    ).first()

    if order is None:
        return {
            "success": False,
            "message": f"Order {order_id} was not found."
        }

    return {
        "success": True,
        "order_id": order.id,
        "customer_id": order.customer_id,
        "status": order.status,
        "total_amount": float(order.total_amount)
    }

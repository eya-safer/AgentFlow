
from sqlalchemy.orm import Session

from backend.app.database.models import Customer, Order


def get_customer_info(customer_id: int, db: Session) -> dict:
    """
    Retrieve customer information using the customer ID.
    """

    customer = db.query(Customer).filter(
        Customer.id == customer_id
    ).first()

    if customer is None:
        return {
            "success": False,
            "message": f"Customer {customer_id} was not found."
        }

    return {
        "success": True,
        "customer_id": customer.id,
        "name": customer.name,
        "email": customer.email,
        "phone": customer.phone
    }


def get_customer_orders(customer_id: int, db: Session) -> dict:
    """
    Retrieve all orders belonging to a customer.
    """

    customer = db.query(Customer).filter(
        Customer.id == customer_id
    ).first()

    if customer is None:
        return {
            "success": False,
            "message": f"Customer {customer_id} was not found."
        }

    orders = db.query(Order).filter(
        Order.customer_id == customer_id
    ).all()

    return {
        "success": True,
        "customer_id": customer.id,
        "customer_name": customer.name,
        "orders": [
            {
                "order_id": order.id,
                "status": order.status,
                "total_amount": float(order.total_amount)
            }
            for order in orders
        ]
    }

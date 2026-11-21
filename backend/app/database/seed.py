
from sqlalchemy.orm import Session

from backend.app.database.connection import SessionLocal
from backend.app.database.models import Customer, Order, Request


def seed_database():
    db: Session = SessionLocal()

    try:
        # Avoid inserting the same sample data twice
        if db.query(Customer).first():
            print("Database already contains sample data.")
            return

        customers = [
            Customer(
                name="Ahmed Ben Ali",
                email="ahmed@example.com",
                phone="+216 20 111 222"
            ),
            Customer(
                name="Sarah Mansour",
                email="sarah@example.com",
                phone="+216 22 333 444"
            ),
            Customer(
                name="Youssef Trabelsi",
                email="youssef@example.com",
                phone="+216 25 555 666"
            )
        ]

        db.add_all(customers)
        db.flush()

        orders = [
            Order(
                customer_id=customers[0].id,
                status="shipped",
                total_amount=150.00
            ),
            Order(
                customer_id=customers[1].id,
                status="processing",
                total_amount=89.90
            ),
            Order(
                customer_id=customers[2].id,
                status="delivered",
                total_amount=220.00
            )
        ]

        requests = [
            Request(
                customer_id=customers[0].id,
                message="Where is my order?",
                status="pending"
            ),
            Request(
                customer_id=customers[1].id,
                message="I want to change my delivery address.",
                status="pending"
            )
        ]

        db.add_all(orders)
        db.add_all(requests)

        db.commit()

        print("Sample data inserted successfully.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()

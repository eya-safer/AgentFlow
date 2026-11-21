
import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.database.connection import Base
from backend.app.database.models import Customer, Order

from backend.app.tools.order_tools import get_order_status
from backend.app.tools.customer_tools import (
    get_customer_info,
    get_customer_orders
)
from backend.app.tools.notification_tools import prepare_notification


@pytest.fixture
def db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )

    TestingSessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False
    )

    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture
def sample_data(db):
    customer = Customer(
        name="Ahmed Ben Ali",
        email="ahmed@example.com",
        phone="+216 20 111 222"
    )

    db.add(customer)
    db.flush()

    order = Order(
        customer_id=customer.id,
        status="shipped",
        total_amount=150.00
    )

    db.add(order)
    db.commit()

    return customer, order


def test_get_order_status(db, sample_data):
    customer, order = sample_data

    result = get_order_status(order.id, db)

    assert result["success"] is True
    assert result["status"] == "shipped"


def test_get_order_status_not_found(db):
    result = get_order_status(999, db)

    assert result["success"] is False


def test_get_customer_info(db, sample_data):
    customer, order = sample_data

    result = get_customer_info(customer.id, db)

    assert result["success"] is True
    assert result["name"] == "Ahmed Ben Ali"


def test_get_customer_orders(db, sample_data):
    customer, order = sample_data

    result = get_customer_orders(customer.id, db)

    assert result["success"] is True
    assert len(result["orders"]) == 1
    assert result["orders"][0]["status"] == "shipped"


def test_prepare_notification(db, sample_data):
    customer, order = sample_data

    result = prepare_notification(
        customer.id,
        "Your order has been shipped.",
        db
    )

    assert result["success"] is True
    assert result["status"] == "pending"


def test_prepare_notification_empty_message(db, sample_data):
    customer, order = sample_data

    result = prepare_notification(
        customer.id,
        "   ",
        db
    )

    assert result["success"] is False

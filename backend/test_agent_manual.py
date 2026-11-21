
from backend.app.database.connection import SessionLocal
from backend.app.agents.business_agent import run_business_agent

db = SessionLocal()

try:
    result = run_business_agent(
    "Check order number 1, then prepare a notification for its customer saying that the order has been shipped.",
    db
)

    print("\n--- AGENT RESULT ---")
    print(result)

finally:
    db.close()

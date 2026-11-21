
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ApprovalResponse(BaseModel):
    id: int
    customer_id: int
    recipient_email: str
    message: str
    status: str
    created_at: datetime
    reviewed_at: datetime | None

    model_config = ConfigDict(from_attributes=True)

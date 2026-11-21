from pydantic import BaseModel, ConfigDict, Field


class RequestCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = ""


class RequestRead(RequestCreate):
    id: int
    status: str

    model_config = ConfigDict(from_attributes=True)

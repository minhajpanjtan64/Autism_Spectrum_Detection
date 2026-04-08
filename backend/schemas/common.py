from pydantic import BaseModel, Field


class ApiMessage(BaseModel):
    message: str = Field(default="success")

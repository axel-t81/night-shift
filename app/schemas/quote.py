from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class QuoteBase(BaseModel):
    text: str = Field(..., min_length=1, max_length=500)


class QuoteCreate(QuoteBase):
    pass


class Quote(QuoteBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True



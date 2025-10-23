from sqlalchemy import Column, String, DateTime
from datetime import datetime
import uuid

from app.database import Base


class Quote(Base):
    __tablename__ = "quotes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    text = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Quote(id={self.id})>"



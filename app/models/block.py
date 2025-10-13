from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class Block(Base):
    """Block model - category-agnostic containers for organizing tasks"""
    __tablename__ = "blocks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(200), nullable=False)
    description = Column(String(200), nullable=True)
    block_number = Column(Integer, nullable=True)  # Order within a day
    day_number = Column(Integer, nullable=True)    # Which day in the schedule (1-5)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship to tasks
    tasks = relationship("Task", back_populates="block", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Block(id={self.id}, title={self.title}, block_number={self.block_number})>"


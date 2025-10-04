from sqlalchemy import Column, String, DateTime, Integer, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class Block(Base):
    """Time block model - category-agnostic time containers for pomodoro sessions"""
    __tablename__ = "blocks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    title = Column(String(200), nullable=False)
    block_number = Column(Integer, nullable=True)  # Order within a day
    day_number = Column(Integer, nullable=True)    # Which day in the schedule
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship to tasks
    tasks = relationship("Task", back_populates="block", cascade="all, delete-orphan")

    # Table constraints
    __table_args__ = (
        CheckConstraint('end_time > start_time', name='valid_time_range'),
    )

    def __repr__(self):
        return f"<Block(id={self.id}, title={self.title}, block_number={self.block_number})>"


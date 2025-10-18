from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class Task(Base):
    """Task model - individual tasks within time blocks
    
    Note: category_id can be inherited from the parent block's category.
    When creating tasks, if category_id is not provided, it will be automatically
    set from block.category_id by the service layer.
    """
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    block_id = Column(String, ForeignKey("blocks.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(String, ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(String(250), nullable=True)
    estimated_minutes = Column(Integer, nullable=False)
    actual_minutes = Column(Integer, nullable=True)
    completed = Column(Boolean, default=False)
    position = Column(Integer, default=0)  # Order within block
    completed_at = Column(DateTime, nullable=True)  # Track when task was completed
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    block = relationship("Block", back_populates="tasks")
    category = relationship("Category", back_populates="tasks")

    # Table constraints
    __table_args__ = (
        CheckConstraint('estimated_minutes > 0', name='positive_estimated_minutes'),
        CheckConstraint('actual_minutes >= 0', name='non_negative_actual_minutes'),
        CheckConstraint('actual_minutes <= 10080', name='reasonable_actual_minutes'),  # 1 week max
    )

    def __repr__(self):
        return f"<Task(id={self.id}, title={self.title}, completed={self.completed})>"


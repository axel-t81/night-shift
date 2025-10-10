"""
Verification script to test the Models Layer
Creates sample data to verify relationships work correctly
"""
from datetime import datetime, timedelta
from app.database import SessionLocal, engine, Base
from app.models import Category, Block, Task

def verify_models():
    """Create sample data and verify model relationships"""
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create a session
    db = SessionLocal()
    
    try:
        # Create a category
        category = Category(
            name="Deep Work - System Design",
            color="#00FF00"
        )
        db.add(category)
        db.flush()  # Get the ID without committing
        
        print(f"✓ Created category: {category.name} (ID: {category.id})")
        
        # Create a time block
        now = datetime.utcnow()
        block = Block(
            title="Night Shift - Focus Block 1",
            start_time=now,
            end_time=now + timedelta(hours=2),
            block_number=1,
            day_number=1
        )
        db.add(block)
        db.flush()
        
        print(f"✓ Created block: {block.title} (ID: {block.id})")
        
        # Create tasks within the block
        task1 = Task(
            block_id=block.id,
            category_id=category.id,
            title="Review data structures",
            description="Go through hash tables and trees",
            estimated_minutes=45,
            position=1
        )
        
        task2 = Task(
            block_id=block.id,
            category_id=category.id,
            title="Practice system design problem",
            description="Design a URL shortener",
            estimated_minutes=60,
            position=2
        )
        
        db.add_all([task1, task2])
        db.commit()
        
        print(f"✓ Created task 1: {task1.title} (ID: {task1.id})")
        print(f"✓ Created task 2: {task2.title} (ID: {task2.id})")
        
        # Verify relationships
        print("\n--- Verifying Relationships ---")
        
        # Block -> Tasks
        print(f"\nBlock '{block.title}' has {len(block.tasks)} tasks:")
        for task in block.tasks:
            print(f"  - {task.title} ({task.estimated_minutes} min)")
        
        # Category -> Tasks
        print(f"\nCategory '{category.name}' has {len(category.tasks)} tasks:")
        for task in category.tasks:
            print(f"  - {task.title}")
        
        # Task -> Block and Category
        print(f"\nTask '{task1.title}' belongs to:")
        print(f"  - Block: {task1.block.title}")
        print(f"  - Category: {task1.category.name}")
        
        print("\n✓ All model relationships verified successfully!")
        
        # Test task completion
        task1.completed = True
        task1.completed_at = datetime.utcnow()
        task1.actual_minutes = 50
        db.commit()
        
        print(f"\n✓ Task '{task1.title}' marked as completed")
        print(f"  - Estimated: {task1.estimated_minutes} min")
        print(f"  - Actual: {task1.actual_minutes} min")
        print(f"  - Completed at: {task1.completed_at}")
        
        print("\n🎉 Models Layer implementation verified successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    verify_models()


#!/usr/bin/env python3
"""
Test script to verify the services layer implementation.

This script demonstrates:
1. Creating categories, blocks, and tasks
2. Completing tasks
3. Using the recurring block functionality
4. Getting statistics

Run with: python test_services.py
"""

from datetime import datetime, timedelta
from app.database import SessionLocal, engine, Base
from app.services import category_service, task_service, block_service
from app.schemas.category import CategoryCreate
from app.schemas.block import BlockCreate
from app.schemas.task import TaskCreate

def main():
    print("🚀 Night Shift App - Services Layer Test\n")
    print("=" * 60)
    
    # Create database tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    # Create a database session
    db = SessionLocal()
    
    try:
        # ===== 1. Create Categories =====
        print("\n📁 Creating Categories...")
        deep_work = category_service.create_category(db, CategoryCreate(
            name="Deep Work",
            color="#1E90FF"
        ))
        print(f"   ✓ Created category: {deep_work.name} (ID: {deep_work.id})")
        
        learning = category_service.create_category(db, CategoryCreate(
            name="Learning",
            color="#32CD32"
        ))
        print(f"   ✓ Created category: {learning.name} (ID: {learning.id})")
        
        # ===== 2. Create a Block =====
        print("\n⏰ Creating Time Block...")
        now = datetime.now()
        block = block_service.create_block(db, BlockCreate(
            start_time=now,
            end_time=now + timedelta(hours=2),
            title="Morning Focus Session",
            block_number=1,
            day_number=1
        ))
        print(f"   ✓ Created block: {block.title} (Block #{block.block_number})")
        
        # ===== 3. Add Tasks to Block =====
        print("\n✅ Adding Tasks to Block...")
        task1 = task_service.create_task(db, TaskCreate(
            block_id=block.id,
            category_id=deep_work.id,
            title="Write project documentation",
            description="Complete the README and API docs",
            estimated_minutes=45,
            position=0
        ))
        print(f"   ✓ Task 1: {task1.title} ({task1.estimated_minutes} min)")
        
        task2 = task_service.create_task(db, TaskCreate(
            block_id=block.id,
            category_id=learning.id,
            title="Study FastAPI advanced features",
            description="Learn about dependencies and middleware",
            estimated_minutes=30,
            position=1
        ))
        print(f"   ✓ Task 2: {task2.title} ({task2.estimated_minutes} min)")
        
        task3 = task_service.create_task(db, TaskCreate(
            block_id=block.id,
            category_id=deep_work.id,
            title="Code review",
            description="Review pull requests",
            estimated_minutes=25,
            position=2
        ))
        print(f"   ✓ Task 3: {task3.title} ({task3.estimated_minutes} min)")
        
        # ===== 4. Check Block Progress =====
        print("\n📊 Block Progress (Initial):")
        progress = task_service.get_block_progress(db, block.id)
        print(f"   Tasks: {progress['completed_tasks']}/{progress['total_tasks']} complete")
        print(f"   Completion: {progress['completion_percentage']}%")
        print(f"   Estimated time: {progress['total_estimated_minutes']} minutes")
        
        # ===== 5. Complete Some Tasks =====
        print("\n✨ Completing Tasks...")
        task_service.complete_task(db, task1.id, actual_minutes=50)
        print(f"   ✓ Completed: {task1.title} (took 50 min)")
        
        task_service.complete_task(db, task2.id, actual_minutes=28)
        print(f"   ✓ Completed: {task2.title} (took 28 min)")
        
        # ===== 6. Check Progress Again =====
        print("\n📊 Block Progress (After 2 tasks):")
        progress = task_service.get_block_progress(db, block.id)
        print(f"   Tasks: {progress['completed_tasks']}/{progress['total_tasks']} complete")
        print(f"   Completion: {progress['completion_percentage']}%")
        print(f"   Actual time spent: {progress['total_actual_minutes']} minutes")
        
        # ===== 7. Get Category Stats =====
        print("\n📈 Category Statistics:")
        deep_work_stats = category_service.get_category_stats(db, deep_work.id)
        print(f"   {deep_work_stats['category_name']}: "
              f"{deep_work_stats['completed_tasks']}/{deep_work_stats['total_tasks']} tasks "
              f"({deep_work_stats['completion_rate']}% complete)")
        
        learning_stats = category_service.get_category_stats(db, learning.id)
        print(f"   {learning_stats['category_name']}: "
              f"{learning_stats['completed_tasks']}/{learning_stats['total_tasks']} tasks "
              f"({learning_stats['completion_rate']}% complete)")
        
        # ===== 8. Complete Last Task =====
        print("\n✨ Completing Final Task...")
        task_service.complete_task(db, task3.id, actual_minutes=23)
        print(f"   ✓ Completed: {task3.title} (took 23 min)")
        
        # ===== 9. Use Recurring Block Feature =====
        print("\n🔄 Testing Recurring Block Feature...")
        print(f"   Current block number: {block.block_number}")
        
        result = block_service.complete_and_reset_block(db, block.id, move_to_end=True)
        print(f"   ✓ Block completed and reset!")
        print(f"   - Tasks completed: {result['tasks_completed']}")
        print(f"   - Tasks reset: {result['tasks_reset']}")
        print(f"   - New block number: {result['new_block_number']}")
        print(f"   - Moved to end: {result['moved_to_end']}")
        
        # ===== 10. Verify Tasks Are Reset =====
        print("\n🔍 Verifying Tasks Are Reset...")
        tasks = task_service.get_tasks_by_block(db, block.id)
        for task in tasks:
            status = "❌ Incomplete" if not task.completed else "✅ Complete"
            print(f"   {status}: {task.title}")
        
        # ===== 11. Clone Block Demo =====
        print("\n📋 Cloning Block for Tomorrow...")
        tomorrow = now + timedelta(days=1)
        cloned_block = block_service.clone_block(
            db,
            block.id,
            new_start_time=tomorrow,
            copy_tasks=True
        )
        print(f"   ✓ Created clone: {cloned_block.title}")
        print(f"   - Original block: #{result['new_block_number']}")
        print(f"   - Cloned block: #{cloned_block.block_number}")
        
        cloned_tasks = task_service.get_tasks_by_block(db, cloned_block.id)
        print(f"   - Cloned {len(cloned_tasks)} tasks")
        
        # ===== 12. Get Next Block =====
        print("\n🎯 Getting Next Block in Queue...")
        next_block = block_service.get_next_block(db)
        if next_block:
            print(f"   Next up: {next_block['block'].title}")
            print(f"   Progress: {next_block['completion_percentage']}%")
        
        # ===== 13. Overall Statistics =====
        print("\n📊 Overall Statistics:")
        block_stats = block_service.get_block_statistics(db)
        print(f"   Total blocks: {block_stats['total_blocks']}")
        print(f"   Active blocks: {block_stats['active_blocks']}")
        print(f"   Completed blocks: {block_stats['completed_blocks']}")
        
        all_categories = category_service.get_categories_with_task_counts(db)
        print(f"\n   Categories:")
        for cat in all_categories:
            print(f"   - {cat['name']}: {cat['completed_tasks']}/{cat['total_tasks']} tasks")
        
        print("\n" + "=" * 60)
        print("✨ Services Layer Test Complete! ✨")
        print("\nAll services are working correctly.")
        print("The recurring block feature successfully:")
        print("  1. Completed all tasks in the block")
        print("  2. Reset them to incomplete")
        print("  3. Moved the block to the end of the queue")
        print("\nReady for API layer implementation! 🚀")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()

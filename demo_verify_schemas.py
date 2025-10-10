#!/usr/bin/env python3
"""
Schema Verification Script

This script demonstrates how the Pydantic schemas work for data validation.
It shows examples of creating, validating, and serializing data using the schemas.

Run this script to verify the schemas are working correctly:
    python verify_schemas.py
"""

from datetime import datetime, timedelta
from app.schemas import (
    CategoryCreate, Category,
    BlockCreate, Block,
    TaskCreate, Task
)


def test_category_schemas():
    """Test Category schemas with various scenarios"""
    print("=" * 60)
    print("TESTING CATEGORY SCHEMAS")
    print("=" * 60)
    
    # Test 1: Valid category creation
    print("\n1. Creating a valid category:")
    category_data = CategoryCreate(
        name="Deep Work",
        color="#1E90FF"
    )
    print(f"   ✓ Category created: {category_data.model_dump()}")
    
    # Test 2: Category without color (optional field)
    print("\n2. Creating category without color:")
    category_no_color = CategoryCreate(name="Learning")
    print(f"   ✓ Category created: {category_no_color.model_dump()}")
    
    # Test 3: Invalid color format (should raise validation error)
    print("\n3. Testing invalid color format:")
    try:
        invalid_category = CategoryCreate(name="Test", color="blue")
        print("   ✗ Should have failed validation!")
    except ValueError as e:
        print(f"   ✓ Validation error caught: {e}")
    
    # Test 4: Simulating API response with complete Category schema
    print("\n4. Simulating API response:")
    api_response = Category(
        id="123e4567-e89b-12d3-a456-426614174000",
        name="Deep Work",
        color="#1E90FF",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    print(f"   ✓ API response: {api_response.model_dump_json(indent=2)}")


def test_block_schemas():
    """Test Block schemas with various scenarios"""
    print("\n" + "=" * 60)
    print("TESTING BLOCK SCHEMAS")
    print("=" * 60)
    
    # Test 1: Valid block creation
    print("\n1. Creating a valid time block:")
    start = datetime.utcnow()
    end = start + timedelta(hours=2)
    block_data = BlockCreate(
        start_time=start,
        end_time=end,
        title="Night Shift Block 1",
        block_number=1,
        day_number=1
    )
    print(f"   ✓ Block created successfully")
    print(f"   ✓ Block data: {block_data.model_dump()}")
    
    # Test 2: Invalid time range (end before start)
    print("\n2. Testing invalid time range (end before start):")
    try:
        invalid_block = BlockCreate(
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow() - timedelta(hours=1),
            title="Invalid Block",
            block_number=1
        )
        print("   ✗ Should have failed validation!")
    except ValueError as e:
        print(f"   ✓ Validation error caught: {e}")
    
    # Test 3: Block without optional fields
    print("\n3. Creating block without optional block_number and day_number:")
    simple_block = BlockCreate(
        start_time=start,
        end_time=end,
        title="Simple Block"
    )
    print(f"   ✓ Block created: {simple_block.model_dump()}")


def test_task_schemas():
    """Test Task schemas with various scenarios"""
    print("\n" + "=" * 60)
    print("TESTING TASK SCHEMAS")
    print("=" * 60)
    
    # Test 1: Valid task creation
    print("\n1. Creating a valid task:")
    task_data = TaskCreate(
        block_id="123e4567-e89b-12d3-a456-426614174000",
        category_id="987f6543-e21b-12d3-a456-426614174999",
        title="Study FastAPI documentation",
        description="Read chapters 3-5",
        estimated_minutes=45,
        position=0
    )
    print(f"   ✓ Task created successfully")
    print(f"   ✓ Task data: {task_data.model_dump()}")
    
    # Test 2: Invalid estimated_minutes (zero or negative)
    print("\n2. Testing invalid estimated_minutes (zero):")
    try:
        invalid_task = TaskCreate(
            block_id="123e4567-e89b-12d3-a456-426614174000",
            category_id="987f6543-e21b-12d3-a456-426614174999",
            title="Invalid Task",
            estimated_minutes=0,
            position=0
        )
        print("   ✗ Should have failed validation!")
    except ValueError as e:
        print(f"   ✓ Validation error caught: {e}")
    
    # Test 3: Unrealistic estimated_minutes (over 1 week)
    print("\n3. Testing unrealistic estimated_minutes (>1 week):")
    try:
        invalid_task = TaskCreate(
            block_id="123e4567-e89b-12d3-a456-426614174000",
            category_id="987f6543-e21b-12d3-a456-426614174999",
            title="Unrealistic Task",
            estimated_minutes=20000,
            position=0
        )
        print("   ✗ Should have failed validation!")
    except ValueError as e:
        print(f"   ✓ Validation error caught: {e}")
    
    # Test 4: Simulating completed task API response
    print("\n4. Simulating completed task API response:")
    completed_task = Task(
        id="456e7890-e12b-34c5-a678-901234567890",
        block_id="123e4567-e89b-12d3-a456-426614174000",
        category_id="987f6543-e21b-12d3-a456-426614174999",
        title="Study FastAPI documentation",
        description="Read chapters 3-5",
        estimated_minutes=45,
        actual_minutes=50,
        completed=True,
        position=0,
        completed_at=datetime.utcnow(),
        created_at=datetime.utcnow() - timedelta(hours=1)
    )
    print(f"   ✓ Completed task: {completed_task.model_dump_json(indent=2)}")


def main():
    """Run all schema tests"""
    print("\n" + "🔍 " * 30)
    print("PYDANTIC SCHEMAS VERIFICATION")
    print("🔍 " * 30)
    
    try:
        test_category_schemas()
        test_block_schemas()
        test_task_schemas()
        
        print("\n" + "=" * 60)
        print("✅ ALL SCHEMA TESTS PASSED!")
        print("=" * 60)
        print("\nThe schemas are working correctly and ready to use in the API layer.")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        raise


if __name__ == "__main__":
    main()


#!/usr/bin/env python3
"""
Category Refactoring Test Suite

Tests the new architecture where categories belong to blocks (not tasks).
Verifies that tasks inherit their category from their parent block.

Run with: python test_category_refactoring.py
"""

import requests
import json
from datetime import datetime

# Base API URL
BASE_URL = "http://localhost:8000/api"

# Track test results
tests_passed = 0
tests_failed = 0

def print_test(name, passed, details=""):
    """Print test result"""
    global tests_passed, tests_failed
    
    if passed:
        tests_passed += 1
        status = "✓ PASS"
        color = "\033[92m"  # Green
    else:
        tests_failed += 1
        status = "✗ FAIL"
        color = "\033[91m"  # Red
    
    reset = "\033[0m"
    print(f"\n{color}{status}{reset}: {name}")
    if details:
        print(f"  Details: {details}")

def test_api_health():
    """Test if API is running"""
    print("\n" + "=" * 70)
    print("TEST 1: API Health Check")
    print("=" * 70)
    try:
        response = requests.get(f"{BASE_URL}/blocks")
        passed = response.status_code in [200, 404]
        print_test("API is responding", passed, f"Status: {response.status_code}")
        return passed
    except Exception as e:
        print_test("API is responding", False, str(e))
        return False

def test_create_category():
    """Test creating a category"""
    print("\n" + "=" * 70)
    print("TEST 2: Create Category")
    print("=" * 70)
    
    category_data = {
        "name": "Deep Work Test",
        "color": "#1E90FF"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/categories", json=category_data)
        if response.status_code == 201:
            data = response.json()
            has_id = 'id' in data
            has_name = data.get('name') == category_data['name']
            has_color = data.get('color') == category_data['color']
            
            passed = all([has_id, has_name, has_color])
            print_test("Create category", passed, json.dumps(data, indent=2))
            return passed, data.get('id')
        else:
            print_test("Create category", False, f"Status: {response.status_code}, {response.text}")
            return False, None
    except Exception as e:
        print_test("Create category", False, str(e))
        return False, None

def test_create_block_with_category(category_id):
    """Test creating a block WITH a category"""
    print("\n" + "=" * 70)
    print("TEST 3: Create Block WITH Category")
    print("=" * 70)
    
    block_data = {
        "title": "Morning Focus Block",
        "description": "Testing block with category",
        "block_number": 10,
        "day_number": 1,
        "category_id": category_id
    }
    
    try:
        response = requests.post(f"{BASE_URL}/blocks", json=block_data)
        if response.status_code == 201:
            data = response.json()
            has_id = 'id' in data
            has_category = data.get('category_id') == category_id
            
            passed = all([has_id, has_category])
            details = json.dumps(data, indent=2)
            if has_category:
                details += f"\n✓ Block correctly has category_id: {category_id}"
            print_test("Create block with category", passed, details)
            return passed, data.get('id')
        else:
            print_test("Create block with category", False, f"Status: {response.status_code}, {response.text}")
            return False, None
    except Exception as e:
        print_test("Create block with category", False, str(e))
        return False, None

def test_create_block_without_category():
    """Test creating a block WITHOUT a category (should be allowed)"""
    print("\n" + "=" * 70)
    print("TEST 4: Create Block WITHOUT Category")
    print("=" * 70)
    
    block_data = {
        "title": "No Category Block",
        "description": "Block without category for testing",
        "block_number": 11,
        "day_number": 2
    }
    
    try:
        response = requests.post(f"{BASE_URL}/blocks", json=block_data)
        if response.status_code == 201:
            data = response.json()
            has_id = 'id' in data
            category_is_null = data.get('category_id') is None
            
            passed = all([has_id, category_is_null])
            details = json.dumps(data, indent=2)
            if category_is_null:
                details += "\n✓ Block correctly has NULL category_id"
            print_test("Create block without category", passed, details)
            return passed, data.get('id')
        else:
            print_test("Create block without category", False, f"Status: {response.status_code}, {response.text}")
            return False, None
    except Exception as e:
        print_test("Create block without category", False, str(e))
        return False, None

def test_create_task_inherits_category(block_id, expected_category_id):
    """Test creating a task WITHOUT category_id (should inherit from block)"""
    print("\n" + "=" * 70)
    print("TEST 5: Create Task - Inherits Category from Block")
    print("=" * 70)
    
    task_data = {
        "block_id": block_id,
        # NOTE: No category_id specified - should inherit from block!
        "title": "Task inheriting category",
        "description": "This task should get category from block",
        "estimated_minutes": 30,
        "position": 0
    }
    
    try:
        response = requests.post(f"{BASE_URL}/tasks", json=task_data)
        if response.status_code == 201:
            data = response.json()
            has_id = 'id' in data
            inherited_category = data.get('category_id') == expected_category_id
            
            passed = all([has_id, inherited_category])
            details = json.dumps(data, indent=2)
            if inherited_category:
                details += f"\n✓ Task correctly inherited category_id: {expected_category_id}"
            else:
                details += f"\n✗ Expected category_id: {expected_category_id}, Got: {data.get('category_id')}"
            print_test("Task inherits category from block", passed, details)
            return passed, data.get('id')
        else:
            print_test("Task inherits category from block", False, f"Status: {response.status_code}, {response.text}")
            return False, None
    except Exception as e:
        print_test("Task inherits category from block", False, str(e))
        return False, None

def test_create_task_explicit_category_matches(block_id, category_id):
    """Test creating a task WITH explicit category_id that matches block's category"""
    print("\n" + "=" * 70)
    print("TEST 6: Create Task - Explicit Category Matches Block")
    print("=" * 70)
    
    task_data = {
        "block_id": block_id,
        "category_id": category_id,  # Explicitly specifying same category as block
        "title": "Task with explicit matching category",
        "description": "Category matches block's category",
        "estimated_minutes": 25,
        "position": 1
    }
    
    try:
        response = requests.post(f"{BASE_URL}/tasks", json=task_data)
        if response.status_code == 201:
            data = response.json()
            has_id = 'id' in data
            correct_category = data.get('category_id') == category_id
            
            passed = all([has_id, correct_category])
            details = json.dumps(data, indent=2)
            if correct_category:
                details += f"\n✓ Task correctly has matching category_id: {category_id}"
            print_test("Task with explicit matching category", passed, details)
            return passed, data.get('id')
        else:
            print_test("Task with explicit matching category", False, f"Status: {response.status_code}, {response.text}")
            return False, None
    except Exception as e:
        print_test("Task with explicit matching category", False, str(e))
        return False, None

def test_create_task_in_block_no_category(block_no_category_id):
    """Test creating a task in a block that has NO category (should fail)"""
    print("\n" + "=" * 70)
    print("TEST 7: Create Task in Block WITHOUT Category (Should Fail)")
    print("=" * 70)
    
    task_data = {
        "block_id": block_no_category_id,
        # No category_id specified, and block has no category
        "title": "Task in categoryless block",
        "estimated_minutes": 20,
        "position": 0
    }
    
    try:
        response = requests.post(f"{BASE_URL}/tasks", json=task_data)
        # This should fail with 400 (block has no category)
        should_fail = response.status_code == 400
        
        details = f"Status: {response.status_code}"
        if should_fail:
            details += "\n✓ Correctly rejected task creation (block has no category)"
        else:
            details += f"\n✗ Should have been rejected but got: {response.text}"
        
        print_test("Task in categoryless block rejected", should_fail, details)
        return should_fail
    except Exception as e:
        print_test("Task in categoryless block rejected", False, str(e))
        return False

def test_create_second_category():
    """Create a second category for mismatch testing"""
    print("\n" + "=" * 70)
    print("TEST 8: Create Second Category (for mismatch test)")
    print("=" * 70)
    
    category_data = {
        "name": "Learning Test",
        "color": "#32CD32"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/categories", json=category_data)
        if response.status_code == 201:
            data = response.json()
            passed = 'id' in data
            print_test("Create second category", passed, json.dumps(data, indent=2))
            return passed, data.get('id')
        else:
            print_test("Create second category", False, f"Status: {response.status_code}")
            return False, None
    except Exception as e:
        print_test("Create second category", False, str(e))
        return False, None

def test_create_task_category_mismatch(block_id, block_category_id, different_category_id):
    """Test creating a task with category that DOESN'T match block's category (should fail)"""
    print("\n" + "=" * 70)
    print("TEST 9: Create Task - Category Mismatch (Should Fail)")
    print("=" * 70)
    
    task_data = {
        "block_id": block_id,
        "category_id": different_category_id,  # Different from block's category!
        "title": "Task with mismatched category",
        "estimated_minutes": 15,
        "position": 2
    }
    
    try:
        response = requests.post(f"{BASE_URL}/tasks", json=task_data)
        # This should fail with 400 (category mismatch)
        should_fail = response.status_code == 400
        
        details = f"Status: {response.status_code}"
        if should_fail:
            details += f"\n✓ Correctly rejected task (category mismatch)"
            details += f"\n  Block category: {block_category_id}"
            details += f"\n  Task category:  {different_category_id}"
        else:
            details += f"\n✗ Should have been rejected (category mismatch)"
            details += f"\n  Response: {response.text}"
        
        print_test("Task with category mismatch rejected", should_fail, details)
        return should_fail
    except Exception as e:
        print_test("Task with category mismatch rejected", False, str(e))
        return False

def test_get_block_with_tasks(block_id, expected_category_id):
    """Test getting block with tasks and verify category inheritance"""
    print("\n" + "=" * 70)
    print("TEST 10: Get Block with Tasks - Verify Category")
    print("=" * 70)
    
    try:
        response = requests.get(f"{BASE_URL}/blocks/{block_id}/with-tasks")
        if response.status_code == 200:
            data = response.json()
            block = data.get('block', {})
            tasks = data.get('tasks', [])
            
            block_has_category = block.get('category_id') == expected_category_id
            all_tasks_have_category = all(task.get('category_id') == expected_category_id for task in tasks)
            
            passed = block_has_category and all_tasks_have_category
            
            details = f"Block ID: {block_id}\n"
            details += f"Block category_id: {block.get('category_id')}\n"
            details += f"Number of tasks: {len(tasks)}\n"
            
            for i, task in enumerate(tasks, 1):
                task_cat = task.get('category_id')
                match = "✓" if task_cat == expected_category_id else "✗"
                details += f"{match} Task {i}: {task.get('title')} - category_id: {task_cat}\n"
            
            print_test("Block with tasks - all have correct category", passed, details)
            return passed
        else:
            print_test("Block with tasks - all have correct category", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("Block with tasks - all have correct category", False, str(e))
        return False

def test_block_statistics():
    """Test that block statistics still work after refactoring"""
    print("\n" + "=" * 70)
    print("TEST 11: Block Statistics (Backward Compatibility)")
    print("=" * 70)
    
    try:
        response = requests.get(f"{BASE_URL}/blocks/statistics")
        if response.status_code == 200:
            data = response.json()
            has_required = all(k in data for k in ['total_blocks', 'active_blocks', 'completed_blocks'])
            
            passed = has_required
            print_test("Block statistics endpoint works", passed, json.dumps(data, indent=2))
            return passed
        else:
            print_test("Block statistics endpoint works", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("Block statistics endpoint works", False, str(e))
        return False

def test_category_with_tasks():
    """Test that category endpoints still work"""
    print("\n" + "=" * 70)
    print("TEST 12: Category with Tasks (Backward Compatibility)")
    print("=" * 70)
    
    try:
        response = requests.get(f"{BASE_URL}/categories/with-tasks")
        if response.status_code == 200:
            data = response.json()
            passed = isinstance(data, list)
            
            details = f"Found {len(data)} categories\n"
            for cat in data[:3]:  # Show first 3
                details += f"  - {cat.get('name')}: {cat.get('total_tasks', 0)} tasks\n"
            
            print_test("Categories with tasks endpoint works", passed, details)
            return passed
        else:
            print_test("Categories with tasks endpoint works", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("Categories with tasks endpoint works", False, str(e))
        return False

def print_summary():
    """Print test summary"""
    total = tests_passed + tests_failed
    percentage = (tests_passed / total * 100) if total > 0 else 0
    
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"\nTotal Tests: {total}")
    print(f"✓ Passed: {tests_passed}")
    print(f"✗ Failed: {tests_failed}")
    print(f"Success Rate: {percentage:.1f}%")
    
    if tests_failed == 0:
        print("\n🎉 ALL TESTS PASSED! The category refactoring is working correctly!")
        print("\nKey Achievements:")
        print("  ✓ Blocks can have categories")
        print("  ✓ Tasks inherit categories from their blocks")
        print("  ✓ Category validation works correctly")
        print("  ✓ Backward compatibility maintained")
    else:
        print(f"\n⚠️  {tests_failed} test(s) failed. Please review the errors above.")
    
    print("=" * 70 + "\n")

def run_all_tests():
    """Run all category refactoring tests"""
    print("\n" + "🔬 " * 35)
    print("CATEGORY REFACTORING TEST SUITE")
    print("Testing: Categories belong to Blocks, Tasks inherit from Blocks")
    print("🔬 " * 35)
    
    # Test 1: API Health
    if not test_api_health():
        print("\n❌ API is not responding. Make sure the server is running:")
        print("   python -m uvicorn app.main:app --reload --port 8000")
        return
    
    # Test 2: Create category
    passed, category_id = test_create_category()
    if not passed or not category_id:
        print("\n❌ Cannot continue without a category")
        return
    
    # Test 3: Create block WITH category
    passed, block_id = test_create_block_with_category(category_id)
    if not passed or not block_id:
        print("\n❌ Cannot continue without a block")
        return
    
    # Test 4: Create block WITHOUT category
    passed, block_no_cat_id = test_create_block_without_category()
    
    # Test 5: Create task that inherits category
    test_create_task_inherits_category(block_id, category_id)
    
    # Test 6: Create task with explicit matching category
    test_create_task_explicit_category_matches(block_id, category_id)
    
    # Test 7: Try to create task in block with no category (should fail)
    if block_no_cat_id:
        test_create_task_in_block_no_category(block_no_cat_id)
    
    # Test 8: Create second category
    passed, category_id_2 = test_create_second_category()
    
    # Test 9: Try to create task with mismatched category (should fail)
    if passed and category_id_2:
        test_create_task_category_mismatch(block_id, category_id, category_id_2)
    
    # Test 10: Get block with tasks and verify
    test_get_block_with_tasks(block_id, category_id)
    
    # Test 11: Block statistics
    test_block_statistics()
    
    # Test 12: Category with tasks
    test_category_with_tasks()
    
    # Print summary
    print_summary()

if __name__ == "__main__":
    run_all_tests()


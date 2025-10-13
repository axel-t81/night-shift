#!/usr/bin/env python3
"""
Backend Testing Script
Tests the Block API endpoints with the new schema (no times, with description)
"""

import requests
import json
from datetime import datetime

# Base API URL
BASE_URL = "http://localhost:8000/api"

def print_test(name, passed, details=""):
    """Print test result"""
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"\n{status}: {name}")
    if details:
        print(f"  Details: {details}")

def test_api_health():
    """Test if API is running"""
    try:
        response = requests.get(f"{BASE_URL}/blocks")
        return response.status_code in [200, 404]
    except:
        return False

def test_create_block():
    """Test creating a block with new schema"""
    block_data = {
        "title": "Test Morning Routine",
        "description": "Testing the new description field",
        "block_number": 1,
        "day_number": 1
    }
    
    try:
        response = requests.post(f"{BASE_URL}/blocks", json=block_data)
        if response.status_code == 201:
            data = response.json()
            # Verify the response has the expected fields
            has_id = 'id' in data
            has_title = data.get('title') == block_data['title']
            has_desc = data.get('description') == block_data['description']
            no_start_time = 'start_time' not in data
            no_end_time = 'end_time' not in data
            
            passed = all([has_id, has_title, has_desc, no_start_time, no_end_time])
            return passed, data.get('id'), json.dumps(data, indent=2)
        return False, None, f"Status: {response.status_code}, {response.text}"
    except Exception as e:
        return False, None, str(e)

def test_create_block_minimal():
    """Test creating a block with only required fields (title)"""
    block_data = {
        "title": "Minimal Block Test"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/blocks", json=block_data)
        if response.status_code == 201:
            data = response.json()
            return True, data.get('id'), json.dumps(data, indent=2)
        return False, None, f"Status: {response.status_code}, {response.text}"
    except Exception as e:
        return False, None, str(e)

def test_get_block(block_id):
    """Test retrieving a block"""
    try:
        response = requests.get(f"{BASE_URL}/blocks/{block_id}")
        if response.status_code == 200:
            data = response.json()
            return True, json.dumps(data, indent=2)
        return False, f"Status: {response.status_code}"
    except Exception as e:
        return False, str(e)

def test_update_block(block_id):
    """Test updating a block"""
    update_data = {
        "description": "Updated description"
    }
    
    try:
        response = requests.put(f"{BASE_URL}/blocks/{block_id}", json=update_data)
        if response.status_code == 200:
            data = response.json()
            desc_updated = data.get('description') == update_data['description']
            return desc_updated, json.dumps(data, indent=2)
        return False, f"Status: {response.status_code}"
    except Exception as e:
        return False, str(e)

def test_list_blocks():
    """Test listing all blocks"""
    try:
        response = requests.get(f"{BASE_URL}/blocks")
        if response.status_code == 200:
            data = response.json()
            return True, f"Found {len(data)} blocks"
        return False, f"Status: {response.status_code}"
    except Exception as e:
        return False, str(e)

def test_invalid_day_number():
    """Test that day_number > 5 is rejected"""
    block_data = {
        "title": "Invalid Day Test",
        "day_number": 7  # Should fail - max is 5
    }
    
    try:
        response = requests.post(f"{BASE_URL}/blocks", json=block_data)
        # Should return 422 Validation Error
        return response.status_code == 422, f"Status: {response.status_code}"
    except Exception as e:
        return False, str(e)

def test_block_statistics():
    """Test getting block statistics"""
    try:
        response = requests.get(f"{BASE_URL}/blocks/statistics")
        if response.status_code == 200:
            data = response.json()
            has_required_fields = all(k in data for k in ['total_blocks', 'completed_blocks', 'active_blocks'])
            return has_required_fields, json.dumps(data, indent=2)
        return False, f"Status: {response.status_code}"
    except Exception as e:
        return False, str(e)

def run_all_tests():
    """Run all backend tests"""
    print("=" * 60)
    print("BACKEND API TESTING - Block Schema Updates")
    print("=" * 60)
    
    # Test 1: API Health
    print("\n[1/8] Testing API Health...")
    api_up = test_api_health()
    print_test("API is running", api_up)
    
    if not api_up:
        print("\n❌ API is not responding. Make sure the server is running:")
        print("   python -m uvicorn app.main:app --reload")
        return
    
    # Test 2: Create block with new schema
    print("\n[2/8] Testing Block Creation (with description)...")
    passed, block_id, details = test_create_block()
    print_test("Create block with description", passed, details)
    
    # Test 3: Create minimal block
    print("\n[3/8] Testing Block Creation (minimal - title only)...")
    passed2, block_id2, details2 = test_create_block_minimal()
    print_test("Create block with only title", passed2, details2)
    
    # Test 4: Get block
    if block_id:
        print("\n[4/8] Testing Get Block by ID...")
        passed, details = test_get_block(block_id)
        print_test("Get block by ID", passed, details)
    else:
        print("\n[4/8] Skipping Get Block (no block_id)")
    
    # Test 5: Update block
    if block_id:
        print("\n[5/8] Testing Update Block...")
        passed, details = test_update_block(block_id)
        print_test("Update block description", passed, details)
    else:
        print("\n[5/8] Skipping Update Block (no block_id)")
    
    # Test 6: List blocks
    print("\n[6/8] Testing List Blocks...")
    passed, details = test_list_blocks()
    print_test("List all blocks", passed, details)
    
    # Test 7: Test day_number validation (1-5)
    print("\n[7/8] Testing Day Number Validation (should reject > 5)...")
    passed, details = test_invalid_day_number()
    print_test("Day number validation (reject 7)", passed, details)
    
    # Test 8: Get statistics
    print("\n[8/8] Testing Block Statistics...")
    passed, details = test_block_statistics()
    print_test("Get block statistics", passed, details)
    
    print("\n" + "=" * 60)
    print("TESTING COMPLETE")
    print("=" * 60)
    print("\n✓ If all tests passed, the backend is working correctly!")
    print("✓ You can now test the frontend UI\n")

if __name__ == "__main__":
    run_all_tests()


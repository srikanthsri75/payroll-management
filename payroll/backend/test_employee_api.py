#!/usr/bin/env python3
"""
Employee API Test Suite
Tests all enhanced employee endpoints with new fields
"""

import requests
import json
import sys
from datetime import date

# Configuration
BASE_URL = "http://localhost:5000"
TEST_ADMIN_EMAIL = "admin@payroll.com"
TEST_ADMIN_PASSWORD = "admin123"

def get_auth_token():
    """Get authentication token for testing"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_ADMIN_EMAIL,
        "password": TEST_ADMIN_PASSWORD
    })
    
    if response.status_code == 200:
        return response.json().get("token")
    else:
        print(f"❌ Login failed: {response.status_code} - {response.text}")
        return None

def test_employee_options(token):
    """Test employee options endpoint"""
    print("\n🔍 Testing employee options endpoint...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/employees/options", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Employee options retrieved successfully")
        print(f"   - Form options: {len(data['form_options'])} categories")
        print(f"   - Statistics: {data['statistics']['total_employees']} total employees")
        return True
    else:
        print(f"❌ Employee options failed: {response.status_code} - {response.text}")
        return False

def test_create_employee_with_details(token):
    """Test creating employee with all new fields"""
    print("\n✨ Testing employee creation with enhanced fields...")
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    test_employee = {
        "name": "Jane Smith",
        "email": "jane.smith@test.com",
        "employee_id": "EMP999",
        "phone": "+1-555-0123",
        "department": "Engineering",
        "position": "Senior Developer",
        "basic_salary": 85000,
        "hire_date": "2024-01-15",
        
        # Personal Details
        "date_of_birth": "1990-05-15",
        "gender": "Female",
        "marital_status": "Married",
        "national_id": "123456789",
        "tax_id": "TX123456789",
        "address": "123 Main St, Anytown, ST 12345",
        
        # Emergency Contact
        "emergency_contact_name": "John Smith",
        "emergency_contact_phone": "+1-555-0456",
        
        # Employment Details
        "employment_type": "Full-time"
    }
    
    response = requests.post(f"{BASE_URL}/api/employees", headers=headers, json=test_employee)
    
    if response.status_code == 201:
        data = response.json()
        employee_id = data['employee']['id']
        print("✅ Employee created successfully")
        print(f"   - Employee ID: {employee_id}")
        print(f"   - Name: {data['employee']['name']}")
        print(f"   - All fields populated: {len(data['employee'])} fields")
        return employee_id
    else:
        print(f"❌ Employee creation failed: {response.status_code} - {response.text}")
        return None

def test_get_employee_details(token, employee_id):
    """Test getting comprehensive employee details"""
    print(f"\n📋 Testing employee details retrieval for ID {employee_id}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/employees/{employee_id}", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Employee details retrieved successfully")
        print(f"   - Personal details included: {'date_of_birth' in data}")
        print(f"   - Emergency contact: {'emergency_contact_name' in data}")
        print(f"   - Employment type: {data.get('employment_type', 'Not set')}")
        print(f"   - Summary statistics: {'summary' in data}")
        if 'summary' in data:
            print(f"   - Years of service: {data['summary'].get('years_of_service', 0)}")
        return True
    else:
        print(f"❌ Employee details failed: {response.status_code} - {response.text}")
        return False

def test_update_employee(token, employee_id):
    """Test updating employee with new fields"""
    print(f"\n✏️ Testing employee update for ID {employee_id}...")
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    update_data = {
        "address": "456 Updated Ave, New City, ST 67890",
        "emergency_contact_name": "Jane Doe",
        "employment_type": "Part-time",
        "basic_salary": 90000
    }
    
    response = requests.put(f"{BASE_URL}/api/employees/{employee_id}", headers=headers, json=update_data)
    
    if response.status_code == 200:
        print("✅ Employee updated successfully")
        return True
    else:
        print(f"❌ Employee update failed: {response.status_code} - {response.text}")
        return False

def test_search_and_filter(token):
    """Test advanced search and filtering"""
    print("\n🔍 Testing advanced search and filtering...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test search
    response = requests.get(f"{BASE_URL}/api/employees?search=Jane&sort_by=name&sort_order=asc", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Search functionality working")
        print(f"   - Found {len(data['employees'])} employees")
        print(f"   - Pagination: {data['pagination']}")
        print(f"   - Summary: {data.get('summary', {}).get('total_filtered', 0)} total filtered")
        return True
    else:
        print(f"❌ Search failed: {response.status_code} - {response.text}")
        return False

def test_validation(token):
    """Test input validation"""
    print("\n🛡️ Testing input validation...")
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Test invalid data
    invalid_employee = {
        "name": "Test User",
        "email": "invalid-email",  # Invalid email
        "employee_id": "TEST001",
        "date_of_birth": "2050-01-01",  # Future date
        "gender": "InvalidGender",  # Invalid gender
        "basic_salary": -1000  # Negative salary
    }
    
    response = requests.post(f"{BASE_URL}/api/employees", headers=headers, json=invalid_employee)
    
    if response.status_code == 400:
        error_data = response.json()
        print("✅ Validation working correctly")
        print(f"   - Validation errors caught: {len(error_data.get('details', []))}")
        return True
    else:
        print(f"❌ Validation not working: {response.status_code} - {response.text}")
        return False

def cleanup_test_employee(token, employee_id):
    """Clean up test employee"""
    if employee_id:
        print(f"\n🧹 Cleaning up test employee {employee_id}...")
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.delete(f"{BASE_URL}/api/employees/{employee_id}", headers=headers)
        
        if response.status_code == 200:
            print("✅ Test employee cleaned up")
        else:
            print(f"⚠️ Cleanup failed: {response.status_code} - {response.text}")

def main():
    """Run all tests"""
    print("🚀 Employee API Enhanced Test Suite")
    print("=" * 50)
    
    # Get authentication token
    token = get_auth_token()
    if not token:
        print("❌ Cannot proceed without authentication token")
        sys.exit(1)
    
    print("✅ Authentication successful")
    
    # Run tests
    tests_passed = 0
    total_tests = 6
    
    # Test employee options
    if test_employee_options(token):
        tests_passed += 1
    
    # Test validation
    if test_validation(token):
        tests_passed += 1
    
    # Test create employee
    employee_id = test_create_employee_with_details(token)
    if employee_id:
        tests_passed += 1
        
        # Test get employee details
        if test_get_employee_details(token, employee_id):
            tests_passed += 1
        
        # Test update employee
        if test_update_employee(token, employee_id):
            tests_passed += 1
        
        # Test search functionality
        if test_search_and_filter(token):
            tests_passed += 1
        
        # Cleanup
        cleanup_test_employee(token, employee_id)
    
    # Results
    print("\n" + "=" * 50)
    print(f"🎯 Tests completed: {tests_passed}/{total_tests} passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Employee API enhancement is working correctly.")
        sys.exit(0)
    else:
        print("⚠️ Some tests failed. Please check the API implementation.")
        sys.exit(1)

if __name__ == "__main__":
    main()
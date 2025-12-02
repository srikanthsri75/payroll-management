#!/usr/bin/env python3
"""
Database Migration Verification Script
Verifies that the new employee fields have been added successfully
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.employee import Employee
from sqlalchemy import inspect

def verify_employee_fields():
    """Verify that all new employee fields exist in the database"""
    app = create_app()
    
    with app.app_context():
        try:
            # Get table inspector
            inspector = inspect(db.engine)
            columns = inspector.get_columns('employees')
            column_names = [col['name'] for col in columns]
            
            # Expected new fields
            expected_fields = [
                'date_of_birth',
                'gender', 
                'marital_status',
                'national_id',
                'tax_id',
                'address',
                'emergency_contact_name',
                'emergency_contact_phone',
                'employment_type'
            ]
            
            print("Verifying employee table structure...")
            print(f"Total columns found: {len(columns)}")
            print("\nColumn verification:")
            
            missing_fields = []
            for field in expected_fields:
                if field in column_names:
                    print(f"✓ {field}")
                else:
                    print(f"✗ {field} - MISSING")
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"\n❌ Migration incomplete. Missing fields: {', '.join(missing_fields)}")
                print("Please run the migration script: ./migrate_employee_details.sh")
                return False
            else:
                print(f"\n✅ Migration successful! All {len(expected_fields)} new fields are present.")
                
                # Test model instantiation
                try:
                    # Create a test employee object to verify model works
                    test_employee = Employee(
                        name="Test Employee",
                        email="test@example.com",
                        employee_id="TEST001",
                        gender="Other",
                        employment_type="Full-time"
                    )
                    
                    # Test to_dict method
                    employee_dict = test_employee.to_dict()
                    print(f"✅ Employee model working correctly")
                    print(f"✅ to_dict() method includes {len([k for k in employee_dict.keys() if k in expected_fields])} new fields")
                    
                except Exception as e:
                    print(f"❌ Employee model error: {e}")
                    return False
                
                return True
                
        except Exception as e:
            print(f"❌ Database connection error: {e}")
            return False

if __name__ == "__main__":
    print("Employee Details Migration Verification")
    print("=" * 50)
    
    success = verify_employee_fields()
    sys.exit(0 if success else 1)
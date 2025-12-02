# Employee API Enhancement Documentation

## Overview
The Employee API has been enhanced with comprehensive personal details, advanced search capabilities, and robust validation.

## Enhanced Endpoints

### GET /api/employees
**Enhanced with advanced filtering and search**

#### Query Parameters
- `page` (int): Page number (default: 1)
- `per_page` (int): Items per page (default: 10, max: 100)
- `search` (string): Search in name, email, employee_id, position, address
- `department` (string): Filter by department
- `employment_type` (string): Filter by employment type
- `gender` (string): Filter by gender
- `hire_date_from` (date): Filter hire date from (YYYY-MM-DD)
- `hire_date_to` (date): Filter hire date to (YYYY-MM-DD)
- `sort_by` (string): Sort field (name, email, employee_id, department, hire_date, created_at)
- `sort_order` (string): Sort order (asc/desc)

#### Response
```json
{
  "employees": [...],
  "pagination": {
    "total": 150,
    "pages": 15,
    "current_page": 1,
    "per_page": 10,
    "has_next": true,
    "has_prev": false
  },
  "filters": {...},
  "summary": {
    "total_filtered": 150,
    "departments": [...],
    "employment_types": [...]
  }
}
```

### GET /api/employees/{id}
**Enhanced with comprehensive employee details**

#### Response
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@company.com",
  "employee_id": "EMP001",
  
  // Personal Details
  "date_of_birth": "1985-03-15",
  "gender": "Male",
  "marital_status": "Married",
  "national_id": "123456789",
  "tax_id": "TX123456789",
  "address": "123 Main St, City, State 12345",
  
  // Emergency Contact
  "emergency_contact_name": "Jane Doe",
  "emergency_contact_phone": "+1-555-0123",
  
  // Employment Details
  "employment_type": "Full-time",
  "department": "Engineering",
  "position": "Senior Developer",
  "hire_date": "2020-01-15",
  
  // Financial Information
  "current_salary": {...},
  "salary_history": [...],
  "allowances": [...],
  "deductions": [...],
  "recent_payrolls": [...],
  "payslips_count": 24,
  
  // Summary Statistics
  "summary": {
    "total_allowances": 500.00,
    "total_deductions": 200.00,
    "net_additions": 300.00,
    "years_of_service": 4
  }
}
```

### POST /api/employees
**Enhanced with new personal detail fields**

#### Request Body
```json
{
  // Required fields
  "name": "Jane Smith",
  "email": "jane@company.com",
  "employee_id": "EMP002",
  
  // Basic Information
  "phone": "+1-555-0456",
  "department": "Marketing",
  "position": "Marketing Manager",
  "basic_salary": 75000,
  "hire_date": "2024-01-01",
  
  // Personal Details (optional)
  "date_of_birth": "1990-06-20",
  "gender": "Female",
  "marital_status": "Single",
  "national_id": "987654321",
  "tax_id": "TX987654321",
  "address": "456 Oak Ave, City, State 67890",
  
  // Emergency Contact (optional)
  "emergency_contact_name": "John Smith",
  "emergency_contact_phone": "+1-555-0789",
  
  // Employment Details (optional)
  "employment_type": "Full-time",
  
  // Banking (optional)
  "bank_account": "1234567890",
  "bank_name": "First National Bank"
}
```

### PUT /api/employees/{id}
**Enhanced to update all new fields**

Same structure as POST, but all fields are optional.

### GET /api/employees/options
**New endpoint for form options and statistics**

#### Response
```json
{
  "form_options": {
    "departments": ["Engineering", "Marketing", "Sales"],
    "employment_types": ["Full-time", "Part-time", "Contract"],
    "genders": ["Male", "Female", "Other", "Prefer not to say"],
    "marital_statuses": ["Single", "Married", "Divorced", "Widowed", "Separated"],
    "employment_type_options": ["Full-time", "Part-time", "Contract", "Temporary", "Intern"]
  },
  "statistics": {
    "total_employees": 150,
    "by_department": [...],
    "by_gender": [...],
    "by_employment_type": [...]
  }
}
```

## New Fields Added

### Personal Details
- `date_of_birth` (DATE): Employee's birth date
- `gender` (VARCHAR): Male, Female, Other, Prefer not to say
- `marital_status` (VARCHAR): Single, Married, Divorced, Widowed, Separated
- `national_id` (VARCHAR): National identification number
- `tax_id` (VARCHAR): Tax identification number
- `address` (TEXT): Full address

### Emergency Contact
- `emergency_contact_name` (VARCHAR): Emergency contact person
- `emergency_contact_phone` (VARCHAR): Emergency contact phone

### Employment
- `employment_type` (VARCHAR): Full-time, Part-time, Contract, Temporary, Intern

## Validation Rules

### Required Fields (Create)
- name, email, employee_id

### Email Validation
- Must be valid email format

### Date Validation
- Dates must be in YYYY-MM-DD format
- Birth date cannot be in the future or before 1900
- Hire date cannot be in the future

### Phone Validation
- Must be valid phone format (10-20 digits with optional formatting)

### Choice Field Validation
- Gender: Must be from predefined list
- Marital Status: Must be from predefined list
- Employment Type: Must be from predefined list

### Salary Validation
- Must be non-negative number

## Error Responses

### Validation Errors (400)
```json
{
  "error": "Validation failed",
  "details": [
    "Invalid email format",
    "Invalid date of birth",
    "Invalid gender value"
  ]
}
```

### Duplicate Entry (400)
```json
{
  "error": "Email already exists"
}
```

### Not Found (404)
```json
{
  "error": "Employee not found"
}
```

### Unauthorized (401)
```json
{
  "error": "Unauthorized"
}
```

## Testing

Run the test suite:
```bash
python test_employee_api.py
```

The test suite covers:
- Authentication
- Employee creation with all new fields
- Data retrieval and validation
- Update operations
- Advanced search and filtering
- Input validation
- Error handling
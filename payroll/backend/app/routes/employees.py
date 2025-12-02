from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app import db
from app.models import Employee, User, Salary, Allowance, Deduction
from datetime import date
import re

employee_bp = Blueprint('employees', __name__, url_prefix='/api/employees')

def validate_employee_data(data, is_update=False):
    """Validate employee input data"""
    errors = []
    
    # Required field validation (for create only)
    if not is_update:
        required_fields = ['name', 'email', 'employee_id']
        for field in required_fields:
            if not data.get(field):
                errors.append(f'{field} is required')
    
    # Email validation
    if data.get('email'):
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, data['email']):
            errors.append('Invalid email format')
    
    # Phone validation (if provided)
    if data.get('phone'):
        # Allow various phone formats, basic validation
        phone_pattern = r'^[+]?[\d\s\-\(\)]{10,20}$'
        if not re.match(phone_pattern, data['phone']):
            errors.append('Invalid phone format')
    
    # Date validations
    date_fields = ['hire_date', 'date_of_birth']
    for field in date_fields:
        if data.get(field):
            try:
                parsed_date = date.fromisoformat(data[field])
                # Check reasonable date ranges
                if field == 'date_of_birth':
                    if parsed_date > date.today() or parsed_date.year < 1900:
                        errors.append('Invalid date of birth')
                elif field == 'hire_date':
                    if parsed_date > date.today():
                        errors.append('Hire date cannot be in the future')
            except ValueError:
                errors.append(f'Invalid date format for {field}. Use YYYY-MM-DD')
    
    # Gender validation
    if data.get('gender'):
        valid_genders = ['Male', 'Female', 'Other', 'Prefer not to say']
        if data['gender'] not in valid_genders:
            errors.append('Invalid gender value')
    
    # Marital status validation
    if data.get('marital_status'):
        valid_statuses = ['Single', 'Married', 'Divorced', 'Widowed', 'Separated']
        if data['marital_status'] not in valid_statuses:
            errors.append('Invalid marital status')
    
    # Employment type validation
    if data.get('employment_type'):
        valid_types = ['Full-time', 'Part-time', 'Contract', 'Temporary', 'Intern']
        if data['employment_type'] not in valid_types:
            errors.append('Invalid employment type')
    
    # Salary validation
    if data.get('basic_salary'):
        try:
            salary = float(data['basic_salary'])
            if salary < 0:
                errors.append('Salary cannot be negative')
        except (ValueError, TypeError):
            errors.append('Invalid salary format')
    
    return errors

@employee_bp.route('', methods=['GET'])
@jwt_required()
def get_employees():
    """Get all employees with advanced pagination, search and filtering"""
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    
    if not user or not user.can_manage_employees():
        return {'error': 'Unauthorized'}, 401
    try:
        current_user_id = int(get_jwt_identity())  # Convert back to int
        print(f"DEBUG GET: Current user ID: {current_user_id}")  # Debug
        
        # Pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)  # Max 100 per page
        
        # Search parameters
        search = request.args.get('search', '', type=str)
        department = request.args.get('department', '', type=str)
        employment_type = request.args.get('employment_type', '', type=str)
        gender = request.args.get('gender', '', type=str)
        
        # Date range filtering
        hire_date_from = request.args.get('hire_date_from', type=str)
        hire_date_to = request.args.get('hire_date_to', type=str)
        
        # Sorting
        sort_by = request.args.get('sort_by', 'name', type=str)
        sort_order = request.args.get('sort_order', 'asc', type=str)
        
        query = Employee.query.filter_by(is_active=True)  # Only active employees
        
        # Apply search filter
        if search:
            query = query.filter(db.or_(
                Employee.name.ilike(f'%{search}%'),
                Employee.email.ilike(f'%{search}%'),
                Employee.employee_id.ilike(f'%{search}%'),
                Employee.position.ilike(f'%{search}%'),
                Employee.address.ilike(f'%{search}%')
            ))
        
        # Apply filters
        if department:
            query = query.filter_by(department=department)
        if employment_type:
            query = query.filter_by(employment_type=employment_type)
        if gender:
            query = query.filter_by(gender=gender)
            
        # Apply date range filters
        if hire_date_from:
            try:
                from_date = date.fromisoformat(hire_date_from)
                query = query.filter(Employee.hire_date >= from_date)
            except ValueError:
                return {'error': 'Invalid hire_date_from format. Use YYYY-MM-DD'}, 400
                
        if hire_date_to:
            try:
                to_date = date.fromisoformat(hire_date_to)
                query = query.filter(Employee.hire_date <= to_date)
            except ValueError:
                return {'error': 'Invalid hire_date_to format. Use YYYY-MM-DD'}, 400
        
        # Apply sorting
        valid_sort_fields = ['name', 'email', 'employee_id', 'department', 'hire_date', 'created_at']
        if sort_by in valid_sort_fields:
            sort_column = getattr(Employee, sort_by)
            if sort_order.lower() == 'desc':
                query = query.order_by(sort_column.desc())
            else:
                query = query.order_by(sort_column.asc())
        
        employees = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # Get summary statistics for the filtered results
        total_count = query.count()
        departments = db.session.query(Employee.department, db.func.count(Employee.id)).filter(query.whereclause).group_by(Employee.department).all()
        employment_types = db.session.query(Employee.employment_type, db.func.count(Employee.id)).filter(query.whereclause).group_by(Employee.employment_type).all()
        
        return {
            'employees': [emp.to_dict() for emp in employees.items],
            'pagination': {
                'total': employees.total,
                'pages': employees.pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': employees.has_next,
                'has_prev': employees.has_prev
            },
            'filters': {
                'search': search,
                'department': department,
                'employment_type': employment_type,
                'gender': gender,
                'hire_date_from': hire_date_from,
                'hire_date_to': hire_date_to
            },
            'summary': {
                'total_filtered': total_count,
                'departments': [{'name': d[0], 'count': d[1]} for d in departments if d[0]],
                'employment_types': [{'name': e[0], 'count': e[1]} for e in employment_types if e[0]]
            }
        }, 200
    
    except Exception as e:
        print(f"DEBUG GET: Error in get_employees: {e}")  # Debug
        return {'error': f'Failed to fetch employees: {str(e)}'}, 500

@employee_bp.route('/<int:employee_id>', methods=['GET'])
@jwt_required()
def get_employee(employee_id):
    """Get comprehensive employee details"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user or not user.can_manage_employees():
            return {'error': 'Unauthorized'}, 401
        
        employee = Employee.query.get(employee_id)
        
        if not employee:
            return {'error': 'Employee not found'}, 404
        
        # Get base employee data
        data = employee.to_dict()
        
        # Get current salary details
        current_salary = Salary.query.filter(
            Salary.employee_id == employee_id,
            db.or_(Salary.end_date.is_(None), Salary.end_date >= date.today())
        ).first()
        
        data['current_salary'] = current_salary.to_dict() if current_salary else None
        
        # Get salary history (last 12 months or all if less than 12)
        salary_history = Salary.query.filter_by(employee_id=employee_id).order_by(Salary.start_date.desc()).limit(12).all()
        data['salary_history'] = [s.to_dict() for s in salary_history]
        
        # Get active allowances
        allowances = Allowance.query.filter(
            Allowance.employee_id == employee_id,
            db.or_(Allowance.end_date.is_(None), Allowance.end_date >= date.today())
        ).all()
        data['allowances'] = [a.to_dict() for a in allowances]
        
        # Get active deductions
        deductions = Deduction.query.filter(
            Deduction.employee_id == employee_id,
            db.or_(Deduction.end_date.is_(None), Deduction.end_date >= date.today())
        ).all()
        data['deductions'] = [d.to_dict() for d in deductions]
        
        # Get recent payroll runs (last 6 months)
        from app.models.payroll_run import PayrollRun
        recent_payrolls = PayrollRun.query.filter_by(employee_id=employee_id).order_by(PayrollRun.year.desc(), PayrollRun.month.desc()).limit(6).all()
        data['recent_payrolls'] = [p.to_dict() for p in recent_payrolls]
        
        # Get recent payslips count
        from app.models.payslip import Payslip
        payslips_count = Payslip.query.filter_by(employee_id=employee_id).count()
        data['payslips_count'] = payslips_count
        
        # Calculate summary statistics
        total_allowances = sum(a.amount for a in allowances if a.is_fixed)
        total_deductions = sum(d.amount for d in deductions if d.is_fixed)
        
        data['summary'] = {
            'total_allowances': float(total_allowances),
            'total_deductions': float(total_deductions),
            'net_additions': float(total_allowances - total_deductions),
            'years_of_service': (date.today() - employee.hire_date).days // 365 if employee.hire_date else 0
        }
        
        return data, 200
        
    except Exception as e:
        print(f"ERROR: Failed to get employee {employee_id}: {e}")
        return {'error': f'Failed to fetch employee details: {str(e)}'}, 500

@employee_bp.route('', methods=['POST'])
@jwt_required()
def create_employee():
    """Create new employee"""
    try:
        current_user_id = int(get_jwt_identity())  # Convert back to int
        print(f"DEBUG POST: Current user ID: {current_user_id}")  # Debug
        
        user = User.query.get(current_user_id)
        print(f"DEBUG POST: User found: {user}, Role: {user.role if user else 'None'}")  # Debug
        
        if not user or user.role not in ['admin', 'finance']:
            print(f"DEBUG POST: Unauthorized - User role: {user.role if user else 'None'}")  # Debug
            return {'error': 'Unauthorized'}, 401
        
        data = request.get_json()
        print(f"DEBUG POST: Received employee data: {data}")  # Debug
        
        # Validate input data
        validation_errors = validate_employee_data(data, is_update=False)
        if validation_errors:
            return {'error': 'Validation failed', 'details': validation_errors}, 400
        
        if not data or not data.get('name') or not data.get('email') or not data.get('employee_id'):
            print(f"DEBUG POST: Missing required fields - Name: {data.get('name') if data else 'None'}, Email: {data.get('email') if data else 'None'}, Employee ID: {data.get('employee_id') if data else 'None'}")  # Debug
            return {'error': 'Missing required fields'}, 400
        
        if Employee.query.filter_by(email=data['email']).first():
            print(f"DEBUG POST: Email already exists: {data['email']}")  # Debug
            return {'error': 'Email already exists'}, 400
        
        if Employee.query.filter_by(employee_id=data['employee_id']).first():
            print(f"DEBUG POST: Employee ID already exists: {data['employee_id']}")  # Debug
            return {'error': 'Employee ID already exists'}, 400
        
        employee = Employee(
            name=data['name'],
            email=data['email'],
            phone=data.get('phone'),
            department=data.get('department'),
            position=data.get('position'),
            bank_account=data.get('bank_account'),
            bank_name=data.get('bank_name'),
            employee_id=data['employee_id'],
            hire_date=date.fromisoformat(data['hire_date']) if data.get('hire_date') else None,
            
            # Personal Details
            date_of_birth=date.fromisoformat(data['date_of_birth']) if data.get('date_of_birth') else None,
            gender=data.get('gender'),
            marital_status=data.get('marital_status'),
            national_id=data.get('national_id'),
            tax_id=data.get('tax_id'),
            address=data.get('address'),
            
            # Emergency Contact
            emergency_contact_name=data.get('emergency_contact_name'),
            emergency_contact_phone=data.get('emergency_contact_phone'),
            
            # Employment Details
            employment_type=data.get('employment_type')
        )
        
        db.session.add(employee)
        db.session.flush()  # To get the employee ID
        
        # Create salary record if basic_salary is provided
        if data.get('basic_salary'):
            salary = Salary(
                employee_id=employee.id,
                basic_salary=float(data['basic_salary']),
                start_date=date.today()
            )
            db.session.add(salary)
        
        db.session.commit()
        
        print(f"DEBUG POST: Employee created successfully: {employee.to_dict()}")  # Debug
        return {'message': 'Employee created', 'employee': employee.to_dict()}, 201
    
    except Exception as e:
        print(f"DEBUG POST: Error creating employee: {e}")  # Debug
        import traceback
        traceback.print_exc()  # Print full traceback
        db.session.rollback()
        return {'error': f'Database error: {str(e)}'}, 422

@employee_bp.route('/<int:employee_id>', methods=['PUT'])
@jwt_required()
def update_employee(employee_id):
    """Update employee"""
    current_user_id = int(get_jwt_identity())  # Convert back to int
    user = User.query.get(current_user_id)
    
    if not user or user.role not in ['admin', 'finance']:
        return {'error': 'Unauthorized'}, 401
    
    employee = Employee.query.get(employee_id)
    
    if not employee:
        return {'error': 'Employee not found'}, 404
    
    data = request.get_json()
    
    # Validate input data
    validation_errors = validate_employee_data(data, is_update=True)
    if validation_errors:
        return {'error': 'Validation failed', 'details': validation_errors}, 400
    
    # Basic employee information
    employee.name = data.get('name', employee.name)
    employee.phone = data.get('phone', employee.phone)
    employee.department = data.get('department', employee.department)
    employee.position = data.get('position', employee.position)
    employee.bank_account = data.get('bank_account', employee.bank_account)
    employee.bank_name = data.get('bank_name', employee.bank_name)
    
    # Update hire_date if provided
    if data.get('hire_date'):
        employee.hire_date = date.fromisoformat(data['hire_date'])
    
    # Personal Details
    if data.get('date_of_birth'):
        employee.date_of_birth = date.fromisoformat(data['date_of_birth'])
    if 'gender' in data:
        employee.gender = data.get('gender')
    if 'marital_status' in data:
        employee.marital_status = data.get('marital_status')
    if 'national_id' in data:
        employee.national_id = data.get('national_id')
    if 'tax_id' in data:
        employee.tax_id = data.get('tax_id')
    if 'address' in data:
        employee.address = data.get('address')
    
    # Emergency Contact
    if 'emergency_contact_name' in data:
        employee.emergency_contact_name = data.get('emergency_contact_name')
    if 'emergency_contact_phone' in data:
        employee.emergency_contact_phone = data.get('emergency_contact_phone')
    
    # Employment Details
    if 'employment_type' in data:
        employee.employment_type = data.get('employment_type')
    
    # Update salary if provided
    if data.get('basic_salary') is not None:
        # End current salary if exists
        current_salary = Salary.query.filter(
            Salary.employee_id == employee_id,
            Salary.end_date.is_(None)
        ).first()
        
        if current_salary:
            if float(data['basic_salary']) != current_salary.basic_salary:
                # End current salary and create new one
                current_salary.end_date = date.today()
                new_salary = Salary(
                    employee_id=employee_id,
                    basic_salary=float(data['basic_salary']),
                    start_date=date.today()
                )
                db.session.add(new_salary)
        else:
            # Create new salary record
            new_salary = Salary(
                employee_id=employee_id,
                basic_salary=float(data['basic_salary']),
                start_date=date.today()
            )
            db.session.add(new_salary)
    
    db.session.commit()
    
    return {'message': 'Employee updated', 'employee': employee.to_dict()}, 200

@employee_bp.route('/<int:employee_id>', methods=['DELETE'])
@jwt_required()
def delete_employee(employee_id):
    """Soft delete employee"""
    current_user_id = int(get_jwt_identity())  # Convert back to int
    user = User.query.get(current_user_id)
    
    if not user or user.role not in ['admin', 'finance']:
        return {'error': 'Unauthorized'}, 401
    
    employee = Employee.query.get(employee_id)
    
    if not employee:
        return {'error': 'Employee not found'}, 404
    
    employee.is_active = False
    db.session.commit()
    
    return {'message': 'Employee deleted'}, 200

@employee_bp.route('/options', methods=['GET'])
@jwt_required()
def get_employee_options():
    """Get options for employee form dropdowns and statistics"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user or not user.can_manage_employees():
            return {'error': 'Unauthorized'}, 401
        
        # Get unique departments
        departments = db.session.query(Employee.department).filter(
            Employee.department.isnot(None),
            Employee.is_active == True
        ).distinct().all()
        
        # Get unique employment types
        employment_types = db.session.query(Employee.employment_type).filter(
            Employee.employment_type.isnot(None),
            Employee.is_active == True
        ).distinct().all()
        
        # Get employee statistics
        total_employees = Employee.query.filter_by(is_active=True).count()
        
        # Department distribution
        dept_stats = db.session.query(
            Employee.department, 
            db.func.count(Employee.id).label('count')
        ).filter_by(is_active=True).group_by(Employee.department).all()
        
        # Gender distribution
        gender_stats = db.session.query(
            Employee.gender,
            db.func.count(Employee.id).label('count')
        ).filter_by(is_active=True).group_by(Employee.gender).all()
        
        # Employment type distribution
        employment_stats = db.session.query(
            Employee.employment_type,
            db.func.count(Employee.id).label('count')
        ).filter_by(is_active=True).group_by(Employee.employment_type).all()
        
        return {
            'form_options': {
                'departments': [d[0] for d in departments if d[0]],
                'employment_types': [e[0] for e in employment_types if e[0]],
                'genders': ['Male', 'Female', 'Other', 'Prefer not to say'],
                'marital_statuses': ['Single', 'Married', 'Divorced', 'Widowed', 'Separated'],
                'employment_type_options': ['Full-time', 'Part-time', 'Contract', 'Temporary', 'Intern']
            },
            'statistics': {
                'total_employees': total_employees,
                'by_department': [{'department': d[0] or 'Unassigned', 'count': d[1]} for d in dept_stats],
                'by_gender': [{'gender': g[0] or 'Not specified', 'count': g[1]} for g in gender_stats],
                'by_employment_type': [{'type': e[0] or 'Not specified', 'count': e[1]} for e in employment_stats]
            }
        }, 200
        
    except Exception as e:
        print(f"ERROR: Failed to get employee options: {e}")
        return {'error': f'Failed to fetch employee options: {str(e)}'}, 500

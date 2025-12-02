from app import db

class Employee(db.Model):
    __tablename__ = 'employees'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    department = db.Column(db.String(100), index=True)
    position = db.Column(db.String(100))
    bank_account = db.Column(db.String(50))
    bank_name = db.Column(db.String(100))
    employee_id = db.Column(db.String(50), unique=True, nullable=False)
    hire_date = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True)
    
    # Personal Details
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))
    marital_status = db.Column(db.String(20))
    national_id = db.Column(db.String(50))
    tax_id = db.Column(db.String(50))
    address = db.Column(db.Text)
    
    # Emergency Contact
    emergency_contact_name = db.Column(db.String(255))
    emergency_contact_phone = db.Column(db.String(20))
    
    # Employment Details
    employment_type = db.Column(db.String(50))  # full-time, part-time, contract, etc.
    
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    # Relationships
    user = db.relationship('User', back_populates='employee')
    salaries = db.relationship('Salary', back_populates='employee', cascade='all, delete-orphan')
    allowances = db.relationship('Allowance', back_populates='employee', cascade='all, delete-orphan')
    deductions = db.relationship('Deduction', back_populates='employee', cascade='all, delete-orphan')
    payslips = db.relationship('Payslip', back_populates='employee', cascade='all, delete-orphan')
    payroll_runs = db.relationship('PayrollRun', back_populates='employee', cascade='all, delete-orphan')
    
    def to_dict(self):
        # Get current salary
        current_salary = None
        for salary in self.salaries:
            if salary.end_date is None or salary.end_date >= db.func.current_date():
                current_salary = salary.basic_salary
                break
        
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'department': self.department,
            'position': self.position,
            'employee_id': self.employee_id,
            'hire_date': self.hire_date.isoformat() if self.hire_date else None,
            'is_active': self.is_active,
            'basic_salary': float(current_salary) if current_salary else None,
            
            # Personal Details
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'gender': self.gender,
            'marital_status': self.marital_status,
            'national_id': self.national_id,
            'tax_id': self.tax_id,
            'address': self.address,
            
            # Emergency Contact
            'emergency_contact_name': self.emergency_contact_name,
            'emergency_contact_phone': self.emergency_contact_phone,
            
            # Employment Details
            'employment_type': self.employment_type,
            
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

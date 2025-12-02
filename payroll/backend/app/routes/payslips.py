from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Payslip, User, Employee
from app.services import PDFService
from io import BytesIO

payslip_bp = Blueprint('payslips', __name__, url_prefix='/api/payslips')

@payslip_bp.route('', methods=['GET'])
@jwt_required()
def get_payslips():
    """Get payslips with filters"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    employee_id = request.args.get('employee_id', type=int)
    payroll_run_id = request.args.get('payroll_run_id', type=int)
    
    query = Payslip.query
    
    # Employees can only see their own payslips
    if user.role == 'employee':
        employee = Employee.query.filter_by(user_id=user.id).first()
        if not employee:
            return {'error': 'Employee record not found'}, 404
        query = query.filter_by(employee_id=employee.id)
    else:
        if employee_id:
            query = query.filter_by(employee_id=employee_id)
    
    if payroll_run_id:
        query = query.filter_by(payroll_run_id=payroll_run_id)
    
    payslips = query.order_by(Payslip.created_at.desc()).paginate(page=page, per_page=per_page)
    
    # Include employee information in response
    result = []
    for payslip in payslips.items:
        payslip_data = payslip.to_dict()
        if payslip.employee:
            payslip_data['employee_name'] = payslip.employee.name
            payslip_data['employee_id_number'] = payslip.employee.employee_id
            payslip_data['department'] = payslip.employee.department
        if payslip.payroll_run:
            payslip_data['month'] = payslip.payroll_run.month
            payslip_data['year'] = payslip.payroll_run.year
        result.append(payslip_data)
    
    return {
        'payslips': result,
        'total': payslips.total,
        'pages': payslips.pages,
        'current_page': page
    }, 200

@payslip_bp.route('/<int:payslip_id>', methods=['GET'])
@jwt_required()
def get_payslip(payslip_id):
    """Get payslip details"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    payslip = Payslip.query.get(payslip_id)
    
    if not payslip:
        return {'error': 'Payslip not found'}, 404
    
    # Check access control
    if user.role == 'employee':
        employee = Employee.query.filter_by(user_id=user.id).first()
        if not employee or employee.id != payslip.employee_id:
            return {'error': 'Unauthorized'}, 401
    
    data = payslip.to_dict()
    data['details'] = [d.to_dict() for d in payslip.details]
    data['employee'] = payslip.employee.to_dict()
    
    return data, 200

@payslip_bp.route('/<int:payslip_id>/pdf', methods=['GET'])
@jwt_required()
def download_payslip_pdf(payslip_id):
    """Download payslip as PDF"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    payslip = Payslip.query.get(payslip_id)
    
    if not payslip:
        return {'error': 'Payslip not found'}, 404
    
    # Check access control
    if user.role == 'employee':
        employee = Employee.query.filter_by(user_id=user.id).first()
        if not employee or employee.id != payslip.employee_id:
            return {'error': 'Unauthorized'}, 401
    
    employee = payslip.employee
    payroll_run = payslip.payroll_run
    
    pdf_buffer = PDFService.generate_payslip_pdf(payslip, employee, payroll_run)
    
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'payslip_{employee.employee_id}_{payroll_run.year}_{payroll_run.month}.pdf'
    )

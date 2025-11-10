from flask import Blueprint, jsonify, request
from .. import db
from ..models import Employee

employees_bp = Blueprint("employees", __name__)

@employees_bp.route("/", methods=["GET"])
def list_employees():
    employees = Employee.query.all()
    data = [{"id": e.id, "name": e.name, "department": e.department, "base_salary": e.base_salary} for e in employees]
    return jsonify(data), 200

@employees_bp.route("/", methods=["POST"])
def add_employee():
    data = request.get_json() or {}
    name = data.get("name")
    department = data.get("department")
    base_salary = float(data.get("base_salary", 0))
    if not name:
        return jsonify({"error": "name is required"}), 400

    emp = Employee(name=name, department=department, base_salary=base_salary)
    db.session.add(emp)
    db.session.commit()
    return jsonify({"message": "Employee added", "id": emp.id}), 201

@employees_bp.route("/<int:emp_id>", methods=["GET"])
def get_employee(emp_id):
    emp = Employee.query.get_or_404(emp_id)
    return jsonify({"id": emp.id, "name": emp.name, "department": emp.department, "base_salary": emp.base_salary})

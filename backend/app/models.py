from . import db
from datetime import datetime

class Employee(db.Model):
    __tablename__ = "employee"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=True)
    base_salary = db.Column(db.Float, nullable=False, default=0.0)

    payslips = db.relationship("Payslip", backref="employee", lazy=True)

class Payslip(db.Model):
    __tablename__ = "payslip"
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employee.id"), nullable=False)
    month = db.Column(db.String(20), nullable=False)
    gross_salary = db.Column(db.Float, nullable=False)
    deductions = db.Column(db.Float, nullable=False)
    net_salary = db.Column(db.Float, nullable=False)
    date_generated = db.Column(db.DateTime, default=datetime.utcnow)

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<User {self.username}>"

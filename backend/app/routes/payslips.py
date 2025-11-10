from flask import Blueprint, jsonify, request
from .. import db
from ..models import Employee, Payslip

payslips_bp = Blueprint("payslips", __name__)

@payslips_bp.route("/generate/<int:emp_id>", methods=["POST"])
def generate_payslip(emp_id):
    emp = Employee.query.get_or_404(emp_id)
    gross = emp.base_salary
    deductions = round(0.10 * gross, 2)
    net = round(gross - deductions, 2)
    month = request.json.get("month") if request.json else None
    if not month:
        from datetime import datetime
        month = datetime.utcnow().strftime("%B %Y")

    payslip = Payslip(employee_id=emp.id, month=month, gross_salary=gross, deductions=deductions, net_salary=net)
    db.session.add(payslip)
    db.session.commit()
    return jsonify({"message": "Payslip generated", "payslip_id": payslip.id, "net": net}), 201

@payslips_bp.route("/employee/<int:emp_id>", methods=["GET"])
def list_payslips_for_employee(emp_id):
    payslips = Payslip.query.filter_by(employee_id=emp_id).all()
    data = [{"id": p.id, "month": p.month, "gross": p.gross_salary, "deductions": p.deductions, "net": p.net_salary} for p in payslips]
    return jsonify(data), 200

@payslips_bp.route("/<int:payslip_id>", methods=["GET"])
def get_payslip(payslip_id):
    p = Payslip.query.get_or_404(payslip_id)
    return jsonify({
        "id": p.id,
        "employee_id": p.employee_id,
        "month": p.month,
        "gross": p.gross_salary,
        "deductions": p.deductions,
        "net": p.net_salary,
        "date_generated": p.date_generated.isoformat() if hasattr(p, "date_generated") and p.date_generated else None,
    }), 200

# --- Analytics Blueprint ---
from datetime import datetime, timedelta
from sqlalchemy import func

analytics_bp = Blueprint("analytics", __name__)

@analytics_bp.route("/summary", methods=["GET"])
def analytics_summary():
    total_employees = db.session.query(func.count(Employee.id)).scalar() or 0
    total_payslips = db.session.query(func.count(Payslip.id)).scalar() or 0

    # Current month boundaries [first_day, first_day_next)
    now = datetime.utcnow()
    first_day = datetime(year=now.year, month=now.month, day=1)
    if now.month == 12:
        first_day_next = datetime(year=now.year + 1, month=1, day=1)
    else:
        first_day_next = datetime(year=now.year, month=now.month + 1, day=1)

    month_net_total = (
        db.session.query(func.coalesce(func.sum(Payslip.net_salary), 0.0))
        .filter(Payslip.date_generated >= first_day, Payslip.date_generated < first_day_next)
        .scalar()
        or 0.0
    )

    return jsonify({
        "total_employees": int(total_employees),
        "total_payslips": int(total_payslips),
        "month_net_total": float(month_net_total),
    })

@analytics_bp.route("/payroll_by_month", methods=["GET"])
def payroll_by_month():
    months = int(request.args.get("months", 6))
    now = datetime.utcnow()
    # compute start date months ago (approx by 31*months days back, then clamp to first of month)
    approx_start = now - timedelta(days=31 * months)
    start = datetime(year=approx_start.year, month=approx_start.month, day=1)

    rows = (
        db.session.query(
            func.year(Payslip.date_generated).label("y"),
            func.month(Payslip.date_generated).label("m"),
            func.coalesce(func.sum(Payslip.net_salary), 0.0).label("net")
        )
        .filter(Payslip.date_generated >= start)
        .group_by("y", "m")
        .order_by("y", "m")
        .all()
    )
    data = []
    for y, m, net in rows:
        data.append({"month": f"{int(y):04d}-{int(m):02d}", "net_total": float(net)})
    return jsonify(data)

@analytics_bp.route("/payroll_by_department", methods=["GET"])
def payroll_by_department():
    month_param = request.args.get("month")  # format YYYY-MM
    if month_param:
        try:
            year, month = map(int, month_param.split("-"))
            first_day = datetime(year=year, month=month, day=1)
            if month == 12:
                first_day_next = datetime(year=year + 1, month=1, day=1)
            else:
                first_day_next = datetime(year=year, month=month + 1, day=1)
        except Exception:
            return jsonify({"error": "Invalid month format. Use YYYY-MM"}), 400
    else:
        now = datetime.utcnow()
        first_day = datetime(year=now.year, month=now.month, day=1)
        if now.month == 12:
            first_day_next = datetime(year=now.year + 1, month=1, day=1)
        else:
            first_day_next = datetime(year=now.year, month=now.month + 1, day=1)

    q = (
        db.session.query(
            Employee.department.label("department"),
            func.coalesce(func.sum(Payslip.net_salary), 0.0).label("net")
        )
        .join(Employee, Employee.id == Payslip.employee_id)
        .filter(Payslip.date_generated >= first_day, Payslip.date_generated < first_day_next)
        .group_by(Employee.department)
        .order_by(func.coalesce(func.sum(Payslip.net_salary), 0.0).desc())
    )
    rows = q.all()
    data = [{"department": dept or "Unassigned", "net_total": float(net)} for dept, net in rows]
    return jsonify(data)

from .. import db
from ..models import Employee

def seed_sample_data():
    if Employee.query.count() == 0:
        sample = [
            Employee(name="Alice Mwangi", department="Engineering", base_salary=120000.0),
            Employee(name="Brian Otieno", department="Finance", base_salary=90000.0),
            Employee(name="Caroline Njeri", department="HR", base_salary=80000.0),
        ]
        db.session.bulk_save_objects(sample)
        db.session.commit()
        print("Seeded sample employees.")
    else:
        print("Seed data already present.")

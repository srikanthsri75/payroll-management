import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    load_dotenv()
    app = Flask(__name__)
    CORS(app)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
            'DATABASE_URL',
            'mysql+pymysql://payrolluser:payroll123456789@127.0.0.1:3306/payroll_db'
            )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', os.getenv('SECRET_KEY', 'devkey'))

    db.init_app(app)
    migrate.init_app(app, db)
    JWTManager(app)

    from .routes.employees import employees_bp
    from .routes.payslips import payslips_bp, analytics_bp
    from .routes import auth_bp
    app.register_blueprint(employees_bp, url_prefix='/api/employees')
    app.register_blueprint(payslips_bp, url_prefix='/api/payslips')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    return app

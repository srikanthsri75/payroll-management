import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import load_dotenv

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    load_dotenv()  # loads .env
    app = Flask(__name__)
    CORS(app)

    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'devkey')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL',
        'mysql+pymysql://root:password@127.0.0.1:3306/payroll_db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Init extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Register routes blueprints
    from .routes.employees import employees_bp
    from .routes.payslips import payslips_bp
    app.register_blueprint(employees_bp, url_prefix='/api/employees')
    app.register_blueprint(payslips_bp, url_prefix='/api/payslips')

    return app

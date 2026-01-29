from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Printer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.String(50), unique=True, nullable=False)
    model_name = db.Column(db.String(100), nullable=False)
    serial_number = db.Column(db.String(50), nullable=False)
    jobs = db.relationship('Job', backref='printer', lazy=True)

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_number = db.Column(db.Integer, unique=True, nullable=False)
    job_kind = db.Column(db.String(20), nullable=False)
    job_name = db.Column(db.String(200), nullable=False)
    job_result = db.Column(db.String(10), nullable=False)
    job_result_detail = db.Column(db.Integer, nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    account_name = db.Column(db.String(100))
    account_code = db.Column(db.String(100))
    pages = db.Column(db.Integer, nullable=False)
    user_name = db.Column(db.String(100))
    login_id = db.Column(db.String(100))
    operation_executioner_login_id = db.Column(db.String(100))
    operation_executioner_domain_name = db.Column(db.String(100))
    print_color_mode = db.Column(db.String(20))
    complete_copies = db.Column(db.Integer)
    copies = db.Column(db.Integer)
    complete_pages = db.Column(db.Integer)
    printer_id = db.Column(db.Integer, db.ForeignKey('printer.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
from flask import Flask, render_template, request, jsonify, redirect, url_for
from models import db, Printer, Job
from email_fetcher import fetch_emails
import schedule
import threading
import time
import os
from dotenv import load_dotenv

load_dotenv()

# Ensure data directory exists with proper permissions
data_dir = os.path.join(os.getcwd(), 'data')
os.makedirs(data_dir, exist_ok=True)
print(f"Data directory: {data_dir} (exists: {os.path.exists(data_dir)}, writable: {os.access(data_dir, os.W_OK)})")

# Use absolute path for database
db_path = os.path.join(data_dir, 'kyocera_reports.db')
default_db_uri = f'sqlite:///{db_path}'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI', default_db_uri)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def run_scheduler():
    # Only run scheduler if POP3 credentials are configured
    if all([os.getenv('POP3_SERVER'), os.getenv('POP3_USERNAME'), os.getenv('POP3_PASSWORD')]):
        schedule.every(10).minutes.do(fetch_emails)
        print("Email scheduler started - fetching every 10 minutes")
    else:
        print("Warning: POP3 credentials not configured - email scheduler disabled")
    
    while True:
        schedule.run_pending()
        time.sleep(1)

@app.route('/')
def index():
    printers = Printer.query.all()
    return render_template('index.html', printers=printers)

@app.route('/stats/<int:printer_id>')
def stats(printer_id):
    printer = Printer.query.get_or_404(printer_id)
    
    # Get filter parameters
    user_filter = request.args.get('user')
    color_filter = request.args.get('color')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    sort = request.args.get('sort', 'job_number')
    order = request.args.get('order', 'desc')
    
    # Build query
    query = Job.query.filter_by(printer_id=printer_id)
    if user_filter:
        query = query.filter_by(user_name=user_filter)
    if color_filter:
        query = query.filter_by(print_color_mode=color_filter)
    
    # Sorting
    if hasattr(Job, sort):
        if order == 'asc':
            query = query.order_by(getattr(Job, sort).asc())
        else:
            query = query.order_by(getattr(Job, sort).desc())
    
    # Paginate
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    jobs = pagination.items

    # Calculate statistics based on filtered query
    total_jobs = query.count()
    total_pages_sum = query.with_entities(db.func.sum(Job.pages)).scalar() or 0
    total_color_pages = query.filter(Job.print_color_mode == 'FULL_COLOR').with_entities(db.func.sum(Job.complete_pages)).scalar() or 0
    users = set(query.with_entities(Job.user_name).filter(Job.user_name != '').all())
    users = {u[0] for u in users}

    return render_template('stats.html', printer=printer, jobs=jobs, pagination=pagination, total_jobs=total_jobs, total_pages=total_pages_sum, total_color_pages=total_color_pages, users=users, sort=sort, order=order)

@app.route('/delete_job/<int:job_id>', methods=['POST'])
def delete_job(job_id):
    job = Job.query.get_or_404(job_id)
    printer_id = job.printer_id
    db.session.delete(job)
    db.session.commit()
    return redirect(url_for('stats', printer_id=printer_id))

@app.route('/delete_jobs', methods=['POST'])
def delete_jobs():
    job_ids = request.form.getlist('job_ids')
    printer_id = None
    for job_id in job_ids:
        job = Job.query.get(int(job_id))
        if job:
            if printer_id is None:
                printer_id = job.printer_id
            db.session.delete(job)
    db.session.commit()
    return redirect(url_for('stats', printer_id=printer_id) if printer_id else url_for('index'))

@app.route('/api/fetch_emails', methods=['POST'])
def api_fetch_emails():
    try:
        fetch_emails()
        return jsonify({'status': 'success', 'message': 'Emails fetched and processed'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    # Initialize database
    with app.app_context():
        try:
            db.create_all()
            print("Database initialized successfully")
        except Exception as e:
            print(f"Error initializing database: {e}")
            print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
            print(f"Current working directory: {os.getcwd()}")
            print(f"Data directory exists: {os.path.exists('data')}")
            print(f"Data directory writable: {os.access('data', os.W_OK) if os.path.exists('data') else 'N/A'}")
            raise
    
    # Start scheduler in background
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()

    app.run(debug=True, host='0.0.0.0', port=5000)
else:
    # Running under Gunicorn - initialize database and start scheduler
    with app.app_context():
        try:
            db.create_all()
            print("Database initialized successfully (Gunicorn)")
        except Exception as e:
            print(f"Error initializing database: {e}")
    
    # Start scheduler in background for Gunicorn
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()
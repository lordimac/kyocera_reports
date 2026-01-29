import xml.etree.ElementTree as ET
from models import db, Printer, Job
from app import app

def test_parse_xml():
    with app.app_context():
        db.create_all()  # Create tables
        # Parse the existing XML file
        tree = ET.parse('export_job_logResponse.xml')
        root = tree.getroot()
        namespace = {'kmloginfo': 'http://www.kyoceramita.com/ws/km-wsdl/log/log_information'}

        # Get or create printer
        printer = Printer.query.filter_by(equipment_id="prn-bln-02-mfp").first()
        if not printer:
            printer = Printer(equipment_id="prn-bln-02-mfp", model_name="ECOSYS M5521cdn", serial_number="VDX9X39783")
            db.session.add(printer)
            db.session.commit()

        for job_log in root.findall('.//kmloginfo:print_job_log', namespace):
            # Use the parse_job_data function from email_fetcher
            from email_fetcher import parse_job_data
            job_data = parse_job_data(job_log, namespace)
            job_data['printer_id'] = printer.id

            # Check if job already exists
            existing_job = Job.query.filter_by(job_number=job_data['job_number']).first()
            if not existing_job:
                job = Job(**job_data)
                db.session.add(job)

        db.session.commit()
        print("XML parsed and stored successfully")

if __name__ == '__main__':
    test_parse_xml()
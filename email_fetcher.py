import poplib
import email
import xml.etree.ElementTree as ET
from email.mime.text import MIMEText
from models import db, Printer, Job
import os
from datetime import datetime

def fetch_emails():
    # POP3 settings from environment
    pop3_server = os.getenv('POP3_SERVER')
    pop3_port = int(os.getenv('POP3_PORT', 995))
    username = os.getenv('POP3_USERNAME')
    password = os.getenv('POP3_PASSWORD')

    if not all([pop3_server, username, password]):
        print("POP3 credentials not configured")
        return

    try:
        mail = poplib.POP3_SSL(pop3_server, pop3_port)
        mail.user(username)
        mail.pass_(password)

        num_messages = len(mail.list()[1])

        for i in range(num_messages):
            raw_email = b"\n".join(mail.retr(i+1)[1])
            email_message = email.message_from_bytes(raw_email)

            # Parse email body to identify printer
            body = get_email_body(email_message)
            printer_id = identify_printer(body)

            if printer_id:
                # Extract XML attachment
                xml_content = extract_xml_attachment(email_message)
                if xml_content:
                    parse_and_store_xml(xml_content, printer_id)
                    # Delete email after processing
                    mail.dele(i+1)

        mail.quit()
    except Exception as e:
        print(f"Error fetching emails: {e}")

def get_email_body(email_message):
    if email_message.is_multipart():
        for part in email_message.walk():
            if part.get_content_type() == "text/plain":
                return part.get_payload(decode=True).decode('utf-8')
    else:
        return email_message.get_payload(decode=True).decode('utf-8')
    return ""

def identify_printer(body):
    # Simple identification based on equipment ID in body
    if "prn-bln-02-mfp" in body:
        return "prn-bln-02-mfp"
    # Add more printers as needed
    return None

def extract_xml_attachment(email_message):
    for part in email_message.walk():
        if part.get_content_type() == "application/xml" or part.get_filename() and part.get_filename().endswith('.xml'):
            return part.get_payload(decode=True).decode('utf-8')
    return None

def parse_and_store_xml(xml_content, printer_id):
    try:
        root = ET.fromstring(xml_content)
        namespace = {'kmloginfo': 'http://www.kyoceramita.com/ws/km-wsdl/log/log_information'}

        # Get or create printer
        printer = Printer.query.filter_by(equipment_id=printer_id).first()
        if not printer:
            # For now, assume known printers; in production, add dynamically
            printer = Printer(equipment_id=printer_id, model_name="ECOSYS M5521cdn", serial_number="VDX9X39783")
            db.session.add(printer)
            db.session.commit()

        for job_log in root.findall('.//kmloginfo:print_job_log', namespace):
            job_data = parse_job_data(job_log, namespace)
            job_data['printer_id'] = printer.id

            # Check if job already exists
            existing_job = Job.query.filter_by(job_number=job_data['job_number']).first()
            if not existing_job:
                job = Job(**job_data)
                db.session.add(job)

        db.session.commit()
    except Exception as e:
        print(f"Error parsing XML: {e}")

def parse_job_data(job_log, namespace):
    common = job_log.find('kmloginfo:common', namespace)
    detail = job_log.find('kmloginfo:detail', namespace)

    def parse_time(time_elem):
        return datetime(
            year=int(time_elem.find('kmloginfo:year', namespace).text) + 1900,
            month=int(time_elem.find('kmloginfo:month', namespace).text) + 1,
            day=int(time_elem.find('kmloginfo:day', namespace).text),
            hour=int(time_elem.find('kmloginfo:hour', namespace).text),
            minute=int(time_elem.find('kmloginfo:minute', namespace).text),
            second=int(time_elem.find('kmloginfo:second', namespace).text)
        )

    return {
        'job_number': int(common.find('kmloginfo:job_number', namespace).text),
        'job_kind': common.find('kmloginfo:job_kind', namespace).text,
        'job_name': common.find('kmloginfo:job_name', namespace).text,
        'job_result': common.find('kmloginfo:job_result', namespace).text,
        'job_result_detail': int(common.find('kmloginfo:job_result_detail', namespace).text),
        'start_time': parse_time(common.find('kmloginfo:start_time', namespace)),
        'end_time': parse_time(common.find('kmloginfo:end_time', namespace)),
        'account_name': common.find('kmloginfo:account_name', namespace).text or '',
        'account_code': common.find('kmloginfo:account_code', namespace).text or '',
        'pages': int(common.find('kmloginfo:pages', namespace).text),
        'user_name': common.find('kmloginfo:user_name', namespace).text or '',
        'login_id': common.find('kmloginfo:login_id', namespace).text or '',
        'operation_executioner_login_id': common.find('kmloginfo:operation_executioner_login_id', namespace).text or '',
        'operation_executioner_domain_name': common.find('kmloginfo:operation_executioner_domain_name', namespace).text or '',
        'print_color_mode': detail.find('kmloginfo:print_color_mode', namespace).text if detail is not None else '',
        'complete_copies': int(detail.find('kmloginfo:complete_copies', namespace).text) if detail is not None and detail.find('kmloginfo:complete_copies', namespace) is not None else 0,
        'copies': int(detail.find('kmloginfo:copies', namespace).text) if detail is not None and detail.find('kmloginfo:copies', namespace) is not None else 0,
        'complete_pages': int(detail.find('kmloginfo:complete_pages', namespace).text) if detail is not None and detail.find('kmloginfo:complete_pages', namespace) is not None else 0,
    }
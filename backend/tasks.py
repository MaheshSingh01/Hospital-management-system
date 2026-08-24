import csv
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from celery import Celery
from celery.schedules import crontab
from models import db, Appointment, User
from datetime import date, timedelta

GMAIL_USER = 'maheshsingh20oct@gmail.com'
GMAIL_PASS = 'htmfbkeqypssbhop'

def send_email(to_email, subject, body_html):
    if not to_email:
        print(f"[EMAIL] No email address found, skipping...")
        return
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = GMAIL_USER
        msg['To'] = to_email
        msg.attach(MIMEText(body_html, 'html'))
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(GMAIL_USER, GMAIL_PASS)
            server.sendmail(GMAIL_USER, to_email, msg.as_string())
        print(f"[EMAIL] Sent to {to_email}")
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")

def build_celery(flask_app):
    celery = Celery(
        flask_app.import_name,
        broker='redis://127.0.0.1:6380/0',
        backend='redis://127.0.0.1:6380/0'
    )

    celery.conf.update(
        broker_url='redis://127.0.0.1:6380/0',
        result_backend='redis://127.0.0.1:6380/0',
        broker_connection_retry_on_startup=True,
        beat_schedule={
            'daily-reminder-morning': {
                'task': 'tasks.send_daily_reminders',
                'schedule': crontab(hour=8, minute=0),
            },
            'monthly-doctor-report': {
                'task': 'tasks.generate_monthly_reports',
                'schedule': crontab(0, 0, day_of_month='1'),
            },
        }
    )

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with flask_app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask

    @celery.task(name="tasks.send_daily_reminders")
    def send_daily_reminders():
        today = date.today()
        appointments = Appointment.query.filter_by(
            scheduled_date=today, booking_status='Booked'
        ).all()
        count = 0
        for appt in appointments:
            patient = appt.visiting_patient
            doctor = appt.attending_doctor
            subject = "Reminder: Your Appointment Today"
            body = f"""
            <html><body>
            <h2>Appointment Reminder</h2>
            <p>Dear <b>{patient.full_name}</b>,</p>
            <p>You have an appointment today.</p>
            <ul>
                <li><b>Doctor:</b> Dr. {doctor.full_name}</li>
                <li><b>Date:</b> {appt.scheduled_date}</li>
                <li><b>Time:</b> {appt.scheduled_time}</li>
            </ul>
            <p>Please arrive 10 minutes early.</p>
            <p>— Nivea Health Care Team</p>
            </body></html>
            """
            print(f"[REMINDER] Sending to {patient.full_name} at {patient.email}")
            send_email(patient.email, subject, body)
            count += 1
        return f"Reminders sent: {count}"

    @celery.task(name="tasks.generate_monthly_reports")
    def generate_monthly_reports():
        doctors = User.query.filter_by(acc_type='doctor').all()
        today = date.today()
        first_day = today.replace(day=1)
        last_month = first_day - timedelta(days=1)
        month_start = last_month.replace(day=1)

        for doctor in doctors:
            appointments = Appointment.query.filter(
                Appointment.doctor_id == doctor.id,
                Appointment.scheduled_date >= month_start,
                Appointment.scheduled_date <= last_month,
                Appointment.booking_status == 'Completed'
            ).all()

            rows = ""
            for a in appointments:
                diag = a.visit_record.diagnosis_text if a.visit_record else "N/A"
                pres = a.visit_record.prescription_text if a.visit_record else "N/A"
                rows += f"""
                <tr>
                    <td>{a.scheduled_date}</td>
                    <td>{a.visiting_patient.full_name}</td>
                    <td>{diag}</td>
                    <td>{pres}</td>
                </tr>"""

            report_html = f"""
            <html><body>
            <h2>Monthly Activity Report — {last_month.strftime('%B %Y')}</h2>
            <p>Doctor: <b>Dr. {doctor.full_name}</b></p>
            <p>Total Completed Appointments: <b>{len(appointments)}</b></p>
            <table border='1' cellpadding='8' cellspacing='0' style='border-collapse:collapse;width:100%'>
                <tr style='background:#1b6ca8;color:#fff'>
                    <th>Date</th><th>Patient</th><th>Diagnosis</th><th>Prescription</th>
                </tr>
                {rows}
            </table>
            <br><p>— Nivea Health Care Auto Report</p>
            </body></html>
            """

            os.makedirs('reports', exist_ok=True)
            filename = f"reports/report_{doctor.username}_{last_month.strftime('%Y_%m')}.html"
            with open(filename, 'w') as f:
                f.write(report_html)

            subject = f"Monthly Report — {last_month.strftime('%B %Y')}"
            print(f"[REPORT] Sending to Dr. {doctor.full_name} at {doctor.email}")
            send_email(doctor.email, subject, report_html)

        return f"Monthly reports generated for {len(doctors)} doctors"

    @celery.task(name="tasks.export_patient_csv")
    def export_patient_csv(patient_id):
        patient = User.query.get(patient_id)
        appointments = Appointment.query.filter_by(patient_id=patient_id).all()

        os.makedirs('exports', exist_ok=True)
        filename = f"exports/history_{patient.username}.csv"

        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Date', 'Time', 'Doctor', 'Department',
                'Status', 'Diagnosis', 'Prescription', 'Notes'
            ])
            for a in appointments:
                dept = a.attending_doctor.department.name if a.attending_doctor.department else 'General'
                diag = a.visit_record.diagnosis_text if a.visit_record else 'N/A'
                pres = a.visit_record.prescription_text if a.visit_record else 'N/A'
                notes = a.visit_record.follow_up_notes if a.visit_record else 'N/A'
                writer.writerow([
                    a.scheduled_date, a.scheduled_time,
                    a.attending_doctor.full_name, dept,
                    a.booking_status, diag, pres, notes
                ])

        subject = "Your Treatment History Export is Ready"
        body = f"""
        <html><body>
        <h2>Export Ready</h2>
        <p>Dear {patient.full_name}, your treatment history CSV has been generated.</p>
        <p>File: <b>{filename}</b></p>
        <p>— Nivea Health Care Team</p>
        </body></html>
        """
        print(f"[EXPORT] CSV ready for {patient.full_name} at {patient.email}")
        send_email(patient.email, subject, body)
        return filename

    build_celery.send_daily_reminders = send_daily_reminders
    build_celery.generate_monthly_reports = generate_monthly_reports
    build_celery.export_patient_csv = export_patient_csv

    return celery

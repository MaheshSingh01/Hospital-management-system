from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, User, Appointment, Treatment, DoctorAvailability
from datetime import datetime, timedelta, date
from utils import login_required, role_required

doctor_bp = Blueprint('doctor', __name__)


@doctor_bp.route('/dashboard')
@login_required
@role_required('doctor')
def dashboard():
    doctor_id = session.get('user_id')
    
    today = date.today()
    week_end = today + timedelta(days=7)
    
    today_appts = Appointment.query.filter(
        Appointment.doctor_id == doctor_id,
        Appointment.date == today
    ).all()
    
    week_appts = Appointment.query.filter(
        Appointment.doctor_id == doctor_id,
        Appointment.date >= today,
        Appointment.date <= week_end
    ).order_by(Appointment.date).all()
    
    total_patients = db.session.query(Appointment.patient_id).filter(
        Appointment.doctor_id == doctor_id
    ).distinct().count()
    
    return render_template('doctor/dashboard.html',
                         today_appts=today_appts,
                         week_appts=week_appts,
                         total_patients=total_patients,
                         today=today)


@doctor_bp.route('/appointments')
@login_required
@role_required('doctor')
def appointments():
    doctor_id = session.get('user_id')
    
    filter_type = request.args.get('filter', 'all')
    
    query = Appointment.query.filter_by(doctor_id=doctor_id)
    
    if filter_type == 'today':
        query = query.filter_by(date=date.today())
    elif filter_type == 'week':
        week_end = date.today() + timedelta(days=7)
        query = query.filter(
            Appointment.date >= date.today(),
            Appointment.date <= week_end
        )
    elif filter_type == 'pending':
        query = query.filter_by(curr_status='Booked')
    
    appts = query.order_by(Appointment.date.desc()).all()
    
    return render_template('doctor/appointments.html', 
                         appointments=appts, 
                         filter_type=filter_type)


@doctor_bp.route('/appointment/<int:id>')
@login_required
@role_required('doctor')
def view_appointment(id):
    doctor_id = session.get('user_id')
    appt = Appointment.query.filter_by(id=id, doctor_id=doctor_id).first_or_404()
    
    treatment = Treatment.query.filter_by(appointment_id=id).first()
    
    patient_history = Appointment.query.filter_by(
        patient_id=appt.patient_id
    ).order_by(Appointment.date.desc()).all()
    
    return render_template('doctor/appointment_detail.html',
                         appointment=appt,
                         treatment=treatment,
                         patient_history=patient_history)


@doctor_bp.route('/appointment/<int:id>/update', methods=['POST'])
@login_required
@role_required('doctor')
def update_appointment(id):
    doctor_id = session.get('user_id')
    appt = Appointment.query.filter_by(id=id, doctor_id=doctor_id).first_or_404()
    
    action = request.form.get('action')
    
    if action == 'complete':
        appt.curr_status = 'Completed'
        diagnosis = request.form.get('diagnosis')
        prescription = request.form.get('prescription')
        notes = request.form.get('notes')
        
        treatment = Treatment.query.filter_by(appointment_id=id).first()
        if treatment:
            treatment.diagnosis = diagnosis
            treatment.prescription = prescription
            treatment.medical_notes = notes
        else:
            treatment = Treatment(
                appointment_id=id,
                diagnosis=diagnosis,
                prescription=prescription,
                medical_notes=notes
            )
            db.session.add(treatment)
        
        flash('Appointment marked as completed', 'success')
    
    elif action == 'cancel':
        appt.curr_status = 'Cancelled'
        flash('Appointment cancelled', 'info')
    
    db.session.commit()
    return redirect(url_for('doctor.appointments'))


@doctor_bp.route('/availability')
@login_required
@role_required('doctor')
def availability():
    doctor_id = session.get('user_id')
    
    today = date.today()
    next_7_days = [today + timedelta(days=i) for i in range(7)]
    
    availability_data = {}
    for day in next_7_days:
        avail = DoctorAvailability.query.filter_by(
            doctor_id=doctor_id,
            date=day
        ).all()
        availability_data[day] = avail
    
    return render_template('doctor/availability.html',
                         next_7_days=next_7_days,
                         availability_data=availability_data)


@doctor_bp.route('/availability/update', methods=['POST'])
@login_required
@role_required('doctor')
def update_availability():
    doctor_id = session.get('user_id')
    
    selected_date = request.form.get('date')
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')
    
    if selected_date and start_time and end_time:
        avail_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
        
        existing = DoctorAvailability.query.filter_by(
            doctor_id=doctor_id,
            date=avail_date,
            start_time=start_time
        ).first()
        
        if existing:
            flash('Availability already set for this time', 'warning')
        else:
            availability = DoctorAvailability(
                doctor_id=doctor_id,
                date=avail_date,
                start_time=start_time,
                end_time=end_time,
                is_available=True
            )
            db.session.add(availability)
            db.session.commit()
            flash('Availability updated', 'success')
    
    return redirect(url_for('doctor.availability'))


@doctor_bp.route('/availability/delete/<int:id>', methods=['POST'])
@login_required
@role_required('doctor')
def delete_availability(id):
    doctor_id = session.get('user_id')
    avail = DoctorAvailability.query.filter_by(id=id, doctor_id=doctor_id).first_or_404()
    
    db.session.delete(avail)
    db.session.commit()
    
    flash('Availability slot removed', 'success')
    return redirect(url_for('doctor.availability'))


@doctor_bp.route('/patients')
@login_required
@role_required('doctor')
def patients():
    doctor_id = session.get('user_id')
    
    patient_ids = db.session.query(Appointment.patient_id).filter(
        Appointment.doctor_id == doctor_id
    ).distinct().all()
    
    patient_ids = [p[0] for p in patient_ids]
    patients_list = User.query.filter(User.id.in_(patient_ids)).all()
    
    return render_template('doctor/patients.html', patients=patients_list)


@doctor_bp.route('/patient/<int:id>')
@login_required
@role_required('doctor')
def patient_history(id):
    doctor_id = session.get('user_id')
    
    patient = User.query.get_or_404(id)
    
    history = Appointment.query.filter_by(patient_id=id).order_by(
        Appointment.date.desc()
    ).all()
    
    return render_template('doctor/patient_history.html',
                         patient=patient,
                         history=history)
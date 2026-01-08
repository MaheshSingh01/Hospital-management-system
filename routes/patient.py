from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, User, Appointment, Treatment, Department, DoctorAvailability
from datetime import datetime, date, timedelta
from utils import login_required, role_required

patient_bp = Blueprint('patient', __name__)


@patient_bp.route('/dashboard')
@login_required
@role_required('patient')
def dashboard():
    patient_id = session.get('user_id')
    
    today = date.today()
    
    upcoming = Appointment.query.filter(
        Appointment.patient_id == patient_id,
        Appointment.date >= today
    ).order_by(Appointment.date).all()
    
    past = Appointment.query.filter(
        Appointment.patient_id == patient_id,
        Appointment.date < today
    ).order_by(Appointment.date.desc()).limit(5).all()
    
    departments = Department.query.all()
    
    return render_template('patient/dashboard.html',
                         upcoming=upcoming,
                         past=past,
                         departments=departments,
                         today=today)


@patient_bp.route('/profile')
@login_required
@role_required('patient')
def profile():
    patient_id = session.get('user_id')
    patient = User.query.get_or_404(patient_id)
    
    return render_template('patient/profile.html', patient=patient)


@patient_bp.route('/profile/update', methods=['POST'])
@login_required
@role_required('patient')
def update_profile():
    patient_id = session.get('user_id')
    patient = User.query.get_or_404(patient_id)
    
    patient.name = request.form.get('name')
    patient.contact_num = request.form.get('contact_num')
    patient.user_addr = request.form.get('user_addr')
    
    new_password = request.form.get('new_password')
    if new_password:
        patient.password = new_password
    
    db.session.commit()
    session['name'] = patient.name
    
    flash('Profile updated successfully', 'success')
    return redirect(url_for('patient.profile'))


@patient_bp.route('/doctors')
@login_required
@role_required('patient')
def doctors():
    search_query = request.args.get('search', '')
    dept_filter = request.args.get('department', '')
    
    query = User.query.filter_by(acc_type='doctor', admin_verified=True)
    
    if search_query:
        query = query.filter(User.name.contains(search_query))
    
    if dept_filter:
        query = query.filter_by(department_id=dept_filter)
    
    doctors_list = query.all()
    departments = Department.query.all()
    
    return render_template('patient/doctors.html',
                         doctors=doctors_list,
                         departments=departments,
                         search_query=search_query,
                         dept_filter=dept_filter)


@patient_bp.route('/doctor/<int:id>')
@login_required
@role_required('patient')
def view_doctor(id):
    doctor = User.query.filter_by(id=id, acc_type='doctor').first_or_404()
    
    today = date.today()
    next_7_days = [today + timedelta(days=i) for i in range(7)]
    
    availability = {}
    for day in next_7_days:
        slots = DoctorAvailability.query.filter_by(
            doctor_id=id,
            date=day,
            is_available=True
        ).all()
        
        booked_slots = Appointment.query.filter_by(
            doctor_id=id,
            date=day
        ).filter(Appointment.curr_status != 'Cancelled').all()
        
        booked_times = [appt.appt_time for appt in booked_slots]
        
        available_slots = [slot for slot in slots if slot.start_time not in booked_times]
        
        if available_slots:
            availability[day] = available_slots
    
    return render_template('patient/doctor_detail.html',
                         doctor=doctor,
                         availability=availability,
                         next_7_days=next_7_days)


@patient_bp.route('/book/<int:doctor_id>', methods=['POST'])
@login_required
@role_required('patient')
def book_appointment(doctor_id):
    patient_id = session.get('user_id')
    
    appt_date = request.form.get('date')
    appt_time = request.form.get('time')
    
    if not appt_date or not appt_time:
        flash('Please select date and time', 'danger')
        return redirect(url_for('patient.view_doctor', id=doctor_id))
    
    appt_date_obj = datetime.strptime(appt_date, '%Y-%m-%d').date()
    
    existing = Appointment.query.filter_by(
        doctor_id=doctor_id,
        date=appt_date_obj,
        appt_time=appt_time
    ).filter(Appointment.curr_status != 'Cancelled').first()
    
    if existing:
        flash('This time slot is already booked', 'warning')
        return redirect(url_for('patient.view_doctor', id=doctor_id))
    
    appointment = Appointment(
        doctor_id=doctor_id,
        patient_id=patient_id,
        date=appt_date_obj,
        appt_time=appt_time,
        curr_status='Booked'
    )
    
    db.session.add(appointment)
    db.session.commit()
    
    flash('Appointment booked successfully', 'success')
    return redirect(url_for('patient.appointments'))


@patient_bp.route('/appointments')
@login_required
@role_required('patient')
def appointments():
    patient_id = session.get('user_id')
    
    filter_type = request.args.get('filter', 'upcoming')
    
    today = date.today()
    
    if filter_type == 'upcoming':
        appts = Appointment.query.filter(
            Appointment.patient_id == patient_id,
            Appointment.date >= today
        ).order_by(Appointment.date).all()
    elif filter_type == 'past':
        appts = Appointment.query.filter(
            Appointment.patient_id == patient_id,
            Appointment.date < today
        ).order_by(Appointment.date.desc()).all()
    else:
        appts = Appointment.query.filter_by(
            patient_id=patient_id
        ).order_by(Appointment.date.desc()).all()
    
    return render_template('patient/appointments.html',
                         appointments=appts,
                         filter_type=filter_type)


@patient_bp.route('/appointment/<int:id>')
@login_required
@role_required('patient')
def view_appointment(id):
    patient_id = session.get('user_id')
    appt = Appointment.query.filter_by(id=id, patient_id=patient_id).first_or_404()
    
    treatment = Treatment.query.filter_by(appointment_id=id).first()
    
    can_reschedule = appt.date >= date.today() and appt.curr_status == 'Booked'
    
    return render_template('patient/appointment_detail.html',
                         appointment=appt,
                         treatment=treatment,
                         can_reschedule=can_reschedule)


@patient_bp.route('/appointment/<int:id>/cancel', methods=['POST'])
@login_required
@role_required('patient')
def cancel_appointment(id):
    patient_id = session.get('user_id')
    appt = Appointment.query.filter_by(id=id, patient_id=patient_id).first_or_404()
    
    if appt.curr_status == 'Booked':
        appt.curr_status = 'Cancelled'
        db.session.commit()
        flash('Appointment cancelled', 'info')
    else:
        flash('Cannot cancel this appointment', 'warning')
    
    return redirect(url_for('patient.appointments'))


@patient_bp.route('/appointment/<int:id>/reschedule')
@login_required
@role_required('patient')
def reschedule_form(id):
    patient_id = session.get('user_id')
    appt = Appointment.query.filter_by(id=id, patient_id=patient_id).first_or_404()
    
    if appt.date < date.today() or appt.curr_status != 'Booked':
        flash('Cannot reschedule this appointment', 'warning')
        return redirect(url_for('patient.appointments'))
    
    doctor = appt.doctor
    today = date.today()
    next_7_days = [today + timedelta(days=i) for i in range(7)]
    
    availability = {}
    for day in next_7_days:
        slots = DoctorAvailability.query.filter_by(
            doctor_id=doctor.id,
            date=day,
            is_available=True
        ).all()
        
        booked_slots = Appointment.query.filter_by(
            doctor_id=doctor.id,
            date=day
        ).filter(Appointment.curr_status != 'Cancelled', Appointment.id != id).all()
        
        booked_times = [booked.appt_time for booked in booked_slots]
        
        available_slots = [slot for slot in slots if slot.start_time not in booked_times]
        
        if available_slots:
            availability[day] = available_slots
    
    return render_template('patient/reschedule.html',
                         appointment=appt,
                         doctor=doctor,
                         availability=availability,
                         next_7_days=next_7_days)


@patient_bp.route('/appointment/<int:id>/reschedule', methods=['POST'])
@login_required
@role_required('patient')
def reschedule_appointment(id):
    patient_id = session.get('user_id')
    appt = Appointment.query.filter_by(id=id, patient_id=patient_id).first_or_404()
    
    new_date = request.form.get('date')
    new_time = request.form.get('time')
    
    if not new_date or not new_time:
        flash('Please select date and time', 'danger')
        return redirect(url_for('patient.reschedule_form', id=id))
    
    new_date_obj = datetime.strptime(new_date, '%Y-%m-%d').date()
    
    existing = Appointment.query.filter_by(
        doctor_id=appt.doctor_id,
        date=new_date_obj,
        appt_time=new_time
    ).filter(Appointment.curr_status != 'Cancelled', Appointment.id != id).first()
    
    if existing:
        flash('This time slot is already booked', 'warning')
        return redirect(url_for('patient.reschedule_form', id=id))
    
    appt.date = new_date_obj
    appt.appt_time = new_time
    db.session.commit()
    
    flash('Appointment rescheduled successfully', 'success')
    return redirect(url_for('patient.appointments'))
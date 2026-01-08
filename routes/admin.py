from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, User, Department, Appointment
from utils import login_required, role_required

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/dashboard')
@login_required
@role_required('admin')
def dashboard():
    total_doctors = User.query.filter_by(acc_type='doctor').count()
    total_patients = User.query.filter_by(acc_type='patient').count()
    total_appointments = Appointment.query.count()
    
    return render_template('admin/dashboard.html',
                         total_doctors=total_doctors,
                         total_patients=total_patients,
                         total_appointments=total_appointments)


@admin_bp.route('/doctors')
@login_required
@role_required('admin')
def doctors():
    search = request.args.get('search', '')
    
    if search:
        doctors = User.query.filter(
            User.acc_type == 'doctor',
            (User.name.contains(search)) | 
            (User.department.has(Department.name.contains(search)))
        ).all()
    else:
        doctors = User.query.filter_by(acc_type='doctor').all()
    
    departments = Department.query.all()
    return render_template('admin/doctors.html', doctors=doctors, 
                         departments=departments, search=search)


@admin_bp.route('/doctors/add', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def add_doctor():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        name = request.form.get('name')
        contact = request.form.get('contact')
        address = request.form.get('address')
        dept_id = request.form.get('department_id')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('admin.add_doctor'))
        
        doctor = User(
            username=username,
            password=password,
            acc_type='doctor',
            name=name,
            contact_num=contact,
            user_addr=address,
            department_id=dept_id if dept_id else None,
            admin_verified=True
        )
        
        db.session.add(doctor)
        db.session.commit()
        
        flash(f'Doctor {name} added', 'success')
        return redirect(url_for('admin.doctors'))
    
    departments = Department.query.all()
    return render_template('admin/add_doctor.html', departments=departments)


@admin_bp.route('/doctors/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_doctor(id):
    doctor = User.query.get_or_404(id)
    
    if doctor.acc_type != 'doctor':
        flash('Invalid doctor', 'danger')
        return redirect(url_for('admin.doctors'))
    
    if request.method == 'POST':
        doctor.name = request.form.get('name')
        doctor.contact_num = request.form.get('contact')
        doctor.user_addr = request.form.get('address')
        dept_id = request.form.get('department_id')
        doctor.department_id = dept_id if dept_id else None
        
        db.session.commit()
        flash(f'Updated {doctor.name}', 'success')
        return redirect(url_for('admin.doctors'))
    
    departments = Department.query.all()
    return render_template('admin/edit_doctor.html', doctor=doctor, 
                         departments=departments)


@admin_bp.route('/doctors/delete/<int:id>', methods=['POST'])
@login_required
@role_required('admin')
def delete_doctor(id):
    from models import Appointment, DoctorAvailability, Treatment
    
    doctor = User.query.get_or_404(id)
    
    if doctor.acc_type != 'doctor':
        flash('Invalid doctor', 'danger')
        return redirect(url_for('admin.doctors'))
    
    name = doctor.name
    
    # Delete all associated data in correct order
    # 1. Delete treatments (appointment.treatments is a list)
    appointments = Appointment.query.filter_by(doctor_id=id).all()
    for appt in appointments:
        for treatment in appt.treatments:
            db.session.delete(treatment)
    
    # 2. Delete appointments
    Appointment.query.filter_by(doctor_id=id).delete()
    
    # 3. Delete doctor availability
    DoctorAvailability.query.filter_by(doctor_id=id).delete()
    
    # 4. Finally delete the doctor
    db.session.delete(doctor)
    db.session.commit()
    
    flash(f'Dr. {name} and all associated records removed', 'success')
    return redirect(url_for('admin.doctors'))


@admin_bp.route('/patients')
@login_required
@role_required('admin')
def patients():
    search = request.args.get('search', '')
    
    if search:
        patients = User.query.filter(
            User.acc_type == 'patient',
            (User.name.contains(search)) | 
            (User.id == search if search.isdigit() else False) |
            (User.contact_num.contains(search))
        ).all()
    else:
        patients = User.query.filter_by(acc_type='patient').all()
    
    return render_template('admin/patients.html', patients=patients, search=search)


@admin_bp.route('/patients/delete/<int:id>', methods=['POST'])
@login_required
@role_required('admin')
def delete_patient(id):
    from models import Appointment, Treatment
    
    patient = User.query.get_or_404(id)
    
    if patient.acc_type != 'patient':
        flash('Invalid patient', 'danger')
        return redirect(url_for('admin.patients'))
    
    name = patient.name
    
    # Delete all associated data in correct order
    # 1. Delete treatments (appointment.treatments is a list)
    appointments = Appointment.query.filter_by(patient_id=id).all()
    for appt in appointments:
        for treatment in appt.treatments:
            db.session.delete(treatment)
    
    # 2. Delete appointments
    Appointment.query.filter_by(patient_id=id).delete()
    
    # 3. Finally delete the patient
    db.session.delete(patient)
    db.session.commit()
    
    flash(f'{name} and all associated records removed', 'success')
    return redirect(url_for('admin.patients'))


@admin_bp.route('/appointments')
@login_required
@role_required('admin')
def appointments():
    appts = Appointment.query.order_by(Appointment.date.desc()).all()
    return render_template('admin/appointments.html', appointments=appts)


@admin_bp.route('/doctor/<int:id>/availability')
@login_required
@role_required('admin')
def doctor_availability(id):
    from models import DoctorAvailability
    from datetime import date, timedelta
    
    doctor = User.query.filter_by(id=id, acc_type='doctor').first_or_404()
    
    today = date.today()
    next_7_days = [today + timedelta(days=i) for i in range(7)]
    
    availability_data = {}
    for day in next_7_days:
        avail = DoctorAvailability.query.filter_by(
            doctor_id=id,
            date=day
        ).all()
        availability_data[day] = avail
    
    return render_template('admin/doctor_availability.html',
                         doctor=doctor,
                         next_7_days=next_7_days,
                         availability_data=availability_data)


@admin_bp.route('/doctor/<int:id>/availability/add', methods=['POST'])
@login_required
@role_required('admin')
def add_doctor_availability(id):
    from models import DoctorAvailability
    from datetime import datetime
    
    doctor = User.query.filter_by(id=id, acc_type='doctor').first_or_404()
    
    selected_date = request.form.get('date')
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')
    
    if selected_date and start_time and end_time:
        avail_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
        
        existing = DoctorAvailability.query.filter_by(
            doctor_id=id,
            date=avail_date,
            start_time=start_time
        ).first()
        
        if existing:
            flash('Availability already set for this time', 'warning')
        else:
            availability = DoctorAvailability(
                doctor_id=id,
                date=avail_date,
                start_time=start_time,
                end_time=end_time,
                is_available=True
            )
            db.session.add(availability)
            db.session.commit()
            flash('Availability added', 'success')
    
    return redirect(url_for('admin.doctor_availability', id=id))


@admin_bp.route('/doctor/availability/delete/<int:id>', methods=['POST'])
@login_required
@role_required('admin')
def delete_doctor_availability(id):
    from models import DoctorAvailability
    
    avail = DoctorAvailability.query.get_or_404(id)
    doctor_id = avail.doctor_id
    
    db.session.delete(avail)
    db.session.commit()
    
    flash('Availability removed', 'success')
    return redirect(url_for('admin.doctor_availability', id=doctor_id))
    return redirect(url_for('admin.doctor_availability', id=doctor_id))
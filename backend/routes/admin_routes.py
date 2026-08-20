import os
from flask import Blueprint, request, jsonify
from models import db, User, Appointment, Department, DoctorSchedule
from auth_utils import token_required, require_role
from extensions import cache
from datetime import datetime, date, timedelta

patient_bp = Blueprint('patient', __name__)


# Dashboard

@patient_bp.route('/dashboard', methods=['GET'])
@token_required
@require_role('patient')
def patient_dashboard(caller_id, caller_role):
    today = date.today()

    upcoming = Appointment.query.filter(
        Appointment.patient_id == caller_id,
        Appointment.scheduled_date >= today,
        Appointment.booking_status != 'Cancelled'
    ).order_by(Appointment.scheduled_date.asc()).all()

    past = Appointment.query.filter(
        Appointment.patient_id == caller_id,
        Appointment.scheduled_date <= today
    ).order_by(Appointment.scheduled_date.desc()).limit(5).all()

    departments = _get_cached_departments()

    return jsonify({
        'upcoming_appointments': [a.to_dict() for a in upcoming],
        'past_appointments': [a.to_dict() for a in past],
        'departments': departments
    }), 200


@cache.cached(timeout=300, key_prefix='dept_list')
def _get_cached_departments():
    depts = Department.query.all()
    return [d.to_dict() for d in depts]

# Doctors & Availability

@patient_bp.route('/doctors', methods=['GET'])
@token_required
@require_role('patient')
def browse_doctors(caller_id, caller_role):
    name_kw = request.args.get('name', '').strip()
    dept_id = request.args.get('dept_id', '').strip()

    query = User.query.filter_by(acc_type='doctor', is_verified=True)

    if name_kw:
        query = query.filter(User.full_name.ilike(f'%{name_kw}%'))
    if dept_id:
        query = query.filter_by(dept_id=dept_id)

    doctors = query.all()
    today = date.today()
    week_end = today + timedelta(days=7)

    result = []
    for doc in doctors:
        slots = DoctorSchedule.query.filter(
            DoctorSchedule.doctor_id == doc.id,
            DoctorSchedule.avail_date >= today,
            DoctorSchedule.avail_date <= week_end
        ).all()

        available = []
        for s in slots:
            already_booked = Appointment.query.filter(
                Appointment.doctor_id == doc.id,
                Appointment.scheduled_date == s.avail_date,
                Appointment.scheduled_time == s.slot_start,
                Appointment.booking_status != 'Cancelled'
            ).first()
            if not already_booked:
                available.append(s.to_dict())

        info = doc.basic_info()
        info['available_slots'] = available
        result.append(info)

    return jsonify(result), 200


@patient_bp.route('/doctors/<int:doc_id>/availability', methods=['GET'])
@token_required
@require_role('patient')
def doctor_availability(caller_id, caller_role, doc_id):
    User.query.filter_by(id=doc_id, acc_type='doctor', is_verified=True).first_or_404()
    cache_key = f'doc_availability_{doc_id}'
    cached = cache.get(cache_key)
    if cached:
        return jsonify(cached), 200

    today = date.today()
    slots = DoctorSchedule.query.filter(
        DoctorSchedule.doctor_id == doc_id,
        DoctorSchedule.avail_date >= today,
        DoctorSchedule.avail_date <= today + timedelta(days=7)
    ).all()
    result = [s.to_dict() for s in slots]
    cache.set(cache_key, result, timeout=120)
    return jsonify(result), 200


#Appointments 

@patient_bp.route('/appointments/book', methods=['POST'])
@token_required
@require_role('patient')
def book_appointment(caller_id, caller_role):
    body = request.get_json()

    try:
        appt_date = datetime.strptime(body['scheduled_date'], '%Y-%m-%d').date()
    except (KeyError, ValueError):
        return jsonify({'error': 'scheduled_date must be in YYYY-MM-DD format'}), 400

    doc_id = body.get('doctor_id')
    appt_time = body.get('scheduled_time')

    if not doc_id or not appt_time:
        return jsonify({'error': 'doctor_id and scheduled_time are required'}), 400

    if appt_date < date.today():
        return jsonify({'error': 'Cannot book appointments in the past'}), 400

    clash = Appointment.query.filter(
        Appointment.doctor_id == doc_id,
        Appointment.scheduled_date == appt_date,
        Appointment.scheduled_time == appt_time,
        Appointment.booking_status != 'Cancelled'
    ).first()

    if clash:
        return jsonify({'error': 'That time slot is already taken by another patient'}), 409

    patient_used = Appointment.query.filter(
        Appointment.patient_id == caller_id,
        Appointment.scheduled_date == appt_date,
        Appointment.scheduled_time == appt_time,
        Appointment.booking_status != 'Cancelled'
    ).first()
    
    if patient_used:
        return jsonify({'error':'You have already book in this timing'}), 409
    
    new_appt = Appointment(
        doctor_id=doc_id,
        patient_id=caller_id,
        scheduled_date=appt_date,
        scheduled_time=appt_time,
        booking_status='Booked'
    )
    db.session.add(new_appt)
    db.session.commit()

    return jsonify({
        'message': 'Appointment booked successfully',
        'appointment': new_appt.to_dict()
    }), 201


@patient_bp.route('/appointments/<int:appt_id>/reschedule', methods=['POST'])
@token_required
@require_role('patient')
def reschedule_appointment(caller_id, caller_role, appt_id):
    appt = Appointment.query.filter_by(id=appt_id, patient_id=caller_id).first_or_404()

    if appt.booking_status != 'Booked':
        return jsonify({'error': f'Cannot reschedule — appointment is already {appt.booking_status}'}), 400

    if appt.scheduled_date < date.today():
        return jsonify({'error': 'Cannot reschedule a past appointment'}), 400

    body = request.get_json()
    try:
        new_date = datetime.strptime(body['scheduled_date'], '%Y-%m-%d').date()
    except (KeyError, ValueError):
        return jsonify({'error': 'scheduled_date must be in YYYY-MM-DD format'}), 400

    new_time = body.get('scheduled_time')
    if not new_time:
        return jsonify({'error': 'scheduled_time is required'}), 400

    clash = Appointment.query.filter(
        Appointment.doctor_id == appt.doctor_id,
        Appointment.scheduled_date == new_date,
        Appointment.scheduled_time == new_time,
        Appointment.booking_status != 'Cancelled',
        Appointment.id != appt_id
    ).first()

    if clash:
        return jsonify({'error': 'That time slot is already taken'}), 409

    valid_slot = DoctorSchedule.query.filter(
        DoctorSchedule.doctor_id == appt.doctor_id,
        DoctorSchedule.avail_date == new_date,
        DoctorSchedule.slot_start <= new_time,
        DoctorSchedule.slot_end >= new_time
    ).first()

    if not valid_slot:
        return jsonify({'error': 'The selected time is outside the doctor\'s available hours'}), 400

    appt.scheduled_date = new_date
    appt.scheduled_time = new_time
    db.session.commit()

    return jsonify({'message': 'Appointment rescheduled', 'appointment': appt.to_dict()}), 200


@patient_bp.route('/appointments/<int:appt_id>/cancel', methods=['POST'])
@token_required
@require_role('patient')
def cancel_appointment(caller_id, caller_role, appt_id):
    appt = Appointment.query.filter_by(id=appt_id, patient_id=caller_id).first_or_404()

    if appt.booking_status != 'Booked':
        return jsonify({'error': f'Cannot cancel — appointment is already {appt.booking_status}'}), 400

    appt.booking_status = 'Cancelled'
    db.session.commit()
    return jsonify({'message': 'Appointment cancelled successfully'}), 200


# History 

@patient_bp.route('/history', methods=['GET'])
@token_required
@require_role('patient')
def full_history(caller_id, caller_role):
    records = Appointment.query.filter_by(
        patient_id=caller_id
    ).order_by(Appointment.scheduled_date.desc()).all()

    return jsonify([a.to_dict() for a in records]), 200


# Profile 

@patient_bp.route('/profile', methods=['GET'])
@token_required
@require_role('patient')
def get_profile(caller_id, caller_role):
    me = User.query.get(caller_id)
    return jsonify(me.basic_info()), 200


@patient_bp.route('/profile', methods=['PUT'])
@token_required
@require_role('patient')
def update_profile(caller_id, caller_role):
    me = User.query.get(caller_id)
    body = request.get_json()
    if 'full_name' in body:
        me.full_name = body['full_name']
    if 'contact_num' in body:
        me.contact_num = body['contact_num']
    if 'home_address' in body:
        me.home_address = body['home_address']
    if 'email' in body and body['email']:
        # Check if another user already has this email
        existing = User.query.filter(
            User.email == body['email'],
            User.id != caller_id
        ).first()
        if existing:
            return jsonify({'error': 'This email is already linked to another account'}), 400
        me.email = body['email']
    db.session.commit()
    return jsonify({'message': 'Profile updated', 'profile': me.basic_info()}), 200

@patient_bp.route('/export/status/<task_id>', methods=['GET'])
@token_required
@require_role('patient')
def export_status(caller_id, caller_role, task_id):
    from app import celery
    result = celery.AsyncResult(task_id)
    return jsonify({
        'status': result.status,
        'ready': result.ready(),
        'successful': result.successful()
    }), 200

@patient_bp.route('/download-csv', methods=['GET'])
@token_required
@require_role('patient')
def download_csv(caller_id, caller_role):
    from flask import send_file
    me = User.query.get(caller_id)
    filename = f"exports/history_{me.username}.csv"
    if not os.path.exists(filename):
        return jsonify({'error': 'No export found. Please export first.'}), 404
    return send_file(
        os.path.abspath(filename),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f"history_{me.username}.csv"
    )
# CSV Export

@patient_bp.route('/export', methods=['POST'])
@token_required
@require_role('patient')
def trigger_csv_export(caller_id, caller_role):
    from app import celery
    task = celery.send_task('tasks.export_patient_csv', args=[caller_id])
    return jsonify({
        'message': 'Export queued',
        'task_id': task.id
    }), 202

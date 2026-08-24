from flask import Blueprint, request, jsonify
from models import db, User, Appointment, TreatmentRecord, DoctorSchedule
from auth_utils import token_required, require_role
from datetime import datetime, date, timedelta
from extensions import cache

doctor_bp = Blueprint('doctor', __name__)


# Dashboard 
@doctor_bp.route('/dashboard', methods=['GET'])
@token_required
@require_role('doctor')
def doctor_dashboard(caller_id, caller_role):
    me = User.query.get(caller_id)
    today = date.today()
    week_ahead = today + timedelta(days=7)

    todays_count = Appointment.query.filter_by(
        doctor_id=caller_id, scheduled_date=today
    ).count()

    week_count = Appointment.query.filter(
        Appointment.doctor_id == caller_id,
        Appointment.scheduled_date >= today,
        Appointment.scheduled_date <= week_ahead
    ).count()

    todays_appts = Appointment.query.filter_by(
        doctor_id=caller_id, scheduled_date=today
    ).order_by(Appointment.scheduled_time).all()

    return jsonify({
        'welcome': f'Welcome back, Dr. {me.full_name}',
        'todays_count': todays_count,
        'week_count': week_count,
        'todays_appointments': [a.to_dict() for a in todays_appts]
    }), 200


# Appointments 

@doctor_bp.route('/appointments', methods=['GET'])
@token_required
@require_role('doctor')
def fetch_appointments(caller_id, caller_role):
    view = request.args.get('view', 'all')  
    query = Appointment.query.filter_by(doctor_id=caller_id)
    today = date.today()

    if view == 'today':
        query = query.filter_by(scheduled_date=today)
    elif view == 'week':
        query = query.filter(
            Appointment.scheduled_date >= today,
            Appointment.scheduled_date <= today + timedelta(days=7)
        )

    appts = query.order_by(Appointment.scheduled_date.asc(), Appointment.scheduled_time.asc()).all()
    return jsonify([a.to_dict() for a in appts]), 200


@doctor_bp.route('/appointments/<int:appt_id>/complete', methods=['POST'])
@token_required
@require_role('doctor')
def mark_completed(caller_id, caller_role, appt_id):
    appt = Appointment.query.filter_by(id=appt_id, doctor_id=caller_id).first_or_404()

    if appt.booking_status == 'Cancelled':
        return jsonify({'error': 'Cannot complete a cancelled appointment'}), 400

    body = request.get_json()
    if not body.get('diagnosis_text') or not body.get('prescription_text'):
        return jsonify({'error': 'Diagnosis and prescription are required to complete an appointment'}), 400

    appt.booking_status = 'Completed'

    # update or create treatment record
    if appt.visit_record:
        appt.visit_record.diagnosis_text = body['diagnosis_text']
        appt.visit_record.prescription_text = body['prescription_text']
        appt.visit_record.follow_up_notes = body.get('follow_up_notes', '')
        appt.visit_record.next_visit_date = body.get('next_visit_date', '')
    else:
        record = TreatmentRecord(
            appointment_id=appt_id,
            diagnosis_text=body['diagnosis_text'],
            prescription_text=body['prescription_text'],
            follow_up_notes=body.get('follow_up_notes', ''),
            next_visit_date=body.get('next_visit_date', '')
        )
        db.session.add(record)

    db.session.commit()

    # send email if next visit date is provided
    if body.get('next_visit_date') and appt.visiting_patient.email:
        from tasks import send_email
        patient = appt.visiting_patient
        doctor = appt.attending_doctor
        send_email(
            patient.email,
            'Your Next Visit Reminder — Nivea Health Care',
            f"""
            <html><body>
            <h2>Next Visit Scheduled</h2>
            <p>Dear <b>{patient.full_name}</b>,</p>
            <p>Your appointment with <b>Dr. {doctor.full_name}</b> has been completed.</p>
            <p>Your next visit has been scheduled for: <b>{body.get('next_visit_date')}</b></p>
            <p>Please book your appointment for that date in advance.</p>
            <p>— Nivea Health Care Team</p>
            </body></html>
            """
        )

    return jsonify({'message': 'Appointment marked as completed with treatment details saved'}), 200


@doctor_bp.route('/appointments/<int:appt_id>/cancel', methods=['POST'])
@token_required
@require_role('doctor')
def cancel_appointment(caller_id, caller_role, appt_id):
    appt = Appointment.query.filter_by(id=appt_id, doctor_id=caller_id).first_or_404()

    if appt.booking_status != 'Booked':
        return jsonify({'error': f'Cannot cancel an appointment that is already {appt.booking_status}'}), 400

    appt.booking_status = 'Cancelled'
    db.session.commit()
    return jsonify({'message': 'Appointment has been cancelled'}), 200


# Patient History
@doctor_bp.route('/patients', methods=['GET'])
@token_required
@require_role('doctor')
def my_patients(caller_id, caller_role):
    all_appts = Appointment.query.filter_by(doctor_id=caller_id).all()
    seen_ids = set()
    patient_list = []
    for a in all_appts:
        if a.patient_id not in seen_ids:
            seen_ids.add(a.patient_id)
            patient_list.append(a.visiting_patient.basic_info())
    return jsonify(patient_list), 200


@doctor_bp.route('/patients/<int:pat_id>/history', methods=['GET'])
@token_required
@require_role('doctor')
def patient_full_history(caller_id, caller_role, pat_id):
    patient = User.query.filter_by(id=pat_id, acc_type='patient').first_or_404()

    all_records = Appointment.query.filter_by(
        patient_id=pat_id
    ).order_by(Appointment.scheduled_date.desc()).all()

    return jsonify({
        'patient': patient.basic_info(),
        'history': [a.to_dict() for a in all_records]
    }), 200


# Schedule
@doctor_bp.route('/schedule', methods=['GET'])
@token_required
@require_role('doctor')
def view_my_schedule(caller_id, caller_role):
    slots = DoctorSchedule.query.filter_by(doctor_id=caller_id).all()
    return jsonify([s.to_dict() for s in slots]), 200


@doctor_bp.route('/schedule', methods=['POST'])
@token_required
@require_role('doctor')
def add_schedule_slot(caller_id, caller_role):
    body = request.get_json()
    try:
        parsed_date = datetime.strptime(body['avail_date'], '%Y-%m-%d').date()
    except (KeyError, ValueError):
        return jsonify({'error': 'avail_date must be in YYYY-MM-DD format'}), 400

    # allow availability within the next 7 days
    today = date.today()
    if parsed_date < today or parsed_date > today + timedelta(days=7):
        return jsonify({'error': 'You can only set availability for the next 7 days'}), 400
    
    new_start = body.get('slot_start')
    new_end = body.get('slot_end')
    existing_slots = DoctorSchedule.query.filter_by(
        doctor_id=caller_id,
        avail_date=parsed_date
    ).all()

    # check any time overlaps
    for existing in existing_slots:
        if new_start < existing.slot_end and new_end > existing.slot_start:
            return jsonify({
                'error': f'This slot overlaps with an existing slot ({existing.slot_start} – {existing.slot_end})'
            }), 409

    slot = DoctorSchedule(
        doctor_id=caller_id,
        avail_date=parsed_date,
        slot_start=body.get('slot_start'),
        slot_end=body.get('slot_end')
    )
    db.session.add(slot)
    db.session.commit()
    cache.delete(f'doc_availability_{caller_id}')
    return jsonify({'message': 'Availability slot added', 'slot': slot.to_dict()}), 201


@doctor_bp.route('/schedule/<int:slot_id>', methods=['DELETE'])
@token_required
@require_role('doctor')
def remove_my_slot(caller_id, caller_role, slot_id):
    slot = DoctorSchedule.query.filter_by(id=slot_id, doctor_id=caller_id).first_or_404()
    db.session.delete(slot)
    db.session.commit()
    cache.delete(f'doc_availability_{slot.doctor_id}')
    return jsonify({'message': 'Availability slot removed'}), 200

@doctor_bp.route('/appointments/<int:appt_id>/reschedule', methods=['POST'])
@token_required
@require_role('doctor')
def reschedule_appointment(caller_id, caller_role, appt_id):
    appt = Appointment.query.filter_by(id=appt_id, doctor_id=caller_id).first_or_404()

    if appt.booking_status != 'Booked':
        return jsonify({'error': f'Cannot reschedule — appointment is already {appt.booking_status}'}), 400

    body = request.get_json()
    try:
        new_date = datetime.strptime(body['scheduled_date'], '%Y-%m-%d').date()
    except (KeyError, ValueError):
        return jsonify({'error': 'scheduled_date must be in YYYY-MM-DD format'}), 400

    new_time = body.get('scheduled_time')
    if not new_time:
        return jsonify({'error': 'scheduled_time is required'}), 400

    clash = Appointment.query.filter(
        Appointment.doctor_id == caller_id,
        Appointment.scheduled_date == new_date,
        Appointment.scheduled_time == new_time,
        Appointment.booking_status != 'Cancelled',
        Appointment.id != appt_id
    ).first()

    if clash:
        return jsonify({'error': 'That time slot is already booked'}), 409

    appt.scheduled_date = new_date
    appt.scheduled_time = new_time
    db.session.commit()
    return jsonify({'message': 'Appointment rescheduled', 'appointment': appt.to_dict()}), 200


# Profile
@doctor_bp.route('/profile', methods=['GET'])
@token_required
@require_role('doctor')
def get_profile(caller_id, caller_role):
    me = User.query.get(caller_id)
    return jsonify(me.basic_info()), 200


@doctor_bp.route('/profile', methods=['PUT'])
@token_required
@require_role('doctor')
def update_profile(caller_id, caller_role):
    me = User.query.get(caller_id)
    body = request.get_json()
    if 'contact_num' in body:
        me.contact_num = body['contact_num']
    if 'home_address' in body:
        me.home_address = body['home_address']
    if 'email' in body and body['email']:
        me.email = body['email']
    if 'bio' in body:
        me.bio = body['bio']
    db.session.commit()
    db.session.commit()
    return jsonify({'message': 'Profile updated', 'profile': me.basic_info()}), 200

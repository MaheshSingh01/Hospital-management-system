from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Department(db.Model):
    __tablename__ = 'department'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(300))

    enrolled_doctors = db.relationship('User', backref='department', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'doctor_count': len(self.enrolled_doctors)
        }


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    acc_type = db.Column(db.String(20), nullable=False)  
    full_name = db.Column(db.String(100), nullable=False)
    contact_num = db.Column(db.String(15))
    email = db.Column(db.String(120))
    home_address = db.Column(db.String(300))
    dept_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=True)
    is_verified = db.Column(db.Boolean, default=False)
    bio = db.Column(db.Text, default='')    
    appts_as_doctor = db.relationship(
        'Appointment', foreign_keys='Appointment.doctor_id',
        backref='attending_doctor', lazy=True, cascade='all, delete-orphan'
    )
    appts_as_patient = db.relationship(
        'Appointment', foreign_keys='Appointment.patient_id',
        backref='visiting_patient', lazy=True, cascade='all, delete-orphan'
    )
    schedule_slots = db.relationship(
        'DoctorSchedule', backref='assigned_doctor',
        lazy=True, cascade='all, delete-orphan'
    )

    @property
    def display_id(self):
        prefix_map = {'admin': 'ADM', 'doctor': 'DR', 'patient': 'PT'}
        prefix = prefix_map.get(self.acc_type, 'USR')
        return f'{prefix}{self.id:04d}'

    def basic_info(self):
        return {
            'id': self.id,
            'display_id': self.display_id,
            'username': self.username,
            'full_name': self.full_name,
            'contact_num': self.contact_num,
            'email': self.email,
            'home_address': self.home_address,
            'acc_type': self.acc_type,
            'is_verified': self.is_verified,
            'department': self.department.name if self.department else None,
            'dept_id': self.dept_id,
            'bio': self.bio or ''
        }


class Appointment(db.Model):
    __tablename__ = 'appointment'

    id = db.Column(db.Integer, primary_key=True)
    @property
    def display_id(self):
        return f'APT{self.id:04d}'
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    scheduled_date = db.Column(db.Date, nullable=False)
    scheduled_time = db.Column(db.String(10), nullable=False)
    booking_status = db.Column(db.String(20), default='Booked') 

    visit_record = db.relationship(
        'TreatmentRecord', backref='linked_appointment',
        uselist=False, cascade='all, delete-orphan'
    )

    def to_dict(self):
        doc = self.attending_doctor
        pat = self.visiting_patient
        rec = self.visit_record
        return {
            'id': self.id,
            'display_id': self.display_id,
            'doctor_id': self.doctor_id,
            'doctor_name': doc.full_name if doc else None,
            'doctor_dept': doc.department.name if doc and doc.department else None,
            'patient_id': self.patient_id,
            'patient_name': pat.full_name if pat else None,
            'scheduled_date': str(self.scheduled_date),
            'scheduled_time': self.scheduled_time,
            'booking_status': self.booking_status,
            'has_treatment': rec is not None,
            'treatment': rec.to_dict() if rec else None
        }


class TreatmentRecord(db.Model):
    __tablename__ = 'treatment_record'

    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'), nullable=False)
    diagnosis_text = db.Column(db.Text, nullable=False)
    prescription_text = db.Column(db.Text, nullable=False)
    follow_up_notes = db.Column(db.Text)
    next_visit_date = db.Column(db.String(30))

    def to_dict(self):
        return {
            'id': self.id,
            'appointment_id': self.appointment_id,
            'diagnosis_text': self.diagnosis_text,
            'prescription_text': self.prescription_text,
            'follow_up_notes': self.follow_up_notes,
            'next_visit_date': self.next_visit_date
        }


class DoctorSchedule(db.Model):
    __tablename__ = 'doctor_schedule'

    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    avail_date = db.Column(db.Date, nullable=False)
    slot_start = db.Column(db.String(10), nullable=False)
    slot_end = db.Column(db.String(10), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'doctor_id': self.doctor_id,
            'avail_date': str(self.avail_date),
            'slot_start': self.slot_start,
            'slot_end': self.slot_end
        }

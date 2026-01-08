from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    acc_type = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    user_addr = db.Column(db.String(200))
    contact_num = db.Column(db.String(15))
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    admin_verified = db.Column(db.Boolean, default=False)
    
    doctor_appointments = db.relationship('Appointment', foreign_keys='Appointment.doctor_id', backref='doctor')
    patient_appointments = db.relationship('Appointment', foreign_keys='Appointment.patient_id', backref='patient')
    availability = db.relationship('DoctorAvailability', backref='doctor', cascade='all, delete-orphan')
    
    @property
    def display_id(self):
        """Generate  ID based on account type"""
        if self.acc_type == 'doctor':
            return f'DR{self.id:03d}'  
        elif self.acc_type == 'patient':
            return f'P{self.id:03d}'   
        elif self.acc_type == 'admin':
            return f'ADM{self.id:03d}' 
        return str(self.id)


class Department(db.Model):
    __tablename__ = 'department'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    
    doctors = db.relationship('User', backref='department')


class Appointment(db.Model):
    __tablename__ = 'appointment'
    
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    appt_time = db.Column(db.String(10), nullable=False)
    curr_status = db.Column(db.String(20), default='Booked')
    
    treatments = db.relationship('Treatment', backref='appointment', cascade='all, delete-orphan')
    
    @property
    def display_id(self):
        """Generate appointment ID"""
        return f'APP{self.id:04d}'


class Treatment(db.Model):
    __tablename__ = 'treatment'
    
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'), nullable=False)
    diagnosis = db.Column(db.Text)
    prescription = db.Column(db.Text)
    medical_notes = db.Column(db.Text)


class DoctorAvailability(db.Model):
    __tablename__ = 'doctor_availability'
    
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.String(10), nullable=False)
    end_time = db.Column(db.String(10), nullable=False)
    is_available = db.Column(db.Boolean, default=True)
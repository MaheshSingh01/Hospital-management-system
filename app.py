from flask import Flask
from config import Config
from models import db
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.doctor import doctor_bp
from routes.patient import patient_bp

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(doctor_bp, url_prefix='/doctor')
app.register_blueprint(patient_bp, url_prefix='/patient')


def init_db():
    with app.app_context():
        db.create_all()
        
        from models import User, Department
        
        admin = User.query.filter_by(acc_type='admin').first()
        if not admin:
            admin = User(
                username='admin',
                password='admin123',
                acc_type='admin',
                name='Admin',
                admin_verified=True
            )
            db.session.add(admin)
            db.session.commit()
        
        if Department.query.count() == 0:
            depts = [
                Department(name='Cardiology', description='Heart care'),
                Department(name='Neurology', description='Brain and nerves'),
                Department(name='Orthopedics', description='Bones and joints'),
                Department(name='Pediatrics', description='Child care'),
                Department(name='General Medicine', description='General health')
            ]
            db.session.add_all(depts)
            db.session.commit()


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
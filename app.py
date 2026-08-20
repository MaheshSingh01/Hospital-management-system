from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from models import db, User, Department
from extensions import cache
from tasks import build_celery

from routes.auth_routes import auth_bp
from routes.admin_routes import admin_bp
from routes.doctor_routes import doctor_bp
from routes.patient_routes import patient_bp

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
cache.init_app(app)
CORS(app, resources={r"/api/*": {"origins": "*"}})
celery = build_celery(app)


app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(doctor_bp, url_prefix='/api/doctor')
app.register_blueprint(patient_bp, url_prefix='/api/patient')

@app.route('/api/health')
def health_check():
    return jsonify({'status': 'HMS API is running'}), 200

def init_db():
    with app.app_context():
        db.create_all()

        if not User.query.filter_by(acc_type='admin').first():
            db.session.add(User(
                username='admin',
                password='admin123',
                acc_type='admin',
                full_name='Hospital Admin',
                is_verified=True
            ))
        
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
    

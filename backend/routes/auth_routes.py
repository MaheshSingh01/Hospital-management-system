from flask import Blueprint, request, jsonify
from models import db, User
from auth_utils import create_jwt

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def patient_register():
    body = request.get_json()

    required = ['username', 'password', 'full_name']
    for field in required:
        if not body.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    already_exists = User.query.filter_by(username=body['username']).first()
    if already_exists:
        return jsonify({'error': 'That username is already taken'}), 409

    if body.get('email'):
        email_taken = User.query.filter_by(email=body['email']).first()
        if email_taken:
            return jsonify({'error': 'That email is already linked to another account'}), 409

    new_patient = User(
        username=body['username'],
        password=body['password'],      
        acc_type='patient',
        full_name=body['full_name'],
        contact_num=body.get('contact_num'),
        home_address=body.get('home_address'),
        email=body.get('email'),
        is_verified=True                
    )
    db.session.add(new_patient)
    db.session.commit()
    return jsonify({'message': 'Registration successful, you can now log in'}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    body = request.get_json()
    username = body.get('username', '').strip()
    password = body.get('password', '')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    matched_user = User.query.filter_by(username=username).first()

    if not matched_user or matched_user.password != password:
        return jsonify({'error': 'Incorrect username or password'}), 401

    if matched_user.acc_type == 'doctor' and not matched_user.is_verified:
        return jsonify({'error': 'Your account is pending admin verification'}), 403

    token = create_jwt(matched_user)
    return jsonify({
        'token': token,
        'role': matched_user.acc_type,
        'full_name': matched_user.full_name,
        'user_id': matched_user.id,
        'display_id': matched_user.display_id
    }), 200

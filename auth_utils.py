import jwt
import datetime
from functools import wraps
from flask import request, jsonify
from config import Config


def create_jwt(user):
    expiry = datetime.datetime.utcnow() + datetime.timedelta(days=1)
    payload = {
        'user_id': user.id,
        'user_role': user.acc_type,
        'exp': expiry
    }
    return jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')


def token_required(fn):
    @wraps(fn)
    def check_token(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authorization token missing'}), 401
        raw_token = auth_header.split(' ')[1]
        try:
            decoded = jwt.decode(raw_token, Config.SECRET_KEY, algorithms=['HS256'])
            caller_id = decoded['user_id']
            caller_role = decoded['user_role']
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Session expired, please login again'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token provided'}), 401
        return fn(caller_id, caller_role, *args, **kwargs)
    return check_token


def require_role(expected_role):
    def outer(fn):
        @wraps(fn)
        def guard(caller_id, caller_role, *args, **kwargs):
            if caller_role != expected_role:
                return jsonify({'error': 'You do not have permission for this action'}), 403
            return fn(caller_id, caller_role, *args, **kwargs)
        return guard
    return outer
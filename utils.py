from flask import session, redirect, url_for, flash
from functools import wraps

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return wrapper


def role_required(role):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please login first', 'danger')
                return redirect(url_for('auth.login'))
            
            if session.get('acc_type') != role:
                flash('Access denied', 'danger')
                return redirect(url_for('auth.login'))
            
            return f(*args, **kwargs)
        return wrapper
    return decorator
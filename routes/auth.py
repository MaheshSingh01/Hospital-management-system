from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/')
def home():
    return render_template('home.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.password == password:
            if user.acc_type == 'doctor' and not user.admin_verified:
                flash('Account pending verification', 'warning')
                return redirect(url_for('auth.login'))
            
            session['user_id'] = user.id
            session['username'] = user.username
            session['acc_type'] = user.acc_type
            session['name'] = user.name
            
            flash(f'Welcome back, {user.name}', 'success')
            
            if user.acc_type == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif user.acc_type == 'doctor':
                return redirect(url_for('doctor.dashboard'))
            else:
                return redirect(url_for('patient.dashboard'))
        else:
            flash('Wrong username or password', 'danger')
    
    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        name = request.form.get('name')
        contact = request.form.get('contact')
        address = request.form.get('address')
        
        if User.query.filter_by(username=username).first():
            flash('Username already taken', 'danger')
            return redirect(url_for('auth.register'))
        
        patient = User(
            username=username,
            password=password,
            acc_type='patient',
            name=name,
            contact_num=contact,
            user_addr=address
        )
        
        db.session.add(patient)
        db.session.commit()
        
        flash('Account created successfully', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('auth.home'))
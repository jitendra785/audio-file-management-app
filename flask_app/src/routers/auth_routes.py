from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from pydantic import ValidationError

from services.auth_service import AuthService
from basemodels.auth import LoginRequest, SignupRequest

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page and handler"""
    if current_user.is_authenticated:
        # Redirect based on user role
        if current_user.role.value == 'ADMIN':
            return redirect(url_for('admin.users'))
        else:
            return redirect(url_for('audio.files'))

    if request.method == 'POST':
        try:
            # Validate request data
            login_data = LoginRequest(
                username=request.form.get('username'),
                password=request.form.get('password')
            )

            # Authenticate user
            user = AuthService.authenticate_user(
                login_data.username,
                login_data.password
            )

            if user:
                login_user(user)
                flash('Login successful!', 'success')

                # Redirect based on role
                if user.role.value == 'ADMIN':
                    return redirect(url_for('admin.users'))
                else:
                    return redirect(url_for('audio.files'))
            else:
                flash('Invalid username or password', 'error')

        except ValidationError as e:
            flash('Invalid input data', 'error')

    return render_template('login.html')


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """Signup page and handler"""
    if current_user.is_authenticated:
        return redirect(url_for('audio.files'))

    if request.method == 'POST':
        try:
            # Validate request data
            signup_data = SignupRequest(
                username=request.form.get('username'),
                email=request.form.get('email'),
                password=request.form.get('password'),
                full_name=request.form.get('full_name')
            )

            # Create user
            result = AuthService.signup_user(signup_data)

            if result['success']:
                flash('Account created successfully! Please login.', 'success')
                return redirect(url_for('auth.login'))
            else:
                flash(result['message'], 'error')

        except ValidationError as e:
            errors = e.errors()
            for error in errors:
                flash(f"{error['loc'][0]}: {error['msg']}", 'error')

    return render_template('signup.html')


@auth_bp.route('/logout')
def logout():
    """Logout handler"""
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from functools import wraps
from pydantic import ValidationError

from services.user_service import UserService
from basemodels.user import UserCreateRequest, UserUpdateRequest

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.role.value != 'ADMIN':
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('audio.files'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/users')
@admin_required
def users():
    """Admin page to view all users"""
    all_users = UserService.get_all_users()
    return render_template('admin_users.html', users=all_users)


@admin_bp.route('/users/create', methods=['POST'])
@admin_required
def create_user():
    """Create a new user (admin only)"""
    try:
        user_data = UserCreateRequest(
            username=request.form.get('username'),
            email=request.form.get('email'),
            password=request.form.get('password'),
            full_name=request.form.get('full_name'),
            role=request.form.get('role', 'USER')
        )

        result = UserService.create_user(user_data)

        if result['success']:
            flash('User created successfully!', 'success')
        else:
            flash(result['message'], 'error')

    except ValidationError as e:
        errors = e.errors()
        for error in errors:
            flash(f"{error['loc'][0]}: {error['msg']}", 'error')

    return redirect(url_for('admin.users'))


@admin_bp.route('/users/<int:user_id>/edit', methods=['POST'])
@admin_required
def edit_user(user_id):
    """Edit an existing user (admin only)"""
    try:
        # Build update data (only include non-empty fields)
        update_data = {}

        if request.form.get('email'):
            update_data['email'] = request.form.get('email')

        if request.form.get('full_name'):
            update_data['full_name'] = request.form.get('full_name')

        if request.form.get('role'):
            update_data['role'] = request.form.get('role')

        if request.form.get('password'):
            update_data['password'] = request.form.get('password')

        user_update = UserUpdateRequest(**update_data)
        result = UserService.update_user(user_id, user_update)

        if result['success']:
            flash('User updated successfully!', 'success')
        else:
            flash(result['message'], 'error')

    except ValidationError as e:
        errors = e.errors()
        for error in errors:
            flash(f"{error['loc'][0]}: {error['msg']}", 'error')

    return redirect(url_for('admin.users'))


@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    """Delete a user (admin only)"""
    # Prevent admin from deleting themselves
    if user_id == current_user.id:
        flash('You cannot delete your own account.', 'error')
        return redirect(url_for('admin.users'))

    result = UserService.delete_user(user_id)

    if result['success']:
        flash('User deleted successfully!', 'success')
    else:
        flash(result['message'], 'error')

    return redirect(url_for('admin.users'))


@admin_bp.route('/users/<int:user_id>/get', methods=['GET'])
@admin_required
def get_user(user_id):
    """Get user details (for editing)"""
    user = UserService.get_user_by_id(user_id)

    if user:
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'full_name': user.full_name,
            'role': user.role.value
        })
    else:
        return jsonify({'error': 'User not found'}), 404

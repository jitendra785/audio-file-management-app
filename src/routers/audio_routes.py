from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, Response
from flask_login import login_required, current_user
from io import BytesIO

from services.audio_service import AudioService

audio_bp = Blueprint('audio', __name__, url_prefix='/audio')


@audio_bp.route('/files')
@login_required
def files():
    """Audio files page - view all user's audio files"""
    user_files = AudioService.get_user_files(current_user.id)
    return render_template('audio_files.html', files=user_files)


@audio_bp.route('/upload', methods=['POST'])
@login_required
def upload():
    """Upload an audio file"""
    if 'file' not in request.files:
        flash('No file provided', 'error')
        return redirect(url_for('audio.files'))

    file = request.files['file']

    result = AudioService.upload_file(file, current_user.id)

    if result['success']:
        flash('File uploaded successfully!', 'success')
    else:
        flash(result['message'], 'error')

    return redirect(url_for('audio.files'))


@audio_bp.route('/files/<int:file_id>/play')
@login_required
def play(file_id):
    """Stream/play an audio file"""
    audio_file = AudioService.get_file_by_id(file_id)

    if not audio_file or audio_file.user_id != current_user.id:
        flash('File not found or access denied', 'error')
        return redirect(url_for('audio.files'))

    # Get file data from GridFS
    file_data = AudioService.get_file_data(audio_file.gridfs_file_id)

    if not file_data:
        flash('File data not found', 'error')
        return redirect(url_for('audio.files'))

    # Return file as streaming response
    return Response(
        BytesIO(file_data),
        mimetype=audio_file.content_type,
        headers={
            'Content-Disposition': f'inline; filename="{audio_file.filename}"'
        }
    )


@audio_bp.route('/files/<int:file_id>/download')
@login_required
def download(file_id):
    """Download an audio file"""
    audio_file = AudioService.get_file_by_id(file_id)

    if not audio_file or audio_file.user_id != current_user.id:
        flash('File not found or access denied', 'error')
        return redirect(url_for('audio.files'))

    # Get file data from GridFS
    file_data = AudioService.get_file_data(audio_file.gridfs_file_id)

    if not file_data:
        flash('File data not found', 'error')
        return redirect(url_for('audio.files'))

    # Return file as download
    return send_file(
        BytesIO(file_data),
        mimetype=audio_file.content_type,
        as_attachment=True,
        download_name=audio_file.filename
    )


@audio_bp.route('/files/<int:file_id>/update', methods=['POST'])
@login_required
def update(file_id):
    """Update/replace an audio file"""
    if 'file' not in request.files:
        flash('No file provided', 'error')
        return redirect(url_for('audio.files'))

    file = request.files['file']

    result = AudioService.update_file(file_id, current_user.id, file)

    if result['success']:
        flash('File updated successfully!', 'success')
    else:
        flash(result['message'], 'error')

    return redirect(url_for('audio.files'))


@audio_bp.route('/files/<int:file_id>/delete', methods=['POST'])
@login_required
def delete(file_id):
    """Delete an audio file"""
    result = AudioService.delete_file(file_id, current_user.id)

    if result['success']:
        flash('File deleted successfully!', 'success')
    else:
        flash(result['message'], 'error')

    return redirect(url_for('audio.files'))

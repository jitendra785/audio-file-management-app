from typing import List, Optional, Dict, Any
from werkzeug.datastructures import FileStorage
from bson import ObjectId
from datetime import datetime
from dbentities.audio_file import AudioFile
from dependencies.database import get_db_session, get_gridfs
from dependencies.constants import allowed_file, MAX_FILE_SIZE_BYTES


class AudioService:
    """Service for audio file management using MongoDB GridFS"""

    @staticmethod
    def upload_file(file: FileStorage, user_id: int) -> Dict[str, Any]:
        """
        Upload an audio file to MongoDB GridFS
        Returns dict with success status and message
        """
        try:
            # Validate file
            if not file or file.filename == '':
                return {
                    'success': False,
                    'message': 'No file provided'
                }

            if not allowed_file(file.filename):
                return {
                    'success': False,
                    'message': 'Invalid file type. Allowed types: mp3, wav, ogg, m4a, flac'
                }

            # Read file data
            file_data = file.read()
            file_size = len(file_data)

            if file_size > MAX_FILE_SIZE_BYTES:
                return {
                    'success': False,
                    'message': f'File too large. Maximum size: {MAX_FILE_SIZE_BYTES / (1024 * 1024)} MB'
                }

            # Store file in GridFS
            gridfs = get_gridfs()
            gridfs_file_id = gridfs.put(
                file_data,
                filename=file.filename,
                content_type=file.content_type or 'audio/mpeg'
            )

            # Create metadata record in PostgreSQL
            db = get_db_session()
            audio_file = AudioFile(
                user_id=user_id,
                filename=file.filename,
                original_filename=file.filename,
                content_type=file.content_type or 'audio/mpeg',
                file_size=file_size,
                gridfs_file_id=str(gridfs_file_id)
            )

            db.add(audio_file)
            db.commit()
            db.refresh(audio_file)

            return {
                'success': True,
                'message': 'File uploaded successfully',
                'file': audio_file
            }

        except Exception as e:
            db = get_db_session()
            db.rollback()
            return {
                'success': False,
                'message': f'An error occurred: {str(e)}'
            }

    @staticmethod
    def get_user_files(user_id: int) -> List[AudioFile]:
        """Get all audio files for a specific user"""
        db = get_db_session()
        return db.query(AudioFile).filter(AudioFile.user_id == user_id).all()

    @staticmethod
    def get_file_by_id(file_id: int) -> Optional[AudioFile]:
        """Get audio file metadata by ID"""
        db = get_db_session()
        return db.query(AudioFile).filter(AudioFile.id == file_id).first()

    @staticmethod
    def get_file_data(gridfs_file_id: str) -> Optional[bytes]:
        """Get actual file data from GridFS"""
        try:
            gridfs = get_gridfs()
            file_data = gridfs.get(ObjectId(gridfs_file_id))
            return file_data.read()
        except Exception:
            return None

    @staticmethod
    def delete_file(file_id: int, user_id: int) -> Dict[str, Any]:
        """
        Delete an audio file (both metadata and GridFS data)
        Returns dict with success status and message
        """
        db = get_db_session()

        try:
            audio_file = db.query(AudioFile).filter(
                AudioFile.id == file_id,
                AudioFile.user_id == user_id
            ).first()

            if not audio_file:
                return {
                    'success': False,
                    'message': 'File not found'
                }

            # Delete from GridFS
            try:
                gridfs = get_gridfs()
                gridfs.delete(ObjectId(audio_file.gridfs_file_id))
            except Exception as e:
                # Log error but continue with metadata deletion
                print(f"Error deleting file from GridFS: {e}")

            # Delete metadata from PostgreSQL
            db.delete(audio_file)
            db.commit()

            return {
                'success': True,
                'message': 'File deleted successfully'
            }

        except Exception as e:
            db.rollback()
            return {
                'success': False,
                'message': f'An error occurred: {str(e)}'
            }

    @staticmethod
    def update_file(file_id: int, user_id: int, new_file: FileStorage) -> Dict[str, Any]:
        """
        Update/replace an audio file
        Returns dict with success status and message
        """
        db = get_db_session()

        try:
            audio_file = db.query(AudioFile).filter(
                AudioFile.id == file_id,
                AudioFile.user_id == user_id
            ).first()

            if not audio_file:
                return {
                    'success': False,
                    'message': 'File not found'
                }

            # Validate new file
            if not new_file or new_file.filename == '':
                return {
                    'success': False,
                    'message': 'No file provided'
                }

            if not allowed_file(new_file.filename):
                return {
                    'success': False,
                    'message': 'Invalid file type'
                }

            # Delete old file from GridFS
            try:
                gridfs = get_gridfs()
                gridfs.delete(ObjectId(audio_file.gridfs_file_id))
            except Exception as e:
                print(f"Error deleting old file from GridFS: {e}")

            # Upload new file to GridFS
            file_data = new_file.read()
            file_size = len(file_data)

            if file_size > MAX_FILE_SIZE_BYTES:
                return {
                    'success': False,
                    'message': 'File too large'
                }

            gridfs_file_id = gridfs.put(
                file_data,
                filename=new_file.filename,
                content_type=new_file.content_type or 'audio/mpeg'
            )

            # Update metadata
            audio_file.filename = new_file.filename
            audio_file.original_filename = new_file.filename
            audio_file.content_type = new_file.content_type or 'audio/mpeg'
            audio_file.file_size = file_size
            audio_file.gridfs_file_id = str(gridfs_file_id)
            audio_file.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(audio_file)

            return {
                'success': True,
                'message': 'File updated successfully',
                'file': audio_file
            }

        except Exception as e:
            db.rollback()
            return {
                'success': False,
                'message': f'An error occurred: {str(e)}'
            }

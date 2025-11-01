from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from dependencies.database import db


class AudioFile(db.Model):
    """Audio file metadata model (actual file stored in MongoDB GridFS)"""
    __tablename__ = 'audio_files'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    content_type = Column(String(100), nullable=False)
    file_size = Column(BigInteger, nullable=False)  # Size in bytes
    gridfs_file_id = Column(String(24), nullable=False, unique=True)  # MongoDB GridFS file ID
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationship to User
    user = relationship('User', backref='audio_files')

    def __repr__(self):
        return f'<AudioFile {self.filename}>'

    def to_dict(self):
        """Convert audio file object to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'content_type': self.content_type,
            'file_size': self.file_size,
            'gridfs_file_id': self.gridfs_file_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

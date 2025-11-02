from pydantic import BaseModel
from datetime import datetime


class AudioFileResponse(BaseModel):
    """Audio file response model"""
    id: int
    user_id: int
    filename: str
    original_filename: str
    content_type: str
    file_size: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

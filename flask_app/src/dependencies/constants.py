"""Application constants"""

from .app_config import get_config

# File upload constants
ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'wav', 'ogg', 'm4a', 'flac'}

# Get max file size from config (convert MB to bytes)
def get_max_file_size() -> int:
    """Get maximum file size in bytes from configuration"""
    config = get_config()
    max_size_mb = config.get('file_upload.max_file_size_mb', 50)
    return max_size_mb * 1024 * 1024

MAX_FILE_SIZE_BYTES = get_max_file_size()


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_AUDIO_EXTENSIONS

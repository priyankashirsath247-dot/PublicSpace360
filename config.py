import os
from dotenv import load_dotenv

# Load .env file if present
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    BASE_DIR = BASE_DIR
    SECRET_KEY = os.environ.get('SECRET_KEY', 'publicspace360-super-secret-key-2026-cep')
    
    # Upload settings
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads', 'reports')
    UPLOAD_SPACES_FOLDER = os.path.join(BASE_DIR, 'uploads', 'spaces')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}

    # Maps API
    GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY', '')

    # MySQL Configuration
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'root')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'publicspace360')
    
    # SQLite Fallback path (enables 100% instant execution if MySQL server is not active)
    SQLITE_DB = os.path.join(BASE_DIR, 'database', 'publicspace360.db')
    
    # Preferred backend ('mysql' or 'sqlite' or 'auto')
    DB_BACKEND = os.environ.get('DB_BACKEND', 'auto')

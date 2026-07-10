import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_secret_key_change_me_in_prod')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt_secret_key_change_me_in_prod')
    
    # Database configuration - SQLite by default for easy local running
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///rent_flatmate.db')
    # If the URL starts with postgres:// (e.g. from Render), convert it to postgresql:// for SQLAlchemy
    if SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT configuration
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Mail configuration (Flask-Mail)
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.mailtrap.io')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 2525))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() in ('true', '1', 'yes')
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'False').lower() in ('true', '1', 'yes')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@rentflatmate.com')
    
    # OpenAI configuration
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    
    # Upload folder
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}

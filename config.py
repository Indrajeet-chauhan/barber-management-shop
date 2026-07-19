# config.py
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Secret key for signing session cookies and protection against CSRF attacks
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-fallback-key-change-in-production'
    
    # Define database location. Default to local SQLite instance.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f"sqlite:///{os.path.join(BASE_DIR, 'database', 'barber.db')}"
    
    # Disable tracking overhead for performance optimization
    SQLALCHEMY_TRACK_MODIFICATIONS = False
# config.py
import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'a3f1c2e8b7a940c395d2d57a47e2facc')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://postgres:1234@localhost:5432/game_store')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'app/static/uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    PERMANENT_SESSION_LIFETIME = timedelta(hours=3)
    OPENROUTER_API_KEY = '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'
    SITE_URL = 'http://localhost:5000'
    SITE_NAME = 'Game Store'
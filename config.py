import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'a3f1c2e8b7a940c395d2d57a47e2facc')  # CSRF және сессиялар үшін құпия кілт
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://postgres:1234@localhost:5432/game_store')  # Дерекқор қосылымы
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # SQLAlchemy ескертулерін өшіру
    UPLOAD_FOLDER = 'app/static/uploads'  # Суреттерді сақтауға арналған папка
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}  # Рұқсат етілген файл кеңейтімдері
    PERMANENT_SESSION_LIFETIME = timedelta(hours=30)  # Сессия мерзімі 30 минут
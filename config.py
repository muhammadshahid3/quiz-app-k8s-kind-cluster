"""
config.py
---------
Central configuration for the Flask app.
Reads values from .env so no secrets are hard-coded.
"""

import os
from dotenv import load_dotenv

load_dotenv()  # load variables from .env into environment


class Config:
    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

    # MySQL connection (PyMySQL driver)
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "quiz_app_db")

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Quiz settings
    QUESTIONS_PER_QUIZ = int(os.getenv("QUESTIONS_PER_QUIZ", 10))
    PASS_PERCENTAGE = float(os.getenv("PASS_PERCENTAGE", 50))
    MAX_QUIZZES_PER_TEACHER = int(os.getenv("MAX_QUIZZES_PER_TEACHER", 10))

    # Session / CSRF
    WTF_CSRF_ENABLED = True
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour

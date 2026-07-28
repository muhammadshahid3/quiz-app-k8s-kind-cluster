"""
models.py
---------
SQLAlchemy ORM models mapping to the MySQL tables:
    users, quizzes, questions, results
"""

from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from database import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(10), nullable=False, default="student")  # 'student' | 'teacher'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    results = db.relationship(
        "Result", backref="user", lazy=True, cascade="all, delete-orphan"
    )
    quizzes = db.relationship(
        "Quiz", backref="teacher", lazy=True, cascade="all, delete-orphan"
    )

    def set_password(self, raw_password: str) -> None:
        """Hash and store the password (never store plain text)."""
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        """Verify a plain-text password against the stored hash."""
        return check_password_hash(self.password, raw_password)

    @property
    def is_teacher(self) -> bool:
        return self.role == "teacher"

    @property
    def is_student(self) -> bool:
        return self.role == "student"

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"


class Quiz(db.Model):
    __tablename__ = "quizzes"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    questions = db.relationship(
        "Question", backref="quiz", lazy=True, cascade="all, delete-orphan"
    )
    results = db.relationship(
        "Result", backref="quiz", lazy=True, cascade="all, delete-orphan"
    )

    @property
    def question_count(self) -> int:
        return len(self.questions)

    def __repr__(self):
        return f"<Quiz {self.title}>"


class Question(db.Model):
    __tablename__ = "questions"

    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quizzes.id"), nullable=False)
    question = db.Column(db.String(500), nullable=False)
    option_a = db.Column(db.String(255), nullable=False)
    option_b = db.Column(db.String(255), nullable=False)
    option_c = db.Column(db.String(255), nullable=False)
    option_d = db.Column(db.String(255), nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)  # 'A' / 'B' / 'C' / 'D'

    def __repr__(self):
        return f"<Question {self.id}>"


class Result(db.Model):
    __tablename__ = "results"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quizzes.id"), nullable=True)
    score = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    percentage = db.Column(db.Float, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Result user={self.user_id} score={self.score}>"

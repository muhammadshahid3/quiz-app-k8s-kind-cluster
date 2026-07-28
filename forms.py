"""
forms.py
--------
Flask-WTF forms. WTForms gives us:
  - Automatic CSRF token handling
  - Server-side input validation
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, RadioField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class SignupForm(FlaskForm):
    fullname = StringField(
        "Full Name", validators=[DataRequired(), Length(min=2, max=150)]
    )
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=150)])
    password = PasswordField(
        "Password", validators=[DataRequired(), Length(min=6, max=100)]
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), EqualTo("password", message="Passwords must match")],
    )
    role = RadioField(
        "I am a",
        choices=[("student", "Student"), ("teacher", "Teacher")],
        default="student",
        validators=[DataRequired()],
    )
    submit = SubmitField("Sign Up")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class QuizForm(FlaskForm):
    title = StringField("Quiz Title", validators=[DataRequired(), Length(min=3, max=150)])
    description = TextAreaField("Description (optional)", validators=[Length(max=500)])
    submit = SubmitField("Save Quiz")


class QuestionForm(FlaskForm):
    question = StringField("Question", validators=[DataRequired(), Length(max=500)])
    option_a = StringField("Option A", validators=[DataRequired(), Length(max=255)])
    option_b = StringField("Option B", validators=[DataRequired(), Length(max=255)])
    option_c = StringField("Option C", validators=[DataRequired(), Length(max=255)])
    option_d = StringField("Option D", validators=[DataRequired(), Length(max=255)])
    correct_answer = SelectField(
        "Correct Answer",
        choices=[("A", "A"), ("B", "B"), ("C", "C"), ("D", "D")],
        validators=[DataRequired()],
    )
    submit = SubmitField("Add Question")

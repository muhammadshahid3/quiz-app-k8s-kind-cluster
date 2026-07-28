"""
routes.py
---------
All application routes, grouped in a single Blueprint ("main").
Using a Blueprint keeps routes decoupled from app.py (MVC-style
"Controller" layer) while still living in one file as requested.
"""

import logging
import random
from datetime import datetime
from functools import wraps

from flask import (
    Blueprint, render_template, redirect, url_for,
    flash, request, session, current_app, abort
)
from flask_login import (
    login_user, logout_user, login_required, current_user
)

from database import db
from models import User, Quiz, Question, Result
from forms import SignupForm, LoginForm, QuizForm, QuestionForm

main_bp = Blueprint("main", __name__)
logger = logging.getLogger("quiz_app")


# ----------------------------------------------------------------------
# Role-based access helper
# ----------------------------------------------------------------------
def teacher_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_teacher:
            flash("This page is only available to teacher accounts.", "warning")
            return redirect(url_for("main.dashboard"))
        return view_func(*args, **kwargs)
    return wrapped


def student_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_student:
            flash("This page is only available to student accounts.", "warning")
            return redirect(url_for("main.teacher_dashboard"))
        return view_func(*args, **kwargs)
    return wrapped


# ----------------------------------------------------------------------
# Landing page
# ----------------------------------------------------------------------
@main_bp.route("/")
def index():
    return render_template("index.html")


# ----------------------------------------------------------------------
# Signup (role-aware: ?role=teacher pre-selects the Teacher option)
# ----------------------------------------------------------------------
@main_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard") if current_user.is_student else url_for("main.teacher_dashboard"))

    form = SignupForm()
    requested_role = request.args.get("role", "student")
    if requested_role not in ("student", "teacher"):
        requested_role = "student"
    if request.method == "GET":
        form.role.data = requested_role

    if form.validate_on_submit():
        try:
            existing_user = User.query.filter_by(email=form.email.data.lower()).first()
            if existing_user:
                flash("An account with this email already exists. Please log in.", "danger")
                return redirect(url_for("main.signup"))

            new_user = User(
                fullname=form.fullname.data.strip(),
                email=form.email.data.lower().strip(),
                role=form.role.data,
            )
            new_user.set_password(form.password.data)

            db.session.add(new_user)
            db.session.commit()

            logger.info(f"New user registered: {new_user.email} ({new_user.role})")
            flash("Account created successfully! Please log in.", "success")
            return redirect(url_for("main.login"))

        except Exception as exc:
            db.session.rollback()
            logger.error(f"Signup error: {exc}")
            flash("Something went wrong while creating your account. Please try again.", "danger")

    return render_template("signup.html", form=form)


# ----------------------------------------------------------------------
# Login
# ----------------------------------------------------------------------
@main_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard") if current_user.is_student else url_for("main.teacher_dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()

        if user and user.check_password(form.password.data):
            login_user(user)
            logger.info(f"User logged in: {user.email} ({user.role})")
            flash(f"Welcome back, {user.fullname}!", "success")
            next_page = request.args.get("next")
            if next_page:
                return redirect(next_page)
            return redirect(url_for("main.dashboard") if user.is_student else url_for("main.teacher_dashboard"))

        flash("Invalid email or password.", "danger")

    return render_template("login.html", form=form)


# ----------------------------------------------------------------------
# Logout
# ----------------------------------------------------------------------
@main_bp.route("/logout")
@login_required
def logout():
    logger.info(f"User logged out: {current_user.email}")
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.index"))


# ----------------------------------------------------------------------
# Student Dashboard - browse quizzes + recent attempts
# ----------------------------------------------------------------------
@main_bp.route("/dashboard")
@login_required
@student_required
def dashboard():
    available_quizzes = (
        Quiz.query.order_by(Quiz.created_at.desc()).all()
    )
    available_quizzes = [q for q in available_quizzes if q.question_count > 0]

    recent_results = (
        Result.query.filter_by(user_id=current_user.id)
        .order_by(Result.submitted_at.desc())
        .limit(5)
        .all()
    )
    return render_template("dashboard.html", results=recent_results, quizzes=available_quizzes)


# ----------------------------------------------------------------------
# Teacher Dashboard - manage quizzes (max MAX_QUIZZES_PER_TEACHER)
# ----------------------------------------------------------------------
@main_bp.route("/teacher/dashboard")
@login_required
@teacher_required
def teacher_dashboard():
    my_quizzes = (
        Quiz.query.filter_by(teacher_id=current_user.id)
        .order_by(Quiz.created_at.desc())
        .all()
    )
    max_quizzes = current_app.config["MAX_QUIZZES_PER_TEACHER"]
    return render_template(
        "teacher_dashboard.html",
        quizzes=my_quizzes,
        max_quizzes=max_quizzes,
        quiz_count=len(my_quizzes),
    )


# ----------------------------------------------------------------------
# Teacher - create a new quiz (blocked once the teacher has 10)
# ----------------------------------------------------------------------
@main_bp.route("/teacher/quiz/new", methods=["GET", "POST"])
@login_required
@teacher_required
def create_quiz():
    max_quizzes = current_app.config["MAX_QUIZZES_PER_TEACHER"]
    existing_count = Quiz.query.filter_by(teacher_id=current_user.id).count()

    if existing_count >= max_quizzes:
        flash(f"You've reached the maximum of {max_quizzes} quizzes. Delete one to add another.", "warning")
        return redirect(url_for("main.teacher_dashboard"))

    form = QuizForm()
    if form.validate_on_submit():
        try:
            # Re-check at submit time to prevent race conditions
            if Quiz.query.filter_by(teacher_id=current_user.id).count() >= max_quizzes:
                flash(f"You've reached the maximum of {max_quizzes} quizzes.", "warning")
                return redirect(url_for("main.teacher_dashboard"))

            new_quiz = Quiz(
                title=form.title.data.strip(),
                description=(form.description.data or "").strip(),
                teacher_id=current_user.id,
            )
            db.session.add(new_quiz)
            db.session.commit()
            logger.info(f"Quiz created: {new_quiz.title} by {current_user.email}")
            flash("Quiz created! Now add some questions to it.", "success")
            return redirect(url_for("main.manage_quiz", quiz_id=new_quiz.id))
        except Exception as exc:
            db.session.rollback()
            logger.error(f"Create quiz error: {exc}")
            flash("Something went wrong while creating the quiz.", "danger")

    return render_template("create_quiz.html", form=form, existing_count=existing_count, max_quizzes=max_quizzes)


# ----------------------------------------------------------------------
# Teacher - manage a quiz: add / view / delete questions
# ----------------------------------------------------------------------
@main_bp.route("/teacher/quiz/<int:quiz_id>", methods=["GET", "POST"])
@login_required
@teacher_required
def manage_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    if quiz.teacher_id != current_user.id:
        abort(403)

    form = QuestionForm()
    if form.validate_on_submit():
        try:
            new_question = Question(
                quiz_id=quiz.id,
                question=form.question.data.strip(),
                option_a=form.option_a.data.strip(),
                option_b=form.option_b.data.strip(),
                option_c=form.option_c.data.strip(),
                option_d=form.option_d.data.strip(),
                correct_answer=form.correct_answer.data,
            )
            db.session.add(new_question)
            db.session.commit()
            flash("Question added.", "success")
            return redirect(url_for("main.manage_quiz", quiz_id=quiz.id))
        except Exception as exc:
            db.session.rollback()
            logger.error(f"Add question error: {exc}")
            flash("Something went wrong while adding the question.", "danger")

    questions = Question.query.filter_by(quiz_id=quiz.id).order_by(Question.id).all()
    return render_template("manage_quiz.html", quiz=quiz, form=form, questions=questions)


# ----------------------------------------------------------------------
# Teacher - delete a question
# ----------------------------------------------------------------------
@main_bp.route("/teacher/quiz/<int:quiz_id>/question/<int:question_id>/delete", methods=["POST"])
@login_required
@teacher_required
def delete_question(quiz_id, question_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    if quiz.teacher_id != current_user.id:
        abort(403)

    question = Question.query.get_or_404(question_id)
    if question.quiz_id != quiz.id:
        abort(404)

    db.session.delete(question)
    db.session.commit()
    flash("Question removed.", "info")
    return redirect(url_for("main.manage_quiz", quiz_id=quiz.id))


# ----------------------------------------------------------------------
# Teacher - delete an entire quiz
# ----------------------------------------------------------------------
@main_bp.route("/teacher/quiz/<int:quiz_id>/delete", methods=["POST"])
@login_required
@teacher_required
def delete_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    if quiz.teacher_id != current_user.id:
        abort(403)

    db.session.delete(quiz)
    db.session.commit()
    logger.info(f"Quiz deleted: {quiz.title} by {current_user.email}")
    flash("Quiz deleted.", "info")
    return redirect(url_for("main.teacher_dashboard"))


# ----------------------------------------------------------------------
# Quiz - student starts a quiz created by a teacher
# ----------------------------------------------------------------------
@main_bp.route("/quiz/<int:quiz_id>", methods=["GET"])
@login_required
@student_required
def quiz(quiz_id):
    quiz_obj = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_obj.id).all()

    if not questions:
        flash("This quiz has no questions yet. Please try another one.", "warning")
        return redirect(url_for("main.dashboard"))

    random.shuffle(questions)

    # Store the chosen question ids + quiz id in the session so submit_quiz
    # grades exactly what was shown (prevents tampering with the form).
    session["quiz_id"] = quiz_obj.id
    session["quiz_question_ids"] = [q.id for q in questions]

    return render_template("quiz.html", questions=questions, quiz=quiz_obj)


# ----------------------------------------------------------------------
# Quiz - submit answers
# ----------------------------------------------------------------------
@main_bp.route("/submit_quiz", methods=["POST"])
@login_required
@student_required
def submit_quiz():
    question_ids = session.get("quiz_question_ids")
    quiz_id = session.get("quiz_id")
    if not question_ids or not quiz_id:
        flash("Your quiz session expired. Please start again.", "warning")
        return redirect(url_for("main.dashboard"))

    try:
        quiz_obj = Quiz.query.get_or_404(quiz_id)
        questions = Question.query.filter(Question.id.in_(question_ids)).all()
        questions_by_id = {q.id: q for q in questions}

        correct_count = 0
        total = len(question_ids)
        answer_breakdown = []

        for qid in question_ids:
            question = questions_by_id.get(qid)
            submitted_answer = request.form.get(f"question_{qid}", "").upper()
            is_correct = submitted_answer == question.correct_answer
            if is_correct:
                correct_count += 1

            answer_breakdown.append({
                "question": question.question,
                "your_answer": submitted_answer or "Not answered",
                "correct_answer": question.correct_answer,
                "is_correct": is_correct,
            })

        wrong_count = total - correct_count
        percentage = round((correct_count / total) * 100, 2) if total else 0
        passed = percentage >= current_app.config["PASS_PERCENTAGE"]

        result = Result(
            user_id=current_user.id,
            quiz_id=quiz_obj.id,
            score=correct_count,
            total_questions=total,
            percentage=percentage,
        )
        db.session.add(result)
        db.session.commit()

        session.pop("quiz_question_ids", None)
        session.pop("quiz_id", None)
        logger.info(f"Quiz submitted by {current_user.email}: {correct_count}/{total}")

        return render_template(
            "result.html",
            quiz=quiz_obj,
            score=correct_count,
            total=total,
            wrong=wrong_count,
            percentage=percentage,
            passed=passed,
            breakdown=answer_breakdown,
        )

    except Exception as exc:
        db.session.rollback()
        logger.error(f"Error submitting quiz: {exc}")
        flash("Something went wrong while grading your quiz.", "danger")
        return redirect(url_for("main.dashboard"))


# ----------------------------------------------------------------------
# Previous results
# ----------------------------------------------------------------------
@main_bp.route("/previous_results")
@login_required
@student_required
def previous_results():
    results = (
        Result.query.filter_by(user_id=current_user.id)
        .order_by(Result.submitted_at.desc())
        .all()
    )
    return render_template("previous_results.html", results=results)


# ----------------------------------------------------------------------
# Leaderboard - Top 10 by score
# ----------------------------------------------------------------------
@main_bp.route("/leaderboard")
@login_required
def leaderboard():
    top_results = (
        db.session.query(
            User.fullname,
            Result.score,
            Result.total_questions,
            Result.percentage,
        )
        .join(User, User.id == Result.user_id)
        .order_by(Result.score.desc(), Result.percentage.desc())
        .limit(10)
        .all()
    )
    return render_template("leaderboard.html", top_results=top_results)


# ----------------------------------------------------------------------
# Error handlers
# ----------------------------------------------------------------------
@main_bp.app_errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404


@main_bp.app_errorhandler(500)
def server_error(error):
    logger.error(f"Server error: {error}")
    return render_template("500.html"), 500


@main_bp.app_errorhandler(403)
def forbidden(error):
    return render_template("404.html"), 403

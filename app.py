"""
app.py
------
Application factory. Run with:  python app.py
"""

import logging
from flask import Flask
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from sqlalchemy import inspect, text

from config import Config
from database import db
from models import User

logger = logging.getLogger("quiz_app")


def _run_auto_migrations():
    """
    Self-healing migration.

    If this app was previously deployed with an older schema (e.g. no
    'role' column on users, or questions/results without 'quiz_id'),
    this adds whatever is missing automatically at startup so nobody
    has to run manual SQL migration commands.

    Safe to run every time the app starts: it only ever adds columns
    that don't already exist.
    """
    inspector = inspect(db.engine)
    existing_tables = inspector.get_table_names()

    try:
        if "users" in existing_tables:
            user_columns = [c["name"] for c in inspector.get_columns("users")]
            if "role" not in user_columns:
                logger.info("Migration: adding 'role' column to users table")
                db.session.execute(text(
                    "ALTER TABLE users ADD COLUMN role VARCHAR(10) NOT NULL DEFAULT 'student'"
                ))
                db.session.commit()

        if "questions" in existing_tables:
            question_columns = [c["name"] for c in inspector.get_columns("questions")]
            if "quiz_id" not in question_columns:
                logger.info("Migration: adding 'quiz_id' column to questions table")
                db.session.execute(text(
                    "ALTER TABLE questions ADD COLUMN quiz_id INT NULL"
                ))
                db.session.commit()
            if "category" in question_columns:
                logger.info("Migration: dropping legacy 'category' column from questions table")
                db.session.execute(text(
                    "ALTER TABLE questions DROP COLUMN category"
                ))
                db.session.commit()

        if "results" in existing_tables:
            result_columns = [c["name"] for c in inspector.get_columns("results")]
            if "quiz_id" not in result_columns:
                logger.info("Migration: adding 'quiz_id' column to results table")
                db.session.execute(text(
                    "ALTER TABLE results ADD COLUMN quiz_id INT NULL"
                ))
                db.session.commit()

    except Exception as exc:
        db.session.rollback()
        logger.error(f"Auto-migration skipped/failed (safe to ignore on a brand-new database): {exc}")


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # ---- Logging -------------------------------------------------
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    # ---- Extensions ------------------------------------------------
    db.init_app(app)
    CSRFProtect(app)  # global CSRF protection for all POST forms

    login_manager = LoginManager()
    login_manager.login_view = "main.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "warning"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # ---- Blueprints --------------------------------------------------
    from routes import main_bp
    app.register_blueprint(main_bp)

    # ---- Create any missing tables, then patch any existing tables ----
    with app.app_context():
        db.create_all()
        _run_auto_migrations()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

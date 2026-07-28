"""
database.py
------------
Holds the single SQLAlchemy() instance used by the whole app.
Kept in its own file so models.py and app.py can both import it
without causing circular-import errors.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# QuizMaster — Full Stack Flask + MySQL Quiz Application

A complete two-tier quiz application built with Flask, SQLAlchemy, MySQL,
Bootstrap 5, and Flask-Login.

---

## 1. Project Structure

```
quiz-app/
├── app.py               # Application factory / entry point
├── config.py             # Configuration loaded from .env
├── database.py            # Shared SQLAlchemy() instance
├── models.py              # User, Question, Result ORM models
├── forms.py               # Flask-WTF signup/login forms
├── routes.py               # All routes (Blueprint "main")
├── requirements.txt
├── .env                     # Environment variables
├── Dockerfile
├── docker-compose.yml
├── sql/
│   └── schema.sql            # CREATE DATABASE/TABLE + 56 seed questions
├── static/
│   ├── css/style.css
│   ├── js/script.js
│   └── js/quiz.js
└── templates/
    ├── base.html, index.html, signup.html, login.html,
    ├── dashboard.html, quiz.html, result.html,
    ├── leaderboard.html, previous_results.html, 404.html, 500.html
```

---

## 2. Option A — Run with Docker Compose (recommended)

Requires Docker + Docker Compose installed.

```bash
cd quiz-app
docker-compose up --build
```

This starts:
- **db** — a MySQL 8 container, auto-seeded from `sql/schema.sql`
- **web** — the Flask app served by Gunicorn on port 5000

Visit **http://localhost:5000**

To stop: `docker-compose down` (add `-v` to also wipe the database volume).

---

## 3. Option B — Run Locally (manual setup)

### 3.1 Prerequisites
- Python 3.10+
- MySQL Server 8.0+ running locally

### 3.2 Create a virtual environment
```bash
cd quiz-app
python -m venv venv

# Activate:
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
```

### 3.3 Install dependencies
```bash
pip install -r requirements.txt
```

### 3.4 Configure MySQL
Log in to MySQL and create the user (or reuse root):
```sql
CREATE USER 'quizuser'@'localhost' IDENTIFIED BY 'quizpassword';
GRANT ALL PRIVILEGES ON quiz_app_db.* TO 'quizuser'@'localhost';
FLUSH PRIVILEGES;
```

### 3.5 Import the database schema + seed questions
```bash
mysql -u quizuser -p < sql/schema.sql
```
(This creates the database, tables, and inserts 56 sample questions.)

### 3.6 Configure environment variables
Edit `.env` to match your MySQL credentials:
```
DB_HOST=localhost
DB_PORT=3306
DB_USER=quizuser
DB_PASSWORD=quizpassword
DB_NAME=quiz_app_db
SECRET_KEY=change-this-to-a-long-random-secret-key
```

### 3.7 Run the application
```bash
python app.py
```
Visit **http://localhost:5000**

> Note: `app.py` also calls `db.create_all()` on startup as a safety net,
> so tables will exist even if you skip step 3.5 — but you still need
> `sql/schema.sql` to get the 56 seed questions.

---

## 4. API / Route Reference

| Route                 | Method    | Auth Required | Description                              |
|------------------------|-----------|----------------|-------------------------------------------|
| `/`                     | GET       | No             | Landing page                              |
| `/signup`               | GET/POST  | No             | Create a new account                      |
| `/login`                | GET/POST  | No             | Log in                                    |
| `/logout`               | GET       | Yes            | Log out and clear session                 |
| `/dashboard`             | GET       | Yes            | User dashboard with recent attempts       |
| `/quiz`                  | GET       | Yes            | Starts a quiz with 10 random questions    |
| `/submit_quiz`            | POST      | Yes            | Grades submitted answers, stores Result   |
| `/previous_results`        | GET       | Yes            | Full quiz history for the logged-in user |
| `/leaderboard`             | GET       | Yes            | Top 10 scorers, sorted by score           |

---

## 5. Security Features Implemented

- **Password hashing** via Werkzeug (`generate_password_hash` / `check_password_hash`)
- **Session-based auth** via Flask-Login (`login_required`, `current_user`)
- **CSRF protection** globally enabled via Flask-WTF `CSRFProtect`
- **SQL injection prevention** — all queries go through SQLAlchemy ORM (parameterized)
- **Server-side input validation** via WTForms validators (`DataRequired`, `Email`, `Length`, `EqualTo`)
- **Duplicate email check** on signup
- **Quiz answer tamper-resistance** — question set for a quiz attempt is stored server-side in the session, not trusted from the form

---

## 6. Architecture / Best Practices

- **MVC-style structure**: `models.py` (Model), `templates/` (View), `routes.py` (Controller)
- **Flask Blueprint** (`main_bp`) keeps routes modular and decoupled from `app.py`
- **Application factory pattern** (`create_app()`) for clean initialization and testability
- **Centralized logging** via Python's `logging` module
- **Environment-based config** — no secrets hard-coded, loaded via `python-dotenv`
- **Global error handlers** for 404 / 500

---

## 7. Default Test Flow

1. Sign up with a name, email, and password
2. Log in
3. Click **Start Quiz** → answer 10 random questions
4. Submit → see instant score, pass/fail, percentage, and answer review
5. Check **Leaderboard** and **Previous Results**
# quiz-app-k8s-kind-cluster

-- =========================================================
-- QuizMaster - MySQL Schema (Teacher / Student edition)
-- =========================================================

CREATE DATABASE IF NOT EXISTS quiz_app_db
    CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE quiz_app_db;

-- ---------------------------------------------------------
-- Table: users  (role: 'student' | 'teacher')
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fullname VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(10) NOT NULL DEFAULT 'student',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ---------------------------------------------------------
-- Table: quizzes  (created by a teacher, max 10 per teacher
-- is enforced in the application layer, routes.py)
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS quizzes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    description VARCHAR(500),
    teacher_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------
-- Table: questions  (each question belongs to one quiz)
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    quiz_id INT NOT NULL,
    question VARCHAR(500) NOT NULL,
    option_a VARCHAR(255) NOT NULL,
    option_b VARCHAR(255) NOT NULL,
    option_c VARCHAR(255) NOT NULL,
    option_d VARCHAR(255) NOT NULL,
    correct_answer CHAR(1) NOT NULL,
    FOREIGN KEY (quiz_id) REFERENCES quizzes(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------
-- Table: results
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    quiz_id INT,
    score INT NOT NULL,
    total_questions INT NOT NULL,
    percentage FLOAT NOT NULL,
    submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (quiz_id) REFERENCES quizzes(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- =========================================================
-- Optional demo seed data: one teacher + one sample quiz.
-- Replace the password hash below (this one is for "teacher123")
-- or simply sign up through the app instead of using this seed.
-- =========================================================

-- INSERT INTO users (fullname, email, password, role) VALUES
-- ('Demo Teacher', 'teacher@example.com', '<werkzeug-hash-here>', 'teacher');
--
-- INSERT INTO quizzes (title, description, teacher_id) VALUES
-- ('Python Basics', 'A quick quiz on Python fundamentals', 1);
--
-- INSERT INTO questions (quiz_id, question, option_a, option_b, option_c, option_d, correct_answer) VALUES
-- (1, 'Which keyword is used to define a function in Python?', 'func', 'def', 'function', 'lambda', 'B'),
-- (1, 'Which data type is immutable in Python?', 'list', 'dictionary', 'set', 'tuple', 'D');

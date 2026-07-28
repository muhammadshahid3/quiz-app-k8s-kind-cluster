-- =========================================================
-- Migration for an EXISTING quiz_app_db created by the old
-- (pre-teacher) version of the app. Run this once.
-- =========================================================
USE quiz_app_db;

-- 1. Add role to users
ALTER TABLE users
    ADD COLUMN role VARCHAR(10) NOT NULL DEFAULT 'student';

-- 2. Create the quizzes table
CREATE TABLE IF NOT EXISTS quizzes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    description VARCHAR(500),
    teacher_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 3. Give old questions somewhere to live: a placeholder quiz
--    owned by the first user in the table, then link quiz_id.
--    (Skip this block if you don't care about old questions.)
INSERT INTO quizzes (title, description, teacher_id)
SELECT 'Legacy Question Bank', 'Auto-created during migration', id
FROM users ORDER BY id LIMIT 1;

ALTER TABLE questions
    ADD COLUMN quiz_id INT NOT NULL DEFAULT 1;

UPDATE questions SET quiz_id = (SELECT id FROM quizzes ORDER BY id LIMIT 1);

ALTER TABLE questions
    ADD CONSTRAINT fk_questions_quiz FOREIGN KEY (quiz_id) REFERENCES quizzes(id) ON DELETE CASCADE;

ALTER TABLE questions DROP COLUMN category;
ALTER TABLE questions ALTER COLUMN quiz_id DROP DEFAULT;

-- 4. Link results to quizzes
ALTER TABLE results
    ADD COLUMN quiz_id INT NULL,
    ADD CONSTRAINT fk_results_quiz FOREIGN KEY (quiz_id) REFERENCES quizzes(id) ON DELETE SET NULL;

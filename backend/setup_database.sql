-- Drop tables if they exist (for clean setup)
DROP TABLE IF EXISTS user_feedbacks CASCADE;
DROP TABLE IF EXISTS user_preferences CASCADE;
DROP TABLE IF EXISTS users CASCADE;


-- Create users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create user_preferences table
CREATE TABLE user_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    preferred_languages JSON DEFAULT '[]',
    liked_genres JSON DEFAULT '[]',
    liked_authors JSON DEFAULT '[]',
    liked_book_ids JSON DEFAULT '[]',
    disliked_genres JSON DEFAULT '[]',
    disliked_authors JSON DEFAULT '[]',
    disliked_book_ids JSON DEFAULT '[]',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create user_feedbacks table
CREATE TABLE user_feedbacks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    book_id VARCHAR(100) NOT NULL,
    feedback_type VARCHAR(20) NOT NULL,
    rating FLOAT,
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample users
INSERT INTO users (username, hashed_password, created_at)
VALUES 
    ('alice', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzS6qY.5M.', '2026-01-01 10:00:00'),
    ('bob', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzS6qY.5M.', '2026-01-02 11:30:00'),
    ('charlie', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzS6qY.5M.', '2026-01-03 14:15:00');

-- Insert sample preferences
INSERT INTO user_preferences (user_id, preferred_languages, liked_genres, liked_authors, liked_book_ids, disliked_genres)
VALUES 
    (1, '["en"]', '["Fantasy", "Science Fiction"]', '["J.K. Rowling", "Suzanne Collins"]', '["en_2767052-the-hunger-games"]', '["Horror"]'),
    (2, '["en"]', '["Mystery", "Thriller"]', '["Agatha Christie"]', '[]', '[]'),
    (3, '["en"]', '["Young Adult", "Romance"]', '[]', '["en_2.Harry_Potter_and_the_Order_of_the_Phoenix"]', '["Dystopia"]');

-- Insert sample feedbacks
INSERT INTO user_feedbacks (user_id, book_id, feedback_type, rating, comment)
VALUES 
    (1, 'en_2767052-the-hunger-games', 'liked', 5.0, 'Absolutely loved it!'),
    (1, 'en_2.Harry_Potter_and_the_Order_of_the_Phoenix', 'liked', 4.5, 'Great book'),
    (2, 'en_2767052-the-hunger-games', 'read', 4.0, 'Good but intense'),
    (3, 'en_2.Harry_Potter_and_the_Order_of_the_Phoenix', 'liked', 5.0, 'My favorite!');

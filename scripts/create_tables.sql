-- SkyrisReward Database Table Creation Script
-- This script creates all necessary tables for the SkyrisReward application

-- Create database if not exists (optional, uncomment if needed)
-- CREATE DATABASE IF NOT EXISTS skyrisreward CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- USE skyrisreward;

-- Drop existing tables if they exist (for clean creation)
DROP TABLE IF EXISTS notifications;
DROP TABLE IF EXISTS reviews;
DROP TABLE IF EXISTS rewards;
DROP TABLE IF EXISTS task_assignments;
DROP TABLE IF EXISTS tasks;
DROP TABLE IF EXISTS users;

-- Create users table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(64) NOT NULL UNIQUE,
    password_hash VARCHAR(128) NOT NULL,
    email VARCHAR(128),
    role ENUM('user', 'publisher', 'admin') NOT NULL DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT = 'Users table - stores basic user information';

-- Create tasks table
CREATE TABLE tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(128) NOT NULL,
    description TEXT,
    publisher_id INT NOT NULL,
    reward_amount FLOAT NOT NULL,
    status ENUM('open', 'in_progress', 'pending_review', 'completed', 'closed') NOT NULL DEFAULT 'open',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_publisher_id (publisher_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at),
    FOREIGN KEY (publisher_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT = 'Tasks table - stores published task information';

-- Create task_assignments table
CREATE TABLE task_assignments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    task_id INT NOT NULL,
    user_id INT NOT NULL,
    submit_content TEXT,
    submit_time TIMESTAMP NULL,
    status ENUM('pending_review', 'approved', 'rejected', 'appealing') NOT NULL DEFAULT 'pending_review',
    review_time TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_task_id (task_id),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    UNIQUE KEY unique_task_user (task_id, user_id),
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT = 'Task assignments table - stores user task acceptance information';

-- Create reviews table
CREATE TABLE reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    assignment_id INT NOT NULL,
    reviewer_id INT NOT NULL,
    review_result ENUM('pending', 'approved', 'rejected', 'appealing') NOT NULL DEFAULT 'pending',
    review_comment TEXT,
    review_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_assignment_id (assignment_id),
    INDEX idx_reviewer_id (reviewer_id),
    INDEX idx_review_result (review_result),
    FOREIGN KEY (assignment_id) REFERENCES task_assignments(id) ON DELETE CASCADE,
    FOREIGN KEY (reviewer_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT = 'Reviews table - stores task review information';

-- Create rewards table
CREATE TABLE rewards (
    id INT AUTO_INCREMENT PRIMARY KEY,
    assignment_id INT NOT NULL,
    amount FLOAT NOT NULL,
    status ENUM('pending', 'issued', 'failed') NOT NULL DEFAULT 'pending',
    issued_time TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_assignment_id (assignment_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at),
    UNIQUE KEY unique_assignment_reward (assignment_id),
    FOREIGN KEY (assignment_id) REFERENCES task_assignments(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT = 'Rewards table - stores reward distribution information';

-- Create notifications table
CREATE TABLE notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    content VARCHAR(256) NOT NULL,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_is_read (is_read),
    INDEX idx_created_at (created_at),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT = 'Notifications table - stores user notification information';

-- Print success message
SELECT 'All tables created successfully!' AS message;
-- SkyrisReward Database Initialization Script
-- This script provides basic database initialization functionality
-- Use this script to set up database configuration and basic settings

-- Use the database (uncomment and modify as needed)
-- USE skyrisreward;

-- Set MySQL configuration for better Unicode support
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;
SET collation_connection = utf8mb4_unicode_ci;

-- Create database if not exists (optional)
-- CREATE DATABASE IF NOT EXISTS skyrisreward CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Print initialization message
SELECT 'Database initialization script loaded successfully!' AS message,
       'Please run create_tables.sql to create the database tables.' AS instruction,
       'Make sure your database connection is properly configured.' AS reminder;

-- Optional: Add any database-level configurations here
-- Example: Set timezone, storage engine preferences, etc.
-- SET time_zone = '+00:00';
-- SET default_storage_engine = InnoDB;
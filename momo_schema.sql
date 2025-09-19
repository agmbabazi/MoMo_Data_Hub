CREATE DATABASE IF NOT EXISTS momo_db;
USE momo_db;

-- System_logs table
CREATE TABLE IF NOT EXISTS System_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    status ENUM('success','failed','pending') NOT NULL,
    context TEXT NOT NULL
);

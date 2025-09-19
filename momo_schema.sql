CREATE DATABASE IF NOT EXISTS momo_db;
USE momo_db;

-- Users table: stores sender/receiver info
CREATE TABLE Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Unique user/customer ID',
    name VARCHAR(100) NOT NULL COMMENT 'Full name of user',
    phone VARCHAR(20) NOT NULL UNIQUE COMMENT 'Mobile phone number',
    email VARCHAR(100) COMMENT 'Email address'
);

-- Transaction Categories table: types of transactions
CREATE TABLE Transaction_Categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Unique category ID',
    name VARCHAR(50) NOT NULL COMMENT 'Transaction type name',
    description VARCHAR(255) COMMENT 'Category description'
);

-- Transactions table: main transaction records
CREATE TABLE Transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Unique transaction ID',
    sender_id INT NOT NULL COMMENT 'FK to Users (sender)',
    receiver_id INT NOT NULL COMMENT 'FK to Users (receiver)',
    category_id INT NOT NULL COMMENT 'FK to Transaction_Categories',
    amount DECIMAL(12,2) NOT NULL COMMENT 'Transaction amount',
    currency VARCHAR(10) NOT NULL COMMENT 'Currency code',
    fee DECIMAL(12,2) DEFAULT 0 COMMENT 'Transaction fee',
    balance DECIMAL(12,2) COMMENT 'Balance after transaction',
    transaction_date DATETIME NOT NULL COMMENT 'Transaction date/time',
    status VARCHAR(20) NOT NULL COMMENT 'Transaction status',
    sms_body TEXT COMMENT 'Original SMS body',
    FOREIGN KEY (sender_id) REFERENCES Users(user_id),
    FOREIGN KEY (receiver_id) REFERENCES Users(user_id),
    FOREIGN KEY (category_id) REFERENCES Transaction_Categories(category_id),
    INDEX idx_sender (sender_id),
    INDEX idx_receiver (receiver_id),
    INDEX idx_category (category_id)
);

-- System Logs table: tracks data processing events
CREATE TABLE System_Logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Unique log ID',
    transaction_id INT COMMENT 'FK to Transactions',
    log_time DATETIME NOT NULL COMMENT 'Log timestamp',
    message VARCHAR(255) NOT NULL COMMENT 'Log message',
    FOREIGN KEY (transaction_id) REFERENCES Transactions(transaction_id)
);

-- Junction table for many-to-many relationships (if needed in future)
CREATE TABLE User_Transaction_Roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    transaction_id INT NOT NULL,
    role VARCHAR(20) NOT NULL COMMENT 'Role in transaction (sender/receiver/other)',
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (transaction_id) REFERENCES Transactions(transaction_id)
);
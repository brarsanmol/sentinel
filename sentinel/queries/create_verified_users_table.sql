-- :name create_verified_users_table
CREATE TABLE IF NOT EXISTS verified_users (
    identifier VARCHAR(255) PRIMARY KEY,
    email_address VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

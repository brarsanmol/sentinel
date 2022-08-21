-- :name create_verification_tokens_table
CREATE TABLE IF NOT EXISTS verification_tokens (
    email_address VARCHAR(255) PRIMARY KEY,
    token VARCHAR(6) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

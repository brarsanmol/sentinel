-- :name create_tokens_table
CREATE TABLE IF NOT EXISTS verification_tokens (
    identifier INTEGER PRIMARY KEY,
    email_address VARCHAR(255) NOT NULL UNIQUE,
    token VARCHAR(6) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

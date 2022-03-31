-- :name find_by_email_address :one
SELECT * FROM verification_tokens WHERE email_address = :email_address

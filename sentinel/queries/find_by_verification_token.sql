-- :name find_by_verification_token :one
SELECT * FROM verification_tokens WHERE token = :token

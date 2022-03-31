-- :name find_by_token :one
SELECT * FROM verification_tokens WHERE token = :token

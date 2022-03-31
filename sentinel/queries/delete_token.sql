-- :name delete_token :one
DELETE FROM verification_tokens WHERE token = :token

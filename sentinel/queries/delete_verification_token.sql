-- :name delete_verification_token :affected
DELETE FROM verification_tokens WHERE token = :token

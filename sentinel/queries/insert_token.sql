-- :name create_token :insert
INSERT INTO verification_tokens (email_address, token) VALUES(:email_address, :token)

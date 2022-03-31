-- :name create_verified_user :insert
INSERT INTO verified_users (identifier, email_address) VALUES(:identifier, :email_address)

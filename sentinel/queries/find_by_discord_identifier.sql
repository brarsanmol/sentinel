-- :name find_by_discord_identifier :one
SELECT * FROM verified_users WHERE identifier = :identifier

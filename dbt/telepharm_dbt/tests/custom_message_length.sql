-- Custom test: Ensure message_length is consistent with text length
SELECT *
FROM {{ ref('stg_telegram_messages') }}
WHERE message_length != LENGTH(COALESCE(text, ''))

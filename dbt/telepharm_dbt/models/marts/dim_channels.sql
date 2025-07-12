{{ config(
    materialized='table',
    schema='marts'
) }}

SELECT DISTINCT
    channel_id,
    channel AS channel_name,
    MIN(message_date) AS first_message_date,
    MAX(message_date) AS last_message_date,
    COUNT(*) AS total_messages
FROM {{ ref('stg_telegram_messages') }}
GROUP BY channel_id, channel

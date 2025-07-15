{{ config(
    materialized='table',
    schema='marts'
) }}

SELECT
    m.message_id,
    c.channel_id,
    m.message_date::DATE AS date_id,
    m.text,
    m.has_image,
    m.image_file,
    m.message_length,
    m.load_timestamp
FROM {{ ref('stg_telegram_messages') }} m
JOIN {{ ref('dim_channels') }} c ON m.channel_id = c.channel_id
JOIN {{ ref('dim_dates') }} d ON m.message_date::DATE = d.date_id

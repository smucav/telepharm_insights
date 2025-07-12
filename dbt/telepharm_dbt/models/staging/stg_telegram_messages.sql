{{ config(
    materialized='view',
    schema='staging'
) }}

SELECT
    message_id,
    channel,
    scrape_date::DATE,
    message_date::TIMESTAMP,
    sender_id AS channel_id,
    COALESCE(text, '') AS text,
    has_image,
    image_file,
    message_length,
    load_timestamp::TIMESTAMP
FROM raw.telegram_messages

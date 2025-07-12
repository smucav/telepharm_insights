{{ config(
    materialized='table',
    schema='marts'
) }}

WITH date_range AS (
    SELECT generate_series(
        (SELECT MIN(message_date)::DATE FROM {{ ref('stg_telegram_messages') }}),
        (SELECT MAX(message_date)::DATE FROM {{ ref('stg_telegram_messages') }}),
        INTERVAL '1 day'
    ) AS date
)
SELECT
    date AS date_id,
    EXTRACT(YEAR FROM date) AS year,
    EXTRACT(MONTH FROM date) AS month,
    EXTRACT(DAY FROM date) AS day,
    EXTRACT(DOW FROM date) AS day_of_week,
    EXTRACT(WEEK FROM date) AS week_of_year,
    CASE
        WHEN EXTRACT(DOW FROM date) IN (0, 6) THEN TRUE
        ELSE FALSE
    END AS is_weekend
FROM date_range

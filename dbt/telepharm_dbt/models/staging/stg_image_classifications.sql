{{ config(
    materialized='view',
    schema='staging'
) }}

SELECT
    classification_id,
    message_id,
    image_file,
    object_class,
    confidence,
    load_timestamp::TIMESTAMP
FROM raw.image_classifications
WHERE confidence >= 0.5  -- Filter low-confidence detections

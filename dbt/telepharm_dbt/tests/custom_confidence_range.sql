-- Custom test: Ensure confidence scores are between 0 and 1
SELECT *
FROM {{ ref('stg_image_classifications') }}
WHERE confidence < 0 OR confidence > 1

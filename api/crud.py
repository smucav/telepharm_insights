from typing import List
from .schemas import TopProduct, ChannelActivity, MessageSearch
import logging

logging.basicConfig(
    filename='api/logs/api.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def get_top_products(db, limit: int) -> List[TopProduct]:
    """Get top products from messages and image classifications."""
    with db.cursor() as cur:
        cur.execute("""
            WITH text_mentions AS (
                SELECT
                    UNNEST(ARRAY['pill', 'cream', 'syringe', 'bottle']) AS product,
                    COUNT(*) AS mention_count
                FROM raw_marts.fct_messages
                WHERE text ILIKE ANY (ARRAY['%pill%', '%cream%', '%syringe%', '%bottle%'])
                GROUP BY product
            ), image_mentions AS (
                SELECT
                    object_class AS product,
                    COUNT(*) AS mention_count
                FROM raw_staging.stg_image_classifications
                GROUP BY object_class
            )
            SELECT
                COALESCE(t.product, i.product) AS product,
                COALESCE(t.mention_count, 0) + COALESCE(i.mention_count, 0) AS mention_count
            FROM text_mentions t
            FULL OUTER JOIN image_mentions i ON t.product = i.product
            ORDER BY mention_count DESC
            LIMIT %s
        """, (limit,))
        results = cur.fetchall()
        logger.info(f"DEBUG get_top_products: results = {results}")
    return [TopProduct(product=row[0], mention_count=row[1]) for row in results]

def get_channel_activity(db, channel_name: str) -> List[ChannelActivity]:
    """Get posting activity for a channel."""
    with db.cursor() as cur:
        cur.execute("""
            WITH
                ic_agg AS (
                    SELECT
                        fm.date_id,
                        d.date_id AS dim_date_id,
                        ic.object_class,
                        COUNT(ic.classification_id) AS detection_count,
                        AVG(ic.confidence) AS avg_confidence
                    FROM raw_marts.fct_messages fm
                    JOIN raw_marts.dim_channels c ON fm.channel_id = c.channel_id
                    JOIN raw_marts.dim_dates d ON fm.date_id = d.date_id
                    LEFT JOIN raw_staging.stg_image_classifications ic ON fm.message_id = ic.message_id
                    WHERE c.channel_name = %s AND ic.object_class IS NOT NULL
                    GROUP BY fm.date_id, d.date_id, ic.object_class
                ),
                activity AS (
                    SELECT
                        d.date_id::TEXT,
                        COUNT(fm.message_id) AS message_count,
                        SUM(CASE WHEN fm.has_image THEN 1 ELSE 0 END) AS image_count,
                        JSON_AGG(
                            JSON_BUILD_OBJECT(
                                'object_class', ic_agg.object_class,
                                'detection_count', ic_agg.detection_count,
                                'avg_confidence', ic_agg.avg_confidence
                            )
                        ) AS object_detections
                    FROM raw_marts.fct_messages fm
                    JOIN raw_marts.dim_channels c ON fm.channel_id = c.channel_id
                    JOIN raw_marts.dim_dates d ON fm.date_id = d.date_id
                    LEFT JOIN ic_agg ON fm.date_id = ic_agg.dim_date_id
                    WHERE c.channel_name = %s
                    GROUP BY d.date_id
                    ORDER BY d.date_id DESC
                )
            SELECT
                date_id,
                message_count,
                image_count,
                COALESCE(object_detections, '[]') AS object_detections
            FROM activity
        """, (channel_name, channel_name))
        results = cur.fetchall()
    return [
        ChannelActivity(
            date_id=row[0],
            message_count=row[1],
            image_count=row[2],
            object_detections=row[3] or []
        ) for row in results
    ]

def search_messages(db, query: str) -> List[MessageSearch]:
    """Search messages by keyword."""
    with db.cursor() as cur:
        cur.execute("""
            SELECT
                fm.message_id,
                c.channel_name,
                fm.load_timestamp::TEXT AS message_date,
                fm.text
            FROM raw_marts.fct_messages fm
            JOIN raw_marts.dim_channels c ON fm.channel_id = c.channel_id
            WHERE fm.text ILIKE %s
            ORDER BY fm.load_timestamp DESC
            LIMIT 50
        """, (f'%{query}%',))
        results = cur.fetchall()
    return [
        MessageSearch(
            message_id=row[0],
            channel_name=row[1],
            message_date=row[2],
            text=row[3]
        ) for row in results
    ]

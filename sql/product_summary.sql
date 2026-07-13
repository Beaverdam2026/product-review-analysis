--grain: one row per (avg_stars bin x review_count bucket)

WITH product_stats AS (
    SELECT COUNT(r.review_id) AS review_count,
        AVG(r.overall) AS avg_stars
    FROM reviews r
    GROUP BY r.asin
)

SELECT FLOOR(ps.avg_stars * 5) / 5.0 as stars_bin,
    COUNT(*) AS product_count,
    SUM(ps.review_count) AS total_reviews,
    CASE
        WHEN ps.review_count < 10  THEN '5-9'
        WHEN ps.review_count < 30  THEN '10-29'
        WHEN ps.review_count < 100 THEN '30-99'
        ELSE '100+'
    END AS size_bucket,
    MIN(ps.review_count) AS bucket_order


FROM product_stats ps
GROUP BY FLOOR(ps.avg_stars * 5) / 5.0, size_bucket
ORDER BY MIN(review_count);


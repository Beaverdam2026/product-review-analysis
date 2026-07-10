-- isolate product-day star measure
-- grain: per product per day
WITH daily AS (
    SELECT r.asin,
        r.unix_review_time AS day,
        COUNT(*) AS n_reviews,
        SUM(r.overall) AS star_sum
    FROM reviews_clean r
    GROUP BY r.asin, r.unix_review_time
),

trajectory AS (
    SELECT d.asin,
        d.day,
        d.n_reviews,
        d.star_sum,
        SUM(star_sum) OVER w / SUM(n_reviews) OVER w AS running_avg
    FROM daily d
WINDOW w AS (PARTITION BY d.asin ORDER BY day)
),

lagged AS (
    SELECT t.asin,
        t.day,
        t.n_reviews,
        t.star_sum,
        t.running_avg,
        lag(running_avg) OVER (PARTITION BY t.asin
        ORDER BY day) AS prev_running_avg
    from trajectory t
)

SELECT p.title,
    l.asin,
    l.day,
    l.n_reviews,
    l.star_sum,
    l.running_avg,
    l.prev_running_avg,
    l.running_avg - l.prev_running_avg AS delta
FROM lagged l
LEFT JOIN products p
ON l.asin = p.asin
ORDER BY l.asin, l.day
LIMIT 10;

-- grain: per product per week, of top 30 products
WITH ranking AS (
    SELECT r.asin,
    RANK() OVER (ORDER BY COUNT(*) DESC) AS rank_by_reviews
    FROM reviews r
    GROUP BY asin
),

weekly AS (
    SELECT r.asin,
        DATE(r.unix_review_time, 'unixepoch', '-6 days', 'weekday 1') AS week,
        COUNT(*) AS n_reviews,
        SUM(r.overall) AS star_sum
    FROM reviews r
    WHERE r.asin IN (SELECT asin FROM ranking WHERE rank_by_reviews <= 30)
    GROUP BY r.asin, week
),

trajectory AS (
    SELECT d.asin,
        d.week,
        d.n_reviews,
        d.star_sum,
        SUM(star_sum) OVER w / SUM(n_reviews) OVER w AS running_avg,
        SUM(n_reviews) OVER w AS review_count
    FROM weekly d
WINDOW w AS (PARTITION BY d.asin ORDER BY d.week)
),

lagged AS (
    SELECT t.asin,
        t.week,
        t.n_reviews,
        t.star_sum,
        t.running_avg,
        lag(running_avg) OVER (PARTITION BY t.asin
        ORDER BY t.week) AS prev_running_avg
    from trajectory t
    --filtering out weeks before products had 10 reviews for better viz readability
    WHERE t.review_count >= 10
)

SELECT COALESCE(p.title, l.asin) AS title,
    l.asin,
    l.week,
    l.n_reviews,
    l.star_sum,
    l.running_avg,
    l.prev_running_avg,
    l.running_avg - l.prev_running_avg AS delta
FROM lagged l
LEFT JOIN products p
ON l.asin = p.asin
ORDER BY l.asin, l.week;

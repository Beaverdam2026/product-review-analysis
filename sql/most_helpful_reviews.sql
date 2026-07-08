WITH ranked AS (
    SELECT r.review_id,
        ROW_NUMBER() OVER (PARTITION BY asin
        ORDER BY helpful_votes DESC) as rn
    FROM reviews_clean r
)

SELECT p.title,
r.reviewer_id,
r.reviewer_name,
r.helpful_votes,
r.total_votes,
-- Casting ratios of 0 as NULL to be converted to NaN in pandas later
CAST(r.helpful_votes AS REAL) / NULLIF(r.total_votes, 0) AS vote_ratio,
r.overall,
r.unix_review_time
FROM reviews_clean r
JOIN ranked rn ON r.review_id = rn.review_id
LEFT JOIN products p
ON r.asin = p.asin
WHERE rn = 1
ORDER BY r.helpful_votes DESC
LIMIT 10;
--ranking done
--TODO: flesh out the other columns selected to fit the use
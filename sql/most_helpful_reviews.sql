--grain: per product's top review, filtered for products with >=5 helpful votes on their top review
WITH ranked AS (
    SELECT r.review_id,
        ROW_NUMBER() OVER (PARTITION BY asin
        --ordering by review id to make code deterministic in ~20 cases where
        --there is a match of (helpful_votes, total_votes)
        ORDER BY r.helpful_votes DESC, r.total_votes, r.review_id) as rn
    FROM reviews r
)

SELECT COALESCE(p.title, r.asin) AS title,
r.asin,
r.reviewer_id,
r.reviewer_name,
r.helpful_votes,
r.total_votes,
-- casting ratios of 0 as NULL to be converted to NaN in pandas
-- never happens with r.helpful_votes >= 5 in the WHERE
CAST(r.helpful_votes AS REAL) / NULLIF(r.total_votes, 0) AS vote_ratio,
r.overall,
r.unix_review_time
FROM reviews r
JOIN ranked rn ON r.review_id = rn.review_id
LEFT JOIN products p
ON r.asin = p.asin
WHERE rn = 1 AND r.helpful_votes >= 5
ORDER BY r.helpful_votes DESC;
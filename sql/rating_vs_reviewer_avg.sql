WITH reviewer_avg_stars AS (
    SELECT r.reviewer_id,
        AVG(r.overall) AS reviewer_avg_stars
    FROM reviews r
    GROUP BY r.reviewer_id
)


SELECT p.title,
    r.reviewer_name,
    r.overall AS stars,
    COUNT(r.review_id) OVER (PARTITION BY r.reviewer_id) AS review_count,
    ra.reviewer_avg_stars,
    r.overall - ra.reviewer_avg_stars AS above_reviewer_avg
FROM reviews r
JOIN reviewer_avg_stars ra 
    ON ra.reviewer_id = r.reviewer_id
LEFT JOIN products p 
    ON r.asin = p.asin;
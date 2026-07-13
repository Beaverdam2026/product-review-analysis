--grain: per (stars, reviewer avg bin) cell
WITH reviewer_avg_stars AS (
    SELECT r.reviewer_id,
        AVG(r.overall) AS reviewer_avg_stars
    FROM reviews r
    GROUP BY r.reviewer_id
)

SELECT 
    r.overall AS stars,
    COUNT(*) AS review_count,
    FLOOR(ra.reviewer_avg_stars * 5) / 5.0 AS reviewer_avg_bin,
    r.overall - FLOOR(ra.reviewer_avg_stars * 5) / 5.0 AS above_reviewer_avg
FROM reviews r
JOIN reviewer_avg_stars ra 
    ON ra.reviewer_id = r.reviewer_id
GROUP BY r.overall, reviewer_avg_bin;
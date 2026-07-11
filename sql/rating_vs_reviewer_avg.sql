--grain: per (stars, reviewer avg bin) cell
WITH reviewer_avg_stars AS (
    SELECT r.reviewer_id,
        AVG(r.overall) AS reviewer_avg_stars
    FROM reviews_clean r
    GROUP BY r.reviewer_id
)


SELECT 
    r.overall AS stars,
    COUNT(*) AS review_count,
    round(ra.reviewer_avg_stars,1) AS reviewer_avg_bin,
    r.overall - ROUND(ra.reviewer_avg_stars,1) AS above_reviewer_avg
FROM reviews_clean r
JOIN reviewer_avg_stars ra 
    ON ra.reviewer_id = r.reviewer_id
GROUP BY r.overall, reviewer_avg_bin;
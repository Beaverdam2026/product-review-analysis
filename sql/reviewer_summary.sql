--grain: per distinct value of review_count

WITH reviewers AS (
    SELECT COUNT(r.review_id) AS review_count,
        AVG(r.overall) AS avg_rating
    FROM reviews_clean r
    GROUP BY r.reviewer_id
)

SELECT re.review_count,
       AVG(re.avg_rating) AS avg_reviewer_rating,
       COUNT(*) AS reviewer_count
       FROM reviewers re
       GROUP BY re.review_count
       ORDER BY review_count DESC;
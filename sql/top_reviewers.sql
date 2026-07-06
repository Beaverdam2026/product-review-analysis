.headers ON
.mode markdown

SELECT r.reviewer_name,
       COUNT(r.review_id) AS review_count,
       AVG(r.overall) AS avg_rating
       FROM reviews r
       GROUP BY r.reviewer_id
       ORDER BY review_count DESC;
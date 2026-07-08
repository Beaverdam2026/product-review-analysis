SELECT r.reviewer_name,
       COUNT(r.review_id) AS review_count,
       AVG(r.overall) AS avg_rating,
       MIN(unix_review_time) AS earliest_review,
       Max(unix_review_time) AS last_review
       FROM reviews r
       GROUP BY r.reviewer_id
       ORDER BY review_count DESC
       LIMIT 10;
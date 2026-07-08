SELECT p.title AS product_name,
COUNT(r.review_id) AS review_count,
p.brand,
AVG(r.overall) AS avg_stars,
AVG(r.helpful_votes) AS avg_upvotes,
AVG(r.total_votes) AS avg_votes,
MIN(r.unix_review_time) AS earliest_review,
MAX(r.unix_review_time) AS latest_review
FROM reviews r 
LEFT JOIN products p ON p.asin = r.asin
GROUP BY r.asin
ORDER BY review_count DESC
LIMIT 10;

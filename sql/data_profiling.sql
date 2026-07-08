-- Data-quality / integrity checks run before trusting any analysis.

-- 1. Brand completeness on the items in the products metadata dataset that
--    are also present in the reviews dataset
--    Finding: 5068 of 10429 products in reviews dataset have NULL brand
--    zero empty strings, zero whitespace - missing brand is always NULL
--
SELECT COUNT(DISTINCT CASE WHEN p.brand IS NULL THEN r.asin END) AS null_brand,
       COUNT(DISTINCT CASE WHEN p.brand = ''   THEN r.asin END) AS empty_str_brand,
       COUNT(DISTINCT CASE WHEN TRIM(p.brand) = '' AND p.brand != '' THEN r.asin END) AS whitespace_brand,
       COUNT(DISTINCT r.asin) AS total_products
FROM reviews r
LEFT JOIN products p
on r.asin = p.asin;

-- 2. Review product title integrity
--    Finding: 0 join misses, 2,841 review rows across 237 distinct asins
--    have a product row but no title.
--
SELECT SUM(CASE WHEN p.asin IS NULL THEN 1 ELSE 0 END) AS reviews_no_product_row,
       SUM(CASE WHEN p.title IS NULL THEN 1 ELSE 0 END) AS reviews_no_title,
       COUNT(DISTINCT CASE WHEN p.title IS NULL THEN r.asin END) AS distinct_asins_no_title,
       COUNT(*) AS total_reviews
FROM reviews r
LEFT JOIN products p ON p.asin = r.asin;

-- 3. Duplicate review integrity per product
--    Flags products where the raw review count differs from the distinct
--    reviewer count - a reviewer reviewed the same product more than once
--    Finding: 0 products differ everywhere,
--    confirming one review per reviewer
SELECT COUNT(*) AS products_with_dupes
FROM (
    SELECT asin
    FROM reviews
    GROUP BY asin
    HAVING COUNT(review_id) <> COUNT(DISTINCT reviewer_id)
);

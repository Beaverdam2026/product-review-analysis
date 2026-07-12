CREATE TABLE IF NOT EXISTS reviews (
    review_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    reviewer_id      TEXT NOT NULL,
    asin             TEXT NOT NULL,
    reviewer_name    TEXT,
    helpful_votes    INTEGER NOT NULL,
    total_votes      INTEGER NOT NULL,
    review_text      TEXT,
    overall          REAL NOT NULL,
    summary          TEXT,
    unix_review_time INTEGER NOT NULL,
    review_time      TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_reviews_asin ON reviews(asin);
CREATE INDEX IF NOT EXISTS idx_reviews_reviewer_id ON reviews(reviewer_id);
CREATE INDEX IF NOT EXISTS idx_reviews_unix_review_time ON reviews(unix_review_time);

CREATE TABLE IF NOT EXISTS products (
    asin             TEXT PRIMARY KEY,
    title            TEXT,
    price            REAL,
    brand            TEXT,
    primary_category TEXT
);

-- Removes 2841 reviews from dataset vs original
-- unused because of minimal value added and viz issues
-- resulting from reducing reviewer review count to below 5
CREATE VIEW IF NOT EXISTS reviews_clean AS
SELECT r.*
from reviews r
JOIN products p ON p.asin = r.asin
WHERE p.title IS NOT NULL;
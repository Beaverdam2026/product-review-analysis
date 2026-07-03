CREATE TABLE reviews (
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

CREATE INDEX idx_reviews_asin ON reviews(asin);
CREATE INDEX idx_reviews_reviewer_id ON reviews(reviewer_id);
CREATE INDEX idx_reviews_unix_review_time ON reviews(unix_review_time);
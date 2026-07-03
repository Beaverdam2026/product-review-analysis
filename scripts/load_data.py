import json
import sqlite3
from pathlib import Path

DB_PATH = Path("data/reviews.db")
SCHEMA_PATH = Path("sql/schema.sql")
DATA_PATH = Path("data/Cell_Phones_and_Accessories_5.json")
BATCH_SIZE = 5000

INSERT_SQL = """
    INSERT INTO reviews (
        reviewer_id, asin, reviewer_name, helpful_votes, total_votes,
        review_text, overall, summary, unix_review_time, review_time
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""


def parse_record(line: str) -> tuple:
    record = json.loads(line)
    helpful_votes, total_votes = record.get("helpful", [0, 0])
    return (
        record["reviewerID"],
        record["asin"],
        record.get("reviewerName"),
        helpful_votes,
        total_votes,
        record.get("reviewText"),
        record["overall"],
        record.get("summary"),
        record["unixReviewTime"],
        record["reviewTime"],
    )


def print_sanity_stats(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    row_count = cur.execute("SELECT COUNT(*) FROM reviews").fetchone()[0]
    min_unix_time, max_unix_time = cur.execute(
        "SELECT MIN(unix_review_time), MAX(unix_review_time) FROM reviews"
    ).fetchone()
    # Human-readable review_time for the earliest and latest rows. Ordering is
    # done on unix_review_time (an integer that sorts chronologically), since
    # the review_time string ("05 21, 2014") does not sort correctly as text.
    min_readable_date = cur.execute(
        "SELECT review_time FROM reviews ORDER BY unix_review_time ASC LIMIT 1"
    ).fetchone()[0]
    max_readable_date = cur.execute(
        "SELECT review_time FROM reviews ORDER BY unix_review_time DESC LIMIT 1"
    ).fetchone()[0]
    rated_helpful = cur.execute(
        "SELECT COUNT(*) FROM reviews WHERE total_votes > 0"
    ).fetchone()[0]
    distinct_products = cur.execute(
        "SELECT COUNT(DISTINCT asin) FROM reviews"
    ).fetchone()[0]
    distinct_reviewers = cur.execute(
        "SELECT COUNT(DISTINCT reviewer_id) FROM reviews"
    ).fetchone()[0]

    print("\n--- Sanity stats ---")
    print(f"Rows loaded:          {row_count}")
    print(f"Distinct products:    {distinct_products}")
    print(f"Distinct reviewers:   {distinct_reviewers}")
    print(f"Rows with votes > 0:  {rated_helpful}")
    print(f"Earliest review: {min_unix_time} (unix) / {min_readable_date}")
    print(f"Latest review:   {max_unix_time} (unix) / {max_readable_date}")


def main():
    conn = sqlite3.connect(DB_PATH)
    # Ensure both tables exist (schema.sql uses CREATE ... IF NOT EXISTS, so this
    # is safe whether or not products has already been loaded), then clear only
    # this loader's own table. We deliberately do NOT delete the whole DB file:
    # products lives in the same database and would be wiped along with it.
    conn.executescript(SCHEMA_PATH.read_text())
    conn.execute("DELETE FROM reviews")
    # AUTOINCREMENT keeps a counter in sqlite_sequence that DELETE leaves behind;
    # reset it so review_id restarts at 1, making reloads fully reproducible.
    conn.execute("DELETE FROM sqlite_sequence WHERE name = 'reviews'")
    conn.commit()

    batch = []
    total_loaded = 0

    with DATA_PATH.open(encoding="utf-8") as f:
        for line in f:
            batch.append(parse_record(line))
            if len(batch) >= BATCH_SIZE:
                conn.executemany(INSERT_SQL, batch)
                conn.commit()
                total_loaded += len(batch)
                print(f"Loaded {total_loaded} rows...")
                batch.clear()

    if batch:
        conn.executemany(INSERT_SQL, batch)
        conn.commit()
        total_loaded += len(batch)

    print(f"\nDone. {total_loaded} rows loaded into {DB_PATH}")
    print_sanity_stats(conn)
    conn.close()


if __name__ == "__main__":
    main()

import ast
import gzip
import html
import sqlite3
from pathlib import Path

DB_PATH = Path("data/reviews.db")
SCHEMA_PATH = Path("sql/schema.sql")
DATA_PATH = Path("data/meta_Cell_Phones_and_Accessories.json.gz")
BATCH_SIZE = 5000

INSERT_SQL = """
    INSERT OR REPLACE INTO products (
        asin, title, price, brand, primary_category
    ) VALUES (?, ?, ?, ?, ?)
"""


def clean_text(value):
    # Titles/brands carry HTML entities (e.g. "&amp;" -> "&"). Unescape them, and
    # normalise empty strings to NULL so "no brand" is a real absence, not "".
    if not value:
        return None
    return html.unescape(value)


def primary_category(categories):
    # categories is a list of category paths, e.g.
    # [['Cell Phones & Accessories', 'Cases', 'Basic Cases']]. The most specific,
    # useful label is the last element of the first path. Guard against missing
    # or malformed values.
    if not categories or not categories[0]:
        return None
    return categories[0][-1]


def parse_record(line: str) -> tuple:
    # These 2014 metadata files are Python dict literals (single-quoted), NOT
    # strict JSON, so ast.literal_eval is required instead of json.loads.
    record = ast.literal_eval(line)
    return (
        record["asin"],
        clean_text(record.get("title")),
        record.get("price"),
        clean_text(record.get("brand")),
        primary_category(record.get("categories")),
    )


def print_sanity_stats(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    row_count = cur.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    with_title = cur.execute(
        "SELECT COUNT(*) FROM products WHERE title IS NOT NULL"
    ).fetchone()[0]
    with_price = cur.execute(
        "SELECT COUNT(*) FROM products WHERE price IS NOT NULL"
    ).fetchone()[0]
    with_brand = cur.execute(
        "SELECT COUNT(*) FROM products WHERE brand IS NOT NULL"
    ).fetchone()[0]
    # How many products actually have at least one review (the useful overlap).
    reviewed = cur.execute(
        "SELECT COUNT(*) FROM products p "
        "WHERE EXISTS (SELECT 1 FROM reviews r WHERE r.asin = p.asin)"
    ).fetchone()[0]

    print("\n--- Sanity stats ---")
    print(f"Products loaded:      {row_count}")
    print(f"With title:           {with_title}")
    print(f"With price:           {with_price}")
    print(f"With brand:           {with_brand}")
    print(f"Products with reviews: {reviewed}")


def main():
    conn = sqlite3.connect(DB_PATH)
    # Ensure both tables exist, then clear only the products table. As with
    # load_data.py, we never delete the whole DB file, so the reviews table is
    # left untouched no matter which loader runs, or in what order.
    conn.executescript(SCHEMA_PATH.read_text())
    conn.execute("DELETE FROM products")
    conn.commit()

    batch = []
    total_loaded = 0

    # gzip.open in text mode streams the compressed file line-by-line without
    # decompressing the whole thing to disk first.
    with gzip.open(DATA_PATH, mode="rt", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            batch.append(parse_record(line))
            if len(batch) >= BATCH_SIZE:
                conn.executemany(INSERT_SQL, batch)
                conn.commit()
                total_loaded += len(batch)
                print(f"Loaded {total_loaded} products...")
                batch.clear()

    if batch:
        conn.executemany(INSERT_SQL, batch)
        conn.commit()
        total_loaded += len(batch)

    print(f"\nDone. {total_loaded} products loaded into {DB_PATH}")
    print_sanity_stats(conn)
    conn.close()


if __name__ == "__main__":
    main()

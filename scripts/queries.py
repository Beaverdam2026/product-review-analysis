"""Turn the .sql files in sql/ into pandas DataFrames.

This module is the single place where a .sql file becomes a DataFrame, so query
text stays in sql/ and never gets inlined into Python. Import it from notebooks
and from Quarto .qmd documents alike:

    from queries import run_query
    df = run_query("product_summary")
"""

import sqlite3
from contextlib import closing
from pathlib import Path

import pandas as pd

# Anchor every path to the repo root (this file's grandparent) instead of the
# current working directory. A notebook runs from notebooks/ and Quarto renders
# from the document's own directory, so a relative Path("data/reviews.db") would
# resolve to a different place depending on who called us. __file__ does not move.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "data" / "reviews.db"
SQL_DIR = PROJECT_ROOT / "sql"

# Altair serialises a chart's data into the page as JSON, and so refuses by
# default to render a result with more rows than this (it raises MaxRowsError).
# A result above the limit is a signal to aggregate in SQL - bin, bucket, or
# group - rather than to raise the limit.
ALTAIR_MAX_ROWS = 5000

# One .sql file per analysis question. Deliberately excludes:
#   schema.sql         - DDL, not a query
#   data_profiling.sql - several statements; use run_script() for it
ANALYSIS_QUERIES = (
    "most_helpful_reviews",
    "product_summary",
    "product_trajectory",
    "rating_vs_reviewer_avg",
    "reviewer_summary",
)


def connect() -> sqlite3.Connection:
    """Open data/reviews.db read-only."""
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"{DB_PATH} not found. Build it first:\n"
            "    uv run python scripts/load_data.py\n"
            "    uv run python scripts/load_metadata.py"
        )
    # mode=ro makes the connection read-only, so an analysis notebook can never
    # accidentally write to the database. sqlite3 only accepts that flag through
    # a file: URI, which is what uri=True enables.
    return sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)


def read_sql(name: str) -> str:
    """Return the text of sql/<name>.sql."""
    path = SQL_DIR / f"{name}.sql"
    if not path.exists():
        available = ", ".join(sorted(p.stem for p in SQL_DIR.glob("*.sql")))
        raise FileNotFoundError(f"No such query: {path}\nAvailable: {available}")
    return path.read_text()


def split_statements(sql: str) -> list[str]:
    """Split a multi-statement .sql file into individual statements."""
    statements: list[str] = []
    buffer = ""
    for line in sql.splitlines(keepends=True):
        buffer += line
        # sqlite3.complete_statement() is the stdlib's own SQL-aware check for
        # "does this text end a statement?". It is used instead of sql.split(";")
        # because it knows that a semicolon inside a string literal or a comment
        # does not terminate a statement, which a naive split would get wrong.
        if sqlite3.complete_statement(buffer):
            statements.append(buffer.strip())
            buffer = ""
    # Anything left over is a trailing statement with no final semicolon, or just
    # trailing comments/whitespace. Keep it only if it has real content.
    if buffer.strip():
        statements.append(buffer.strip())
    return statements


def run_query(name: str) -> pd.DataFrame:
    """Run the single-statement query in sql/<name>.sql and return its result."""
    # closing() guarantees the connection is closed. Note that sqlite3's own
    # `with conn:` block commits or rolls back a transaction but does NOT close
    # the connection, which is a common source of leaked handles.
    with closing(connect()) as conn:
        return pd.read_sql_query(read_sql(name), conn)


def run_script(name: str) -> list[pd.DataFrame]:
    """Run every statement in sql/<name>.sql, returning one DataFrame each.

    For files like data_profiling.sql that hold several independent SELECTs.
    run_query() would silently return only the first of them.
    """
    with closing(connect()) as conn:
        return [
            pd.read_sql_query(statement, conn)
            for statement in split_statements(read_sql(name))
        ]

"""Print the shape, dtypes, and first rows of every analysis query result.

Run this before choosing chart types:

    uv run python scripts/inspect_queries.py

Altair will not render a result larger than ALTAIR_MAX_ROWS rows. Any query
flagged as OVER LIMIT below needs to aggregate in SQL before it can be plotted.
"""

import pandas as pd

from queries import ALTAIR_MAX_ROWS, ANALYSIS_QUERIES, run_query, run_script

HEAD_ROWS = 5


def describe(name: str, df: pd.DataFrame) -> bool:
    """Print one query's shape, dtypes, and head. Return True if it is too big."""
    over_limit = len(df) > ALTAIR_MAX_ROWS
    flag = "  <-- OVER LIMIT, aggregate in SQL" if over_limit else ""

    print(f"\n{'=' * 70}")
    print(f"{name}")
    print("=" * 70)
    print(f"rows: {len(df):,}   cols: {len(df.columns)}{flag}")

    print("\ndtypes:")
    for column, dtype in df.dtypes.items():
        null_count = df[column].isna().sum()
        nulls = f"  ({null_count:,} null)" if null_count else ""
        print(f"  {column:<24} {str(dtype):<12}{nulls}")

    print(f"\nhead({HEAD_ROWS}):")
    print(df.head(HEAD_ROWS).to_string(max_colwidth=32))

    return over_limit


def main() -> None:
    # Show every column rather than pandas' default "..." elision.
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 200)

    too_big = []
    for name in ANALYSIS_QUERIES:
        if describe(name, run_query(name)):
            too_big.append(name)

    # data_profiling.sql holds several independent SELECTs, so it needs
    # run_script(). Each statement is a separate one-row integrity check.
    print(f"\n{'=' * 70}")
    print("data_profiling (multi-statement)")
    print("=" * 70)
    for i, df in enumerate(run_script("data_profiling"), start=1):
        print(f"\nstatement {i}:")
        print(df.to_string(index=False))

    print(f"\n{'=' * 70}")
    print("Summary")
    print("=" * 70)
    if too_big:
        print(f"Over Altair's {ALTAIR_MAX_ROWS:,}-row limit:")
        for name in too_big:
            print(f"  - {name}")
        print("\nAggregate these in SQL (bin, bucket, or GROUP BY) before charting.")
    else:
        print(f"All queries are under Altair's {ALTAIR_MAX_ROWS:,}-row limit.")


if __name__ == "__main__":
    main()

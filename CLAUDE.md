# Amazon Reviews Analysis SQL Project

## Working Style
When a tool call (web fetch, search, file read) returns empty, truncated, or error output, explicitly say so before continuing, and do not describe or summarize content you did not actually receive. Distinguish clearly between information you retrieved versus information you recall or infer — if a claim comes from memory rather than a source you just read, say so.

Aim to cite sources and attribute credit. If you are unsure of who to credit, state this. When writing terminal commands and code, explain the basic logic of what the command is doing. If there is an advanced or uncommon aspect of the command, explain in greater detail. 

## Project
SQL-focused portfolio project analyzing Amazon reviews, targeting a data analyst role at Amazon. SQL is the focus (aiming to strengthen window functions and CTEs specifically); Python is for visualizations only. Keep .sql files separate from Python as much as is reasonable.

## Data
McAuley Amazon review dataset, Cell Phones & Accessories 5-core subset (Cell_Phones_and_Accessories_5.json), from a Kaggle re-upload of the Stanford SNAP data. ~194,562 lines. Apache 2.0 license on the Kaggle upload. Required citation (confirmed from the SNAP page): J. McAuley, C. Targett, J. Shi, A. van den Hengel, "Image-based recommendations on styles and substitutes," SIGIR, 2015. Schema is native/unmodified; helpful field is [helpful_votes, total_votes].

## Environment
Fedora laptop + desktop, synced via GitHub over SSH. Python 3.14, SQLite for the database. Using Claude Code with Opus for scaffolding/syntax, writing core analytical queries by hand.

## Division of Labor
Claude handles scaffolding, boilerplate, and syntax verification. Claude does NOT write the core analytical SQL queries (window functions, trajectory analysis) — the user writes these by hand for learning purposes. Reviewing and critiquing the user's queries is encouraged; writing them from scratch is not.

## Structure & Commands
- /sql — one .sql file per question; schema.sql holds the DDL
- /scripts/load_data.py — ingests JSON into data/reviews.db (run: python3 scripts/load_data.py)
- Run a query file: sqlite3 data/reviews.db < sql/filename.sql
- data/ contents are gitignored

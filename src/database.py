
"""SQLite access utilities for the GitSkills dataset."""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

import pandas as pd

from src.config import get_database_path


@contextmanager
def open_database(
    db_path: str | Path | None = None,
) -> Iterator[sqlite3.Connection]:
    """Open a read-only SQLite connection and close it after use."""
    path = Path(db_path) if db_path is not None else get_database_path()
    path = path.expanduser().resolve()

    if not path.is_file():
        raise FileNotFoundError(f"Database not found: {path}")

    conn = sqlite3.connect(
        f"{path.as_uri()}?mode=ro",
        uri=True,
    )

    try:
        yield conn
    finally:
        conn.close()


def query_dataframe(
    sql: str,
    params: tuple = (),
    db_path: str | Path | None = None,
) -> pd.DataFrame:
    """Execute a SQL query and return the result as a DataFrame."""
    with open_database(db_path) as conn:
        return pd.read_sql_query(sql, conn, params=params)


def list_tables(
    db_path: str | Path | None = None,
) -> list[str]:
    """Return the names of user-defined database tables."""
    result = query_dataframe(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
          AND name NOT LIKE 'sqlite_%'
        ORDER BY name
        """,
        db_path=db_path,
    )

    return result["name"].tolist()

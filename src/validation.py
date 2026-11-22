
"""Data integrity checks for the GitSkills sample."""

import hashlib
import sqlite3

import pandas as pd

from src.database import open_database


def git_blob_sha1(content: bytes) -> str:
    """Compute the Git blob SHA-1 hash of a byte sequence."""
    header = f"blob {len(content)}\0".encode("ascii")
    return hashlib.sha1(header + content).hexdigest()


def validate_primary_hashes(
    conn: sqlite3.Connection,
) -> dict:
    """Check primary content hashes against their stored text."""
    frame = pd.read_sql_query(
        """
        SELECT file_sha, content
        FROM artifacts
        WHERE dedup_primary = 1
          AND content_fetched = 1
        """,
        conn,
    )

    checked = 0
    mismatches = 0
    missing_content = 0

    for row in frame.itertuples(index=False):
        if row.content is None:
            missing_content += 1
            continue

        content = row.content
        if isinstance(content, str):
            content = content.encode("utf-8")

        actual_sha = git_blob_sha1(content)

        checked += 1
        if actual_sha.lower() != row.file_sha.lower():
            mismatches += 1

    return {
        "Primary records checked": checked,
        "Hash mismatches": mismatches,
        "Missing content": missing_content,
    }


def validate_sample(
    conn: sqlite3.Connection,
) -> dict:
    """Check key sample counts and primary-representative uniqueness."""
    frame = pd.read_sql_query(
        """
        SELECT repo_full_name, file_sha, dedup_primary
        FROM artifacts
        """,
        conn,
    )

    primary = frame.loc[frame["dedup_primary"] == 1]

    return {
        "Artifact occurrences": int(len(frame)),
        "Repositories": int(frame["repo_full_name"].nunique()),
        "Unique hashes": int(frame["file_sha"].nunique()),
        "Primary representatives": int(len(primary)),
        "Unique primary hashes": int(primary["file_sha"].nunique()),
        "Missing repository names": int(frame["repo_full_name"].isna().sum()),
        "Missing hashes": int(frame["file_sha"].isna().sum()),
        "One primary per hash": bool(
            len(primary) == frame["file_sha"].nunique()
            and primary["file_sha"].is_unique
        ),
    }


def run_validation() -> dict:
    """Run the main sample and content-integrity checks."""
    with open_database() as conn:
        sample = validate_sample(conn)
        hashes = validate_primary_hashes(conn)

    return {
        "sample": sample,
        "hashes": hashes,
    }

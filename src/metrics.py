
"""Metrics for the GitSkills repository-mining study."""

import pandas as pd


def calculate_overlap(frame: pd.DataFrame) -> dict:
    """Calculate exact-content reuse across repositories.

    Each row represents one artifact occurrence. Artifacts are
    grouped by their Git blob SHA-1 content hash.

    A hash is considered shared when it occurs in at least two
    distinct repositories, regardless of how many copies appear
    within an individual repository.
    """
    required = {"repo_full_name", "file_sha"}
    missing = required - set(frame.columns)

    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    if frame.empty:
        raise ValueError("Cannot calculate overlap on an empty population")

    if frame[["repo_full_name", "file_sha"]].isna().any().any():
        raise ValueError("Repository names and content hashes must not be null")

    groups = frame.groupby("file_sha").agg(
        occurrences=("repo_full_name", "size"),
        repositories=("repo_full_name", "nunique"),
    )

    shared = groups["repositories"] >= 2
    shared_hashes = int(shared.sum())
    shared_occurrences = int(groups.loc[shared, "occurrences"].sum())

    return {
        "Repositories": int(frame["repo_full_name"].nunique()),
        "Artifacts": int(len(frame)),
        "Unique hashes": int(len(groups)),
        "Shared hashes": shared_hashes,
        "Shared hashes (%)": 100 * shared_hashes / len(groups),
        "Artifacts with shared content": shared_occurrences,
        "Artifact overlap (%)": 100 * shared_occurrences / len(frame),
    }


def summarize_numeric(
    values: pd.Series,
) -> dict:
    """Summarize a numeric attribute using nonmissing observations."""
    numeric = pd.to_numeric(values, errors="coerce").dropna()

    if numeric.empty:
        raise ValueError("No valid numeric observations")

    return {
        "count": int(len(numeric)),
        "mean": float(numeric.mean()),
        "median": float(numeric.median()),
        "std": float(numeric.std()),
        "min": float(numeric.min()),
        "p90": float(numeric.quantile(0.90)),
        "max": float(numeric.max()),
    }


def percentage(
    numerator: int | float,
    denominator: int | float,
) -> float:
    """Calculate a percentage without rounding."""
    if denominator <= 0:
        raise ValueError("Denominator must be positive")

    return 100.0 * numerator / denominator

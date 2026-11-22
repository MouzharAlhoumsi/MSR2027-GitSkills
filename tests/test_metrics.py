
"""Unit tests for the GitSkills analysis metrics."""

import pandas as pd
import pytest

from src.metrics import calculate_overlap, percentage, summarize_numeric


def test_overlap_with_shared_content():
    """Count reuse across distinct repositories."""
    artifacts = pd.DataFrame(
        {
            "repo_full_name": [
                "org/repo-a",
                "org/repo-a",
                "org/repo-b",
                "org/repo-c",
                "org/repo-c",
            ],
            "file_sha": [
                "hash-a",
                "hash-a",
                "hash-a",
                "hash-b",
                "hash-c",
            ],
        }
    )

    result = calculate_overlap(artifacts)

    assert result["Repositories"] == 3
    assert result["Artifacts"] == 5
    assert result["Unique hashes"] == 3
    assert result["Shared hashes"] == 1
    assert result["Shared hashes (%)"] == pytest.approx(100 / 3)
    assert result["Artifacts with shared content"] == 3
    assert result["Artifact overlap (%)"] == pytest.approx(60.0)


def test_repeated_content_in_one_repository_is_not_shared():
    """Repeated files within one repository do not imply cross-repo reuse."""
    artifacts = pd.DataFrame(
        {
            "repo_full_name": [
                "org/repo-a",
                "org/repo-a",
                "org/repo-a",
            ],
            "file_sha": ["hash-a", "hash-a", "hash-b"],
        }
    )

    result = calculate_overlap(artifacts)

    assert result["Repositories"] == 1
    assert result["Artifacts"] == 3
    assert result["Unique hashes"] == 2
    assert result["Shared hashes"] == 0
    assert result["Artifacts with shared content"] == 0
    assert result["Artifact overlap (%)"] == 0.0


def test_overlap_rejects_missing_columns():
    """Required repository and hash columns must be present."""
    artifacts = pd.DataFrame({"file_sha": ["hash-a"]})

    with pytest.raises(ValueError, match="Missing required columns"):
        calculate_overlap(artifacts)


def test_overlap_rejects_empty_population():
    """Overlap is undefined for an empty artifact population."""
    artifacts = pd.DataFrame(columns=["repo_full_name", "file_sha"])

    with pytest.raises(ValueError, match="empty population"):
        calculate_overlap(artifacts)


def test_overlap_rejects_null_identifiers():
    """Missing repository or content identifiers are not accepted."""
    artifacts = pd.DataFrame(
        {
            "repo_full_name": ["org/repo-a", None],
            "file_sha": ["hash-a", "hash-b"],
        }
    )

    with pytest.raises(ValueError, match="must not be null"):
        calculate_overlap(artifacts)


def test_numeric_summary():
    """Numeric summaries exclude missing values."""
    values = pd.Series([10, 20, 30, None])

    result = summarize_numeric(values)

    assert result["count"] == 3
    assert result["mean"] == pytest.approx(20.0)
    assert result["median"] == pytest.approx(20.0)
    assert result["min"] == 10
    assert result["max"] == 30
    assert result["p90"] == pytest.approx(28.0)


def test_percentage():
    """Percentages are calculated without premature rounding."""
    assert percentage(1, 4) == pytest.approx(25.0)
    assert percentage(2, 3) == pytest.approx(66.6666666667)


def test_percentage_rejects_zero_denominator():
    """A percentage requires a positive denominator."""
    with pytest.raises(ValueError, match="Denominator must be positive"):
        percentage(5, 0)

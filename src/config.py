
"""Paths and configuration for the GitSkills research project."""

from pathlib import Path


# Project directory (the parent of src/).
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Dataset location.
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
DB_PATH = RAW_DATA_DIR / "agent_skills_sample.db"

# Output directories.
FIGURES_DIR = PROJECT_ROOT / "figures"
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"


def get_database_path() -> Path:
    """Return the SQLite database path, checking that it exists."""
    if not DB_PATH.is_file():
        raise FileNotFoundError(
            f"GitSkills database not found: {DB_PATH}\n"
            "Place agent_skills_sample.db in data/raw/."
        )

    return DB_PATH


def ensure_figures_dir() -> Path:
    """Create the figures directory if needed and return its path."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    return FIGURES_DIR

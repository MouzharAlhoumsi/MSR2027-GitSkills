
"""Plotting utilities for the GitSkills research figures."""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from src.config import ensure_figures_dir


def save_figure(
    fig: Figure,
    filename: str,
    output_dir: str | Path | None = None,
    dpi: int = 300,
) -> tuple[Path, Path]:
    """Save a Matplotlib figure in PDF and PNG formats."""
    if not filename or Path(filename).name != filename:
        raise ValueError("filename must be a simple file name")

    stem = Path(filename).stem
    if not stem or stem in {".", ".."}:
        raise ValueError("filename must have a valid name")

    directory = (
        Path(output_dir)
        if output_dir is not None
        else ensure_figures_dir()
    )
    directory.mkdir(parents=True, exist_ok=True)

    pdf_path = directory / f"{stem}.pdf"
    png_path = directory / f"{stem}.png"

    fig.savefig(pdf_path, bbox_inches="tight")
    fig.savefig(png_path, dpi=dpi, bbox_inches="tight")

    return pdf_path, png_path


def close_figure(fig: Figure) -> None:
    """Close a Matplotlib figure to release resources."""
    plt.close(fig)

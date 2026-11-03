"""Reusable plot classes for the analysis scripts."""

import logging
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

logger = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[1]


class Barplot:
    """Create and save a bar plot from a dataframe."""

    def __init__(self, output_dir: Path | None = None) -> None:
        self.output_dir = output_dir or ROOT / "data" / "processed" / "plots"

    def plot(
        self,
        data: pd.DataFrame,
        *,
        x: str,
        y: str,
        filename: str,
        title: str,
        xlabel: str | None = None,
        ylabel: str | None = None,
    ) -> Path:
        """Save a bar plot and return its path."""
        if data.empty:
            raise ValueError("Cannot create a bar plot from an empty dataframe.")
        missing_columns = {x, y} - set(data.columns)
        if missing_columns:
            raise ValueError(f"Missing plot columns: {sorted(missing_columns)}")

        self.output_dir.mkdir(parents=True, exist_ok=True)
        output_path = self.output_dir / filename
        figure, axis = plt.subplots(figsize=(10, 6))
        try:
            sns.barplot(data=data, x=x, y=y, ax=axis)
            axis.set(title=title, xlabel=xlabel or x, ylabel=ylabel or y)
            axis.tick_params(axis="x", labelrotation=35)
            figure.tight_layout()
            figure.savefig(output_path, dpi=150)
        finally:
            plt.close(figure)

        logger.info("Saved bar plot to %s", output_path)
        return output_path

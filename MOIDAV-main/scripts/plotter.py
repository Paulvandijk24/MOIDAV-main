"""Reusable plot classes for the analysis scripts."""

import logging
from pathlib import Path
from typing import Literal

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

logger = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "output"
PLOTS_DIR = OUTPUT_DIR / "plots"
TABLES_DIR = OUTPUT_DIR / "tabellen"


class Barplot:
    """Create and save a bar plot from a dataframe."""

    def __init__(self, output_dir: Path | None = None) -> None:
        self.output_dir = output_dir or PLOTS_DIR
        if output_dir is None:
            TABLES_DIR.mkdir(parents=True, exist_ok=True)

    def save_plot(
        self,
        data: pd.DataFrame,
        *,
        x: str,
        y: str,
        filename: str,
        title: str,
        xlabel: str | None = None,
        ylabel: str | None = None,
        yerr: str | None = None,
        colors: list[str] | None = None,
        figsize: tuple[float, float] = (10, 6),
        bar_labels: bool = False,
        show_y_axis: bool = True,
        y_limit: tuple[float, float] | None = None,
        axes_position: tuple[float, float, float, float] | None = None,
        caption: str | None = None,
        x_rotation: float = 35,
        tight_layout: bool = True,
    ) -> Path:
        """Save a bar plot and return its path."""
        if data.empty:
            raise ValueError("Cannot create a bar plot from an empty dataframe.")
        required_columns = {x, y}
        if yerr is not None:
            required_columns.add(yerr)
        missing_columns = required_columns - set(data.columns)
        if missing_columns:
            raise ValueError(f"Missing plot columns: {sorted(missing_columns)}")
        if colors is not None and len(colors) != len(data):
            raise ValueError("The number of bar colors must match the number of rows.")

        self.output_dir.mkdir(parents=True, exist_ok=True)
        output_path = self.output_dir / filename
        figure, axis = plt.subplots(figsize=figsize)
        try:
            if yerr is None and colors is None and not bar_labels:
                sns.barplot(data=data, x=x, y=y, ax=axis)
            else:
                bars = axis.bar(
                    data[x].astype(str),
                    data[y].to_numpy(),
                    yerr=data[yerr].to_numpy() if yerr is not None else None,
                    capsize=6 if yerr is not None else 0,
                    color=colors,
                    edgecolor="black" if colors is not None else None,
                )
                if bar_labels:
                    for bar, value in zip(bars, data[y]):
                        axis.text(
                            bar.get_x() + bar.get_width() / 2,
                            bar.get_height() / 2,
                            f"{value:.1f}%",
                            ha="center",
                            va="center",
                            color="white" if value > 0 else "black",
                            fontweight="bold",
                        )
            axis.set(
                title=title,
                xlabel=xlabel if xlabel is not None else x,
                ylabel=ylabel if ylabel is not None else y,
            )
            axis.tick_params(axis="x", labelrotation=x_rotation)
            if not show_y_axis:
                axis.yaxis.set_visible(False)
            if y_limit is not None:
                axis.set_ylim(*y_limit)
            if caption is not None:
                axis.text(
                    0.5,
                    -0.1,
                    caption,
                    transform=axis.transAxes,
                    ha="center",
                    va="top",
                    fontsize=9,
                    color="#4d4d4d",
                    wrap=True,
                )
            if tight_layout:
                figure.tight_layout()
            if axes_position is not None:
                axis.set_position(axes_position)
            figure.savefig(output_path, dpi=150)
        finally:
            plt.close(figure)

        logger.info("Saved bar plot to %s", output_path)
        return output_path

    plot = save_plot


class Plotter:
    """Save an already constructed Matplotlib figure."""

    def __init__(self, output_dir: Path | None = None) -> None:
        self.output_dir = output_dir or PLOTS_DIR

    def save_figure(
        self,
        figure: plt.Figure,
        *,
        filename: str,
        dpi: int = 150,
        bbox_inches: Literal["tight"] | None = "tight",
    ) -> Path:
        """Save a figure and return its path."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        output_path = self.output_dir / filename
        figure.savefig(output_path, dpi=dpi, bbox_inches=bbox_inches)
        logger.info("Saved plot to %s", output_path)
        return output_path

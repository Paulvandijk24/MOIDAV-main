"""Entry point for the upcoming category-comparison analysis."""

import logging

import pandas as pd

from scripts.plotter import Barplot

logger = logging.getLogger(__name__)


class ComparingCategories:
    """Compare average message lengths across author categories."""

    def __init__(self, messages: pd.DataFrame) -> None:
        summary = (
            messages.groupby("author_gender", observed=True)["message_length"]
            .mean()
            .rename("average_message_length")
            .reset_index()
        )
        self.plot_path = Barplot().plot(
            summary,
            x="author_gender",
            y="average_message_length",
            filename="comparing_categories.png",
            title="Average message length by author category",
            ylabel="Average message length",
        )

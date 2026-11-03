"""Summarize a simple author-by-message-count dimension."""

import pandas as pd

from scripts.plotter import Barplot


class DimensionModel:
    """Plot the ten most active authors by message count."""

    def __init__(self, messages: pd.DataFrame) -> None:
        authors = (
            messages.groupby("author")
            .size()
            .nlargest(10)
            .rename("message_count")
            .reset_index()
            .sort_values("message_count")
        )
        self.plot_path = Barplot().plot(
            authors,
            x="author",
            y="message_count",
            filename="dimension_model.png",
            title="Ten most active authors",
            ylabel="Number of messages",
        )

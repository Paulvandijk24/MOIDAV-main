"""Explore the relationship between message length and word count."""

import pandas as pd

from scripts.plotter import Barplot


class Relationship:
    """Plot average character length for message word-count groups."""

    def __init__(self, messages: pd.DataFrame) -> None:
        word_bins = [0, 1, 2, 3, 5, 10, 20, 50, float("inf")]
        grouped = messages.assign(
            word_count_group=pd.cut(
                messages["word_count"],
                bins=word_bins,
                right=False,
                include_lowest=True,
            )
        )
        relationship = (
            grouped.groupby("word_count_group", observed=True)["message_length"]
            .mean()
            .rename("average_message_length")
            .reset_index()
        )
        relationship["word_count_group"] = relationship["word_count_group"].astype(str)
        self.plot_path = Barplot().plot(
            relationship,
            x="word_count_group",
            y="average_message_length",
            filename="relationship.png",
            title="Message length by word-count group",
            xlabel="Word-count group",
            ylabel="Average message length (characters)",
        )

"""Summarize the distribution of message lengths."""

import pandas as pd

from scripts.plotter import Barplot


class Distribution:
    """Plot message counts in message-length bins."""

    def __init__(self, messages: pd.DataFrame) -> None:
        lengths = messages["message_length"]
        bin_width = 20
        bins = range(0, ((int(lengths.max()) // bin_width) + 2) * bin_width, bin_width)
        binned = messages.assign(
            length_bin=pd.cut(lengths, bins=bins, right=False, include_lowest=True)
        )
        counts = (
            binned.groupby("length_bin", observed=True)
            .size()
            .rename("message_count")
            .reset_index()
        )
        counts["length_bin"] = counts["length_bin"].astype(str)
        self.plot_path = Barplot().plot(
            counts,
            x="length_bin",
            y="message_count",
            filename="distribution.png",
            title="Distribution of message lengths",
            xlabel="Message length (characters)",
            ylabel="Number of messages",
        )

"""Summarize message activity over time."""

import pandas as pd

from scripts.plotter import Barplot


class TimeSeries:
    """Plot the monthly number of messages."""

    def __init__(self, messages: pd.DataFrame) -> None:
        monthly = (
            messages.assign(month=messages["timestamp"].dt.strftime("%Y-%m"))
            .groupby("month")
            .size()
            .rename("message_count")
            .reset_index()
        )
        self.plot_path = Barplot().plot(
            monthly,
            x="month",
            y="message_count",
            filename="time_series.png",
            title="Messages per month",
            ylabel="Number of messages",
        )

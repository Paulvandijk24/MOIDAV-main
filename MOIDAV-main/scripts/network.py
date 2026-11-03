"""Build a lightweight network from consecutive message authors."""

import pandas as pd

from scripts.plotter import Barplot


class Network:
    """Plot authors' weighted connections to adjacent message authors."""

    def __init__(self, messages: pd.DataFrame) -> None:
        ordered = messages.sort_values("timestamp")
        transitions = pd.DataFrame(
            {
                "source": ordered["author"].iloc[:-1].to_numpy(),
                "target": ordered["author"].iloc[1:].to_numpy(),
            }
        )
        transitions = transitions[transitions["source"] != transitions["target"]]
        edges = transitions.groupby(["source", "target"]).size().rename("weight")
        activity = (
            pd.concat(
                [
                    edges.groupby(level="source").sum(),
                    edges.groupby(level="target").sum(),
                ]
            )
            .groupby(level=0)
            .sum()
        )
        nodes = (
            activity.nlargest(10)
            .rename_axis("author")
            .rename("weighted_connections")
            .reset_index()
            .sort_values("weighted_connections")
        )
        self.plot_path = Barplot().plot(
            nodes,
            x="author",
            y="weighted_connections",
            filename="network.png",
            title="Authors with the most adjacent-message connections",
            ylabel="Weighted connections",
        )

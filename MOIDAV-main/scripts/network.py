"""Plot the notebook's declared author relationships and chat interactions."""

from itertools import combinations
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

from scripts.plotter import Plotter

CONNECTION_ALIASES = {
    "Thijs": "Thijsje",
    "Vincent": "Vincent Kruithof",
}
CONNECTION_GROUPS = {
    "basisschool": [["Paul", "Tim Wapenaar", "Rüberhaupt", "Rik", "Kevin", "Joel"]],
    "middelbare_school": [
        [
            "Rheno",
            "Rüberhaupt",
            "Thijs",
            "Vincent",
            "Schwéhn",
            "Ijsie",
            "Rik",
            "Vincent Kruithof",
        ],
        ["Joel", "Tim Wapenaar", "Kevin", "Nick"],
    ],
    "korfbal": [["Thijs", "Paul", "Joel"]],
    "werk": [
        ["Rheno", "Schwéhn", "Ijsie", "Rüberhaupt", "Marijn"],
        ["Vincent", "Joel"],
        ["Paul", "Kevin"],
        ["Rüberhaupt", "Nick"],
    ],
}
HIDDEN_WORK_CONNECTIONS = {
    frozenset(("Nick", "Rüberhaupt")),
    frozenset(("Vincent Kruithof", "Joel")),
    frozenset(("Marijn", "Ijsie")),
}
HIDDEN_SCHOOL_CONNECTIONS = {
    frozenset(("Rik", "Thijsje")),
    frozenset(("Rik", "Vincent Kruithof")),
    frozenset(("Rik", "Ijsie")),
    frozenset(("Rik", "Schwéhn")),
    frozenset(("Rik", "Rheno")),
}


class Network:
    """Create the relationship and interaction plot from notebook cell 36."""

    def __init__(self, messages: pd.DataFrame) -> None:
        missing_columns = {"timestamp", "author"} - set(messages.columns)
        if missing_columns:
            raise ValueError(f"Missing network columns: {sorted(missing_columns)}")
        authors = sorted(messages["author"].dropna().unique(), key=str.casefold)
        author_by_casefold = {author.casefold(): author for author in authors}

        def resolve_author(name: str) -> str:
            canonical = CONNECTION_ALIASES.get(name, name)
            resolved = author_by_casefold.get(canonical.casefold())
            if resolved is None:
                raise ValueError(f"Unknown chat author in connection groups: {name!r}")
            return resolved

        connection_groups = {
            relation: [
                sorted({resolve_author(name) for name in members}, key=str.casefold)
                for members in groups
            ]
            for relation, groups in CONNECTION_GROUPS.items()
        }
        combined_connections = nx.Graph()
        combined_connections.add_nodes_from(authors)
        for relation, groups in connection_groups.items():
            for members in groups:
                for author_a, author_b in combinations(members, 2):
                    if combined_connections.has_edge(author_a, author_b):
                        combined_connections[author_a][author_b]["relations"].add(
                            relation
                        )
                    else:
                        combined_connections.add_edge(
                            author_a, author_b, relations={relation}
                        )

        for _, _, attributes in combined_connections.edges(data=True):
            relation_distances = {
                "basisschool": 1,
                "middelbare_school": 2,
                "korfbal": 1,
                "werk": 4,
            }
            shortest_distance = min(
                relation_distances[relation] for relation in attributes["relations"]
            )
            attributes["distance_cm"] = shortest_distance / len(attributes["relations"])

        plot_connections = combined_connections.copy()
        for author_a, author_b, attributes in list(plot_connections.edges(data=True)):
            pair = frozenset((author_a, author_b))
            if (
                pair in HIDDEN_WORK_CONNECTIONS and attributes["relations"] == {"werk"}
            ) or (
                pair in HIDDEN_SCHOOL_CONNECTIONS
                and attributes["relations"] == {"middelbare_school"}
            ):
                plot_connections.remove_edge(author_a, author_b)

        path_distances = dict(nx.floyd_warshall(plot_connections, weight="distance_cm"))
        positions = nx.kamada_kawai_layout(
            plot_connections,
            dist=path_distances,
            weight="distance_cm",
        )
        central_author = resolve_author("Rüberhaupt")
        central_position = positions[central_author].copy()
        positions = {
            author: position - central_position
            for author, position in positions.items()
        }

        self.plot_path = self._plot(
            messages, plot_connections, positions, central_author
        )

    @staticmethod
    def _plot(
        messages: pd.DataFrame,
        graph: nx.Graph,
        positions: dict[str, np.ndarray],
        central_author: str,
    ) -> Path:
        ordered_messages = (
            messages.dropna(subset=["timestamp", "author"])
            .sort_values("timestamp", kind="stable")
            .reset_index(drop=True)
            .copy()
        )
        message_gaps = ordered_messages["timestamp"].diff()
        new_session = message_gaps.isna() | (message_gaps > pd.Timedelta(minutes=60))
        ordered_messages["session_id"] = new_session.cumsum() - 1
        ordered_messages["previous_author"] = ordered_messages.groupby("session_id")[
            "author"
        ].shift()
        author_changes = ordered_messages.loc[
            ordered_messages["previous_author"].notna()
            & ordered_messages["author"].ne(ordered_messages["previous_author"]),
            ["previous_author", "author"],
        ]
        interaction_counts: dict[tuple[str, str], int] = {}
        for previous, current in author_changes.itertuples(index=False, name=None):
            pair_values = sorted((str(previous), str(current)), key=str.casefold)
            pair = (pair_values[0], pair_values[1])
            interaction_counts[pair] = interaction_counts.get(pair, 0) + 1

        maximum_interactions = max(
            (
                interaction_counts.get(tuple(sorted(edge, key=str.casefold)), 0)
                for edge in graph.edges()
            ),
            default=1,
        )

        figure, axis = plt.subplots(figsize=(13, 10))
        try:
            distance_colors = {
                "kort": "#2ca25f",
                "middel": "#3182bd",
                "lang": "#de2d26",
            }
            distance_labels = {
                "kort": "kort (≤ 1 cm)",
                "middel": "middel (≤ 2 cm)",
                "lang": "lang (> 2 cm)",
            }
            for author_a, author_b, attributes in graph.edges(data=True):
                distance = attributes["distance_cm"]
                distance_group = (
                    "kort" if distance <= 1 else "middel" if distance <= 2 else "lang"
                )
                nx.draw_networkx_edges(
                    graph,
                    positions,
                    edgelist=[(author_a, author_b)],
                    ax=axis,
                    edge_color=distance_colors[distance_group],
                    width=1.8,
                    alpha=0.7,
                )

            nx.draw_networkx_nodes(
                graph,
                positions,
                ax=axis,
                node_size=760,
                node_color=[
                    "#f4a261" if author == central_author else "#dbe8f2"
                    for author in graph
                ],
                edgecolors="#34495e",
                linewidths=1.0,
            )
            nx.draw_networkx_labels(graph, positions, ax=axis, font_size=9)
            axis.legend(
                handles=[
                    Line2D(
                        [0],
                        [0],
                        color=color,
                        linewidth=2,
                        label=distance_labels[label],
                    )
                    for label, color in distance_colors.items()
                ],
                title="Effectieve doelafstand",
                loc="upper left",
                frameon=False,
            )
            axis.set_title("Van oprichter naar stille vennoot.", fontsize=16, pad=24)
            caption = (
                "Auteur 9 bracht de groep bij elkaar, maar is niet de actiefste vriend"
            )
            axis.text(
                0.5,
                1.02,
                caption,
                transform=axis.transAxes,
                ha="center",
                va="bottom",
                fontsize=11,
            )
            axis.set_aspect("equal")
            layout_extent = max(
                np.max(np.abs(np.concatenate(list(positions.values())))) * 1.1,
                1.0,
            )
            axis.set_xlim(-layout_extent, layout_extent)
            axis.set_ylim(-layout_extent, layout_extent)
            axis.set_axis_off()
            figure.tight_layout(rect=(0, 0, 1, 0.94))

            distance_legend = axis.get_legend()
            if distance_legend is None:
                raise RuntimeError("The distance legend was not created.")
            distance_legend.remove()
            edge_collections = axis.collections[: graph.number_of_edges()]
            for (author_a, author_b), edge_artist in zip(
                graph.edges(), edge_collections, strict=True
            ):
                pair = tuple(sorted((author_a, author_b), key=str.casefold))
                interactions = interaction_counts.get(pair, 0)
                edge_artist.set_color("#2ca25f" if interactions >= 500 else "#777777")
                edge_artist.set_linewidth(
                    0.6 + 4.4 * np.sqrt(interactions / maximum_interactions)
                )

            node_collection = axis.collections[graph.number_of_edges()]
            node_collection.set_facecolor("#dbe8f2")
            for label in axis.texts:
                label.remove()
            author_numbers = {
                author: str(number)
                for number, author in enumerate(
                    sorted(graph.nodes(), key=str.casefold), start=1
                )
            }
            nx.draw_networkx_labels(
                graph,
                positions,
                labels=author_numbers,
                ax=axis,
                font_size=10,
                font_weight="bold",
            )
            axis.text(
                0.5,
                1.02,
                caption,
                transform=axis.transAxes,
                ha="center",
                va="bottom",
                fontsize=11,
            )
            interaction_legend = axis.legend(
                handles=[
                    Line2D(
                        [0],
                        [0],
                        color="#777777",
                        linewidth=0.6 + 4.4 * np.sqrt(value / maximum_interactions),
                        label=f"{value:,} interacties",
                    )
                    for value in sorted(
                        {
                            int(round(maximum_interactions / 2)),
                            maximum_interactions,
                        }
                    )
                ]
                + [
                    Line2D(
                        [0],
                        [0],
                        color="#2ca25f",
                        linewidth=2,
                        label="≥500 interacties (groen)",
                    )
                ],
                title="Lijndikte: interacties per auteurs-paar",
                loc="upper right",
                frameon=False,
            )
            axis.add_artist(interaction_legend)
            return Plotter().save_figure(
                figure,
                filename="network.png",
                dpi=100,
                bbox_inches=None,
            )
        finally:
            plt.close(figure)

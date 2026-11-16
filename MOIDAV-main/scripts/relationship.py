"""Plot yearly chat volume against the share of congratulation messages."""

import logging
import re

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from scripts.plotter import Plotter

logger = logging.getLogger(__name__)

CONGRATULATION_PATTERNS = (
    r"\bgefeliciteerd\b",
    r"\bgefeliciflapstaart\b",
    r"\bgefeli\w*\b",
    r"\bcongr(?:atz|ats?)\b",
    r"\bcongratulations?\b",
    r"\bsuper\b",
    r"\bvier\w*\b",
    r"\bsucces\w*\b",
    r"\bgewonnen\b",
    r"\bgeslaagd\b",
)


class Relationship:
    """Recreate the notebook's annual volume and congratulation-rate plot."""

    def __init__(self, messages: pd.DataFrame) -> None:
        missing_columns = {"timestamp", "message"} - set(messages.columns)
        if missing_columns:
            raise ValueError(f"Missing relationship columns: {sorted(missing_columns)}")

        timestamped = messages.loc[messages["timestamp"].notna()].copy()
        if timestamped.empty:
            raise ValueError("The chat contains no timestamped messages.")

        patterns = tuple(
            re.compile(pattern, flags=re.IGNORECASE)
            for pattern in CONGRATULATION_PATTERNS
        )
        timestamped["is_congratulation_match"] = timestamped["message"].map(
            lambda message: any(
                pattern.search(str(message))
                for pattern in patterns
                if not pd.isna(message)
            )
        )
        timestamped["year"] = timestamped["timestamp"].dt.year
        timestamped["date_utc"] = timestamped["timestamp"].dt.normalize()
        yearly_congratulations = timestamped.groupby("year").agg(
            total_messages=("message", "size"),
            congratulation_messages=("is_congratulation_match", "sum"),
        )
        yearly_congratulations["percentage"] = (
            100
            * yearly_congratulations["congratulation_messages"]
            / yearly_congratulations["total_messages"]
        )
        yearly_congratulations["coverage_note"] = "binnen waargenomen exportdekking"

        first_timestamp = timestamped["timestamp"].min()
        last_timestamp = timestamped["timestamp"].max()
        first_year = int(first_timestamp.year)
        last_year = int(last_timestamp.year)
        if first_timestamp.month != 1 or first_timestamp.day != 1:
            yearly_congratulations.loc[first_year, "coverage_note"] = (
                "randjaar: waargenomen dekking begint na 1 januari"
            )
        if last_timestamp.month != 12 or last_timestamp.day != 31:
            note = "randjaar: waargenomen dekking eindigt vóór 31 december"
            if (
                last_year == first_year
                and "randjaar" in yearly_congratulations.loc[last_year, "coverage_note"]
            ):
                note = (
                    "randjaar: waargenomen dekking begint/eindigt binnen kalenderjaar"
                )
            yearly_congratulations.loc[last_year, "coverage_note"] = note

        annual_plot_data = yearly_congratulations.copy()
        annual_plot_data["partial_year"] = annual_plot_data[
            "coverage_note"
        ].str.contains("randjaar", case=False, na=False)
        plot_data = annual_plot_data.loc[annual_plot_data.index != 2017].copy()
        if len(plot_data) < 3:
            raise ValueError("Een order-2 fit vereist minimaal drie jaarpunten.")

        quadratic_coefficients = np.polyfit(
            plot_data["total_messages"], plot_data["percentage"], deg=2
        )
        quadratic_fit = np.poly1d(quadratic_coefficients)
        fit_x = np.linspace(
            plot_data["total_messages"].min(),
            plot_data["total_messages"].max(),
            200,
        )
        fit_y = quadratic_fit(fit_x)

        figure, axis = plt.subplots(figsize=(9, 6))
        try:
            for _, group in plot_data.groupby("partial_year"):
                axis.scatter(
                    group["total_messages"],
                    group["percentage"],
                    color="#4c78a8",
                    marker="o",
                    s=75,
                    alpha=0.85,
                )
                for year, row in group.iterrows():
                    axis.annotate(
                        str(year),
                        (row["total_messages"], row["percentage"]),
                        xytext=(5, 4),
                        textcoords="offset points",
                        fontsize=9,
                    )

            axis.plot(
                fit_x,
                fit_y,
                color="crimson",
                linewidth=2,
                label="Kwadratische fit (orde 2)",
            )
            arrow_start_x = fit_x[int(0.7 * (len(fit_x) - 1))]
            arrow_end_x = fit_x[int(0.55 * (len(fit_x) - 1))]
            axis.annotate(
                "",
                xy=(arrow_end_x, quadratic_fit(arrow_end_x)),
                xytext=(arrow_start_x, quadratic_fit(arrow_start_x)),
                arrowprops={"arrowstyle": "->", "color": "crimson", "linewidth": 2},
            )
            axis.set_xlabel("Aantal berichten")
            axis.set_ylabel("Percentage felicitatieberichten")
            axis.set_title(
                "De chat wordt met de jaren meer gebruikt als plek voor felicitaties"
            )
            axis.legend()
            figure.tight_layout()
            self.plot_path = Plotter().save_figure(
                figure, filename="relationship.png", dpi=100
            )
        finally:
            plt.close(figure)

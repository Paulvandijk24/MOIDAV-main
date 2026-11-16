"""Recreate the Squad time-features notebook's message-length trend plot."""

import logging

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from goad_toolkit.analytics import NullDistribution

from scripts.plotter import Plotter

logger = logging.getLogger(__name__)


class TimeSeries:
    """Plot monthly and smoothed message lengths with piecewise trends."""

    def __init__(self, messages: pd.DataFrame) -> None:
        monthly_message_length = (
            messages.assign(
                month=messages["timestamp"].dt.to_period("M").dt.to_timestamp()
            )
            .groupby("month", as_index=False)
            .agg(average_length=("message_length", "mean"))
            .sort_values("month")
        )
        monthly_message_length["period"] = np.where(
            monthly_message_length["month"] < pd.Timestamp("2020-06-01"),
            "Voor",
            "Na",
        )

        def mean_length_difference(data: pd.DataFrame) -> float:
            means = data.groupby("period")["average_length"].mean()
            return means["Na"] - means["Voor"]

        mean_length_null = NullDistribution(
            mean_length_difference, n_iter=10_000, seed=42
        ).run(monthly_message_length, label="period")
        logger.info(
            f"Gemiddeld verschil (Na − Voor): {mean_length_null.observed:.2f} tekens; "
            f"eenzijdige p-waarde: {mean_length_null.p_value('greater'):.5f}"
        )

        def maximum_ecdf_distance(data: pd.DataFrame) -> float:
            before = np.sort(
                data.loc[data["period"] == "Voor", "average_length"].to_numpy()
            )
            after = np.sort(
                data.loc[data["period"] == "Na", "average_length"].to_numpy()
            )
            values = np.sort(np.unique(np.concatenate([before, after])))
            before_ecdf = np.searchsorted(before, values, side="right") / len(before)
            after_ecdf = np.searchsorted(after, values, side="right") / len(after)
            return float(np.max(np.abs(before_ecdf - after_ecdf)))

        ecdf_null = NullDistribution(maximum_ecdf_distance, n_iter=10_000, seed=43).run(
            monthly_message_length, label="period"
        )
        logger.info(
            f"Geobserveerde maximale ECDF-afstand: {ecdf_null.observed:.3f}; "
            f"eenzijdige p-waarde: {ecdf_null.p_value('greater'):.5f}"
        )

        today = pd.Timestamp("2026-09-21")
        birth_date = today - pd.DateOffset(years=29)
        smoothed_message_length_no_period = monthly_message_length.copy()
        smoothed_message_length_no_period["average_length"] = (
            smoothed_message_length_no_period["average_length"]
            .rolling(window=3, center=True, min_periods=1)
            .mean()
        )
        smoothed_message_length_no_period["age"] = (
            smoothed_message_length_no_period["month"] - birth_date
        ).dt.days / 365.2425

        monthly_message_length_with_age = monthly_message_length.copy()
        monthly_message_length_with_age["age"] = (
            monthly_message_length_with_age["month"] - birth_date
        ).dt.days / 365.2425

        trend_breakpoint = pd.Timestamp("2020-06-01")
        trend_before = monthly_message_length_with_age[
            monthly_message_length_with_age["month"] < trend_breakpoint
        ].copy()
        trend_after = monthly_message_length_with_age[
            monthly_message_length_with_age["month"] >= trend_breakpoint
        ].copy()

        trend_before_coefficients = np.polyfit(
            trend_before["age"],
            trend_before["average_length"],
            1,
        )
        trend_after_coefficients = np.polyfit(
            trend_after["age"],
            trend_after["average_length"],
            1,
        )
        trend_before["trend"] = np.polyval(
            trend_before_coefficients,
            trend_before["age"],
        )
        trend_after["trend"] = np.polyval(
            trend_after_coefficients,
            trend_after["age"],
        )

        figure, axis = plt.subplots(figsize=(11, 4))
        axis.plot(
            smoothed_message_length_no_period["age"],
            smoothed_message_length_no_period["average_length"],
            color="blue",
            linewidth=2.5,
            label="Gemiddelde per 3 maanden",
        )
        axis.plot(
            monthly_message_length_with_age["age"],
            monthly_message_length_with_age["average_length"],
            color="gray",
            alpha=0.7,
            label="Gemiddelde per maand",
        )
        axis.plot(
            trend_before["age"],
            trend_before["trend"],
            color="red",
            label="Trend tot juni 2020",
        )
        axis.plot(
            trend_after["age"],
            trend_after["trend"],
            color="red",
            linestyle="--",
            label="Trend vanaf juni 2020",
        )
        breakpoint_age = (trend_breakpoint - birth_date).days / 365.2425
        axis.axvline(
            breakpoint_age,
            color="gray",
            linestyle=":",
            linewidth=1.5,
        )
        axis.annotate(
            "eerste groepsvakantie",
            xy=(breakpoint_age, 0.65),
            xycoords=("data", "axes fraction"),
            xytext=(0.03, 0.93),
            textcoords="axes fraction",
            color="gray",
            ha="left",
            va="top",
            arrowprops={"arrowstyle": "->", "color": "gray", "lw": 1.2},
        )
        axis.set(
            title="Eerste groepsvakantie zorgt voor langere berichten",
            xlabel="Leeftijd (jaar)",
            ylabel="Gemiddelde berichtlengte (tekens)",
        )
        axis.grid(alpha=0.3)
        axis.legend(loc="upper left", bbox_to_anchor=(1.02, 1), borderaxespad=0)
        figure.text(
            0.5,
            0.005,
            "13 vrienden die samen ouder worden, hoe ze met elkaar praten verandert over de jaren. \n"
            "Nadat ze samen op vakantie zijn gegaan is er een sprong in gemiddelde bericht lengte "
            "dit blijft stabiel over de jaren.\n\n"
            "Blauw: gemiddelde per 3 maanden; grijs: gemiddelde per maand; rood: stukgewijze trend.",
            ha="center",
            va="bottom",
            fontsize=9,
        )
        figure.subplots_adjust(bottom=0.32, right=0.78)

        try:
            self.plot_path = Plotter().save_figure(
                figure, filename="time_series.png", dpi=100
            )
        finally:
            plt.close(figure)

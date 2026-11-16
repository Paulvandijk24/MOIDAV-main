"""Entry point for the upcoming category-comparison analysis."""

import logging

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, norm

from scripts.plotter import Plotter

logger = logging.getLogger(__name__)


class ComparingCategories:
    """Recreate the notebook's full-chat sadness comparison and bar plot."""

    def __init__(self, messages: pd.DataFrame) -> None:
        full_phase_order = ["hele_chat_voor", "brand_dag", "hele_chat_na"]
        full_chat = messages.copy()
        if "local_date" not in full_chat:
            full_chat["local_date"] = (
                pd.to_datetime(full_chat["timestamp"], utc=True)
                .dt.tz_convert("Europe/Amsterdam")
                .dt.normalize()
            )
        fire_date = pd.Timestamp("2025-07-06", tz="Europe/Amsterdam")
        full_chat["full_chat_phase"] = np.select(
            [
                full_chat["local_date"] < fire_date,
                full_chat["local_date"].eq(fire_date),
                full_chat["local_date"] > fire_date,
            ],
            full_phase_order,
            default="onbekend",
        )
        full_phase_messages = full_chat[
            full_chat["full_chat_phase"].isin(full_phase_order)
        ]
        sad_messages = full_phase_messages.assign(
            is_sad=full_phase_messages["message_emotion"].eq("verdrietig")
        )
        full_sad_stats = (
            sad_messages.groupby("full_chat_phase")["is_sad"]
            .agg(["mean", "count"])
            .reindex(full_phase_order)
            .fillna(0)
        )
        full_sad_share = full_sad_stats["mean"].mul(100)
        full_sad_error = (
            np.sqrt(
                full_sad_stats["mean"]
                * (1 - full_sad_stats["mean"])
                / full_sad_stats["count"]
            )
            .fillna(0)
            .mul(100)
        )
        full_counts = (
            sad_messages.groupby("full_chat_phase")["is_sad"]
            .agg(["sum", "count"])
            .reindex(full_phase_order)
        )
        observed_counts = full_counts.dropna()
        contingency_table = np.array(
            [
                observed_counts["sum"].to_numpy(),
                (observed_counts["count"] - observed_counts["sum"]).to_numpy(),
            ]
        )
        if len(observed_counts) > 1:
            chi2, omnibus_p, degrees_of_freedom, _ = chi2_contingency(contingency_table)
        else:
            chi2, omnibus_p, degrees_of_freedom = 0.0, 1.0, 0

        def two_proportion_p_value(phase_a: str, phase_b: str) -> float:
            counts = full_counts.loc[[phase_a, phase_b]]
            sad_a, total_a = counts.loc[phase_a, "sum"], counts.loc[phase_a, "count"]
            sad_b, total_b = counts.loc[phase_b, "sum"], counts.loc[phase_b, "count"]
            pooled = (sad_a + sad_b) / (total_a + total_b)
            standard_error = np.sqrt(
                pooled * (1 - pooled) * (1 / total_a + 1 / total_b)
            )
            z_score = (sad_a / total_a - sad_b / total_b) / standard_error
            return 2 * norm.sf(abs(z_score))

        pairwise_comparisons = {
            "voor vs branddag": ("hele_chat_voor", "brand_dag"),
            "branddag vs na": ("brand_dag", "hele_chat_na"),
            "voor vs na": ("hele_chat_voor", "hele_chat_na"),
        }
        pairwise_p = {
            comparison: two_proportion_p_value(*phases)
            for comparison, phases in pairwise_comparisons.items()
            if phases[0] in observed_counts.index and phases[1] in observed_counts.index
        }
        pairwise_p = pd.Series(pairwise_p, dtype=float)
        pairwise_p_bonferroni = (pairwise_p * len(pairwise_p)).clip(upper=1)
        significant_pairs = pairwise_p_bonferroni[pairwise_p_bonferroni < 0.05]
        significant_text = (
            "geen paarvergelijking is significant"
            if significant_pairs.empty
            else ", ".join(
                f"{comparison} (p_adj = {p_value:.3g})"
                for comparison, p_value in significant_pairs.items()
            )
        )

        phase_labels = ["voor de brand", "Branddag", "na de brand"]
        context_text = (
            "Deze grafiek is genormaliseerd: het percentage verdrietige berichten is\n"
            "berekend als het aantal verdrietige berichten gedeeld door het totale aantal\n"
            "berichten in die periode. \n\n"
            f"Significantie: chi-kwadraattoets chi2({degrees_of_freedom}) = "
            f"{chi2:.2f}, p = {omnibus_p:.3g}.\n"
            f"Na Bonferroni-correctie zijn significant: {significant_text}."
        )
        figure, axis = plt.subplots(figsize=(10, 10))
        try:
            bars = axis.bar(
                phase_labels,
                full_sad_share.to_numpy(),
                yerr=full_sad_error.to_numpy(),
                capsize=6,
                color=["gray", "firebrick", "gray"],
                edgecolor="black",
            )
            for bar, value in zip(bars, full_sad_share):
                axis.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() / 2,
                    f"{value:.1f}%",
                    ha="center",
                    va="center",
                    color="white" if value > 0 else "black",
                    fontweight="bold",
                )
            axis.set_title(
                "Brand in vakantiehuis zorgt voor meer verdrietige berichten."
            )
            axis.yaxis.set_visible(False)
            axis.set_ylim(0, max((full_sad_share + full_sad_error).max() * 1.25, 5))
            axis.set_position((0.15, 0.33, 0.7, 0.58))
            axis.text(
                0.5,
                -0.1,
                context_text,
                transform=axis.transAxes,
                ha="center",
                va="top",
                fontsize=9,
                color="#4d4d4d",
                wrap=True,
            )
            self.plot_path = Plotter().save_figure(
                figure, filename="Comparing_categories_plot.png", dpi=100
            )
        finally:
            plt.close(figure)
        logger.info(
            "Jaarlijks gaat de vriendengroep naar Frankrijk naar het huis van de "
            "ouders. Op 6 juli 2025 is het huis afgebrand vlak voordat de vakantie "
            "begon. De grafiek vergelijkt het percentage verdrietige berichten in "
            "de hele chat voor, op en na de branddag."
        )

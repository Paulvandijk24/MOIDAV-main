"""Reproduce the monthly message-count distribution analysis."""

import logging
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from goad_toolkit.analytics import DistributionFitter, FitResult, NullResult

from scripts.plotter import Plotter

logger = logging.getLogger(__name__)


class Distributions:
    """Fit monthly message counts and plot their distributions."""

    PERMUTATION_COUNT = 10_000
    RANDOM_SEED = 42

    def __init__(
        self, messages: pd.DataFrame, squad_vol_messages: pd.DataFrame
    ) -> None:
        required_columns = {"timestamp", "author_gender"}
        missing_columns = required_columns - set(messages.columns)
        if missing_columns:
            raise ValueError(
                f"Missing monthly-count columns: {sorted(missing_columns)}"
            )
        if "timestamp" not in squad_vol_messages.columns:
            raise ValueError("Squad vol messages are missing the timestamp column.")

        monthly_count_series = self._monthly_count_series(messages, squad_vol_messages)
        monthly_count_samples = {
            label: values.to_numpy(dtype=int)
            for label, values in monthly_count_series.items()
        }
        best_monthly_count_fits = self._fit_distributions(monthly_count_samples)
        monthly_count_support = np.arange(
            0,
            int(np.concatenate(list(monthly_count_samples.values())).max()) + 1,
        )
        paired_monthly_counts = self._paired_counts(monthly_count_series)
        block_sensitivity_rows, block_results = self._block_sensitivity(
            paired_monthly_counts
        )
        self._log_block_sensitivity(
            block_sensitivity_rows, paired_monthly_counts, block_results
        )
        self.plot_path = self._plot(
            monthly_count_samples,
            best_monthly_count_fits,
            monthly_count_support,
            paired_monthly_counts,
            block_sensitivity_rows,
        )

    @staticmethod
    def _monthly_count_series(
        messages: pd.DataFrame, squad_vol_messages: pd.DataFrame
    ) -> dict[str, pd.Series]:
        male_messages = messages.loc[
            (messages["author_gender"] == "man") & messages["timestamp"].notna()
        ].copy()
        male_messages["month"] = male_messages["timestamp"].dt.to_period("M")
        plus_chicks_monthly_counts = male_messages.groupby("month").size()

        squad_vol_timestamped = squad_vol_messages.loc[
            squad_vol_messages["timestamp"].notna()
        ].copy()
        squad_vol_timestamped["month"] = squad_vol_timestamped[
            "timestamp"
        ].dt.to_period("M")
        squad_vol_monthly_counts = squad_vol_timestamped.groupby("month").size()

        if plus_chicks_monthly_counts.empty or squad_vol_monthly_counts.empty:
            raise ValueError(
                "Both chats need timestamped messages to fit monthly counts."
            )

        return {
            "Squad plus chicks — mannen": plus_chicks_monthly_counts,
            "Squad vol": squad_vol_monthly_counts,
        }

    @staticmethod
    def _fit_distributions(
        monthly_count_samples: dict[str, np.ndarray],
    ) -> dict[str, FitResult]:
        fitter = DistributionFitter(seed=42)
        fits = {
            label: fitter.fit(values, discrete=True, criterion="likelihood")
            for label, values in monthly_count_samples.items()
        }
        best_fits = {
            label: fitter.best(label_fits, criterion="likelihood")
            for label, label_fits in fits.items()
        }
        selected_fits = {}
        for label, label_fits in best_fits.items():
            if not label_fits or not isinstance(label_fits[0], FitResult):
                raise ValueError(
                    "GOAD kon voor een van de chats geen discrete verdeling fitten."
                )
            selected_fits[label] = label_fits[0]
        return selected_fits

    @staticmethod
    def _paired_counts(
        monthly_count_series: dict[str, pd.Series],
    ) -> pd.DataFrame:
        paired = pd.concat(
            [
                monthly_count_series["Squad plus chicks — mannen"].rename(
                    "plus_chicks"
                ),
                monthly_count_series["Squad vol"].rename("squad_vol"),
            ],
            axis=1,
            join="inner",
        )
        if paired.empty:
            raise ValueError(
                "Er zijn geen maanden waarin beide chats berichten hebben."
            )
        return paired.dropna().sort_index()

    @staticmethod
    def _lower_shift_statistic(plus_chicks: np.ndarray, squad_vol: np.ndarray) -> float:
        support = np.unique(np.concatenate([plus_chicks, squad_vol]))
        plus_chicks_cdf = np.searchsorted(
            np.sort(plus_chicks), support, side="right"
        ) / len(plus_chicks)
        squad_vol_cdf = np.searchsorted(
            np.sort(squad_vol), support, side="right"
        ) / len(squad_vol)
        return float(np.max(plus_chicks_cdf - squad_vol_cdf))

    def _block_sensitivity(
        self, paired_monthly_counts: pd.DataFrame
    ) -> tuple[list[dict[str, float | int]], dict[int, NullResult]]:
        month_ordinals = pd.PeriodIndex(paired_monthly_counts.index).asi8
        segment_edges = np.r_[
            0,
            np.flatnonzero(np.diff(month_ordinals) != 1) + 1,
            len(paired_monthly_counts),
        ]
        block_results: dict[int, NullResult] = {}
        rows: list[dict[str, float | int]] = []

        for block_months in (1, 3, 6):
            plus_blocks = []
            squad_vol_blocks = []
            for segment_start, segment_end in zip(
                segment_edges[:-1], segment_edges[1:]
            ):
                segment = paired_monthly_counts.iloc[segment_start:segment_end]
                for offset in range(0, len(segment) - block_months + 1, block_months):
                    block = segment.iloc[offset : offset + block_months]
                    plus_blocks.append(block["plus_chicks"].to_numpy(dtype=int))
                    squad_vol_blocks.append(block["squad_vol"].to_numpy(dtype=int))

            if len(plus_blocks) < 4:
                rows.append(
                    {
                        "bloklengte (maanden)": block_months,
                        "bruikbare blokken": len(plus_blocks),
                        "p-waarde": np.nan,
                    }
                )
                continue

            plus_blocks_array = np.stack(plus_blocks)
            squad_vol_blocks_array = np.stack(squad_vol_blocks)
            observed = self._lower_shift_statistic(
                plus_blocks_array.ravel(), squad_vol_blocks_array.ravel()
            )
            rng = np.random.default_rng(self.RANDOM_SEED)
            null_statistics = np.empty(self.PERMUTATION_COUNT)
            for iteration in range(self.PERMUTATION_COUNT):
                swap_blocks = rng.integers(
                    0, 2, size=len(plus_blocks_array), dtype=np.int8
                ).astype(bool)
                shuffled_plus = plus_blocks_array.copy()
                shuffled_squad_vol = squad_vol_blocks_array.copy()
                shuffled_plus[swap_blocks] = squad_vol_blocks_array[swap_blocks]
                shuffled_squad_vol[swap_blocks] = plus_blocks_array[swap_blocks]
                null_statistics[iteration] = self._lower_shift_statistic(
                    shuffled_plus.ravel(), shuffled_squad_vol.ravel()
                )

            result = NullResult(
                observed=observed,
                null=null_statistics,
                n_iter=self.PERMUTATION_COUNT,
                seed=self.RANDOM_SEED,
            )
            block_results[block_months] = result
            rows.append(
                {
                    "bloklengte (maanden)": block_months,
                    "bruikbare blokken": len(plus_blocks_array),
                    "maanden per chat": plus_blocks_array.size,
                    "D+ waargenomen": observed,
                    "eenzijdige p-waarde": result.p_value("greater"),
                }
            )

        if not block_results:
            raise ValueError(
                "Te weinig aaneengesloten overlappende maanden voor een bloktoets."
            )
        return rows, block_results

    @staticmethod
    def _log_block_sensitivity(
        rows: list[dict[str, float | int]],
        paired_monthly_counts: pd.DataFrame,
        block_results: dict[int, NullResult],
    ) -> None:
        logger.info(
            "Block-shuffle sensitivity:\n%s",
            pd.DataFrame(rows).to_string(index=False),
        )
        primary_block_months = max(block_results)
        primary_result = block_results[primary_block_months]
        logger.info(
            "Overlappende actieve maanden: %s; waargenomen D+ = %.3f; "
            "eenzijdige p-waarde bij %s-maandsblokken: %.5f.",
            len(paired_monthly_counts),
            primary_result.observed,
            primary_block_months,
            primary_result.p_value("greater"),
        )
        logger.info(
            "De toets ondersteunt alleen een verschuiving naar lagere maandtotalen "
            "voor deze chats; ze bewijst geen oorzaak."
        )

    def _plot(
        self,
        monthly_count_samples: dict[str, np.ndarray],
        best_monthly_count_fits: dict[str, FitResult],
        monthly_count_support: np.ndarray,
        paired_monthly_counts: pd.DataFrame,
        block_sensitivity_rows: list[dict[str, float | int]],
    ) -> Path:
        figure, axis = plt.subplots(figsize=(10, 6))
        try:
            median_values = {}
            for label, values in monthly_count_samples.items():
                color = "C0" if label.startswith("Squad plus chicks") else "C1"
                best_fit = best_monthly_count_fits[label]
                axis.plot(
                    monthly_count_support,
                    best_fit.frozen_dist.pmf(monthly_count_support),
                    color=color,
                    linewidth=2,
                    marker=".",
                    label=label,
                )
                median_values[label] = np.median(values)
                axis.axvline(
                    median_values[label],
                    color="red",
                    linestyle="--",
                    linewidth=1.5,
                    alpha=0.8,
                    label=(
                        "Mediaan"
                        if label == "Squad plus chicks — mannen"
                        else "_nolegend_"
                    ),
                )

            squad_vol_median = median_values["Squad vol"]
            plus_chicks_median = median_values["Squad plus chicks — mannen"]
            if squad_vol_median != plus_chicks_median:
                axis.annotate(
                    "",
                    xy=(plus_chicks_median, 0.01),
                    xytext=(squad_vol_median, 0.01),
                    arrowprops={"arrowstyle": "->", "color": "red", "linewidth": 2},
                )

            axis.set_title("De mannen zeggen minder als hun vriendinnen meekijken.")
            axis.set_xlabel("Aantal berichten per maand")
            axis.set_ylabel("Dichtheid")
            axis.set_xlim(0, 1500)
            axis.set_ylim(0, 0.012)
            axis.legend()
            axis.grid(axis="y", alpha=0.25)

            sensitivity_lines = [
                f"{int(row['bloklengte (maanden)'])}-maandsblokken: "
                f"p={row['eenzijdige p-waarde']:.5f}"
                for row in block_sensitivity_rows
                if pd.notna(row.get("eenzijdige p-waarde"))
            ]
            shuffle_summary = (
                f"Blok-shuffle op {len(paired_monthly_counts)} overlappende actieve maanden "
                f"({self.PERMUTATION_COUNT:,} permutaties). "
                + "; ".join(sensitivity_lines)
            )
            figure.text(
                0.08,
                0.015,
                shuffle_summary,
                ha="left",
                va="bottom",
                fontsize=9,
                wrap=True,
            )
            figure.tight_layout(rect=(0, 0.13, 1, 1))
            return Plotter().save_figure(figure, filename="distributions.png")
        finally:
            plt.close(figure)

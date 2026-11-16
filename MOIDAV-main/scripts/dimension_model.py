"""Reproduce the Squad plus chicks character-trigram PCA plot."""

import logging

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import TfidfVectorizer

from scripts.plotter import Plotter
from scripts.sessionize import merge_messages, sessionize

logger = logging.getLogger(__name__)


class DimensionModel:
    """Project Squad plus chicks chat sessions to the first two PCA components."""

    def __init__(self, messages: pd.DataFrame) -> None:
        missing_columns = {"author", "timestamp", "message"} - set(messages.columns)
        if missing_columns:
            raise ValueError(
                f"Missing dimension-model columns: {sorted(missing_columns)}"
            )

        unnamed_author = messages["author"].str.fullmatch(r"\+?[\d\s().-]+") | (
            messages["author"].str.casefold().isin({"", "null", "unknown"})
        )
        messages = messages.loc[~unnamed_author].copy()
        logger.info(
            "Squad plus chicks: %s berichten, %s auteurs.",
            f"{len(messages):,}",
            f"{messages['author'].nunique():,}",
        )

        chat = messages.sort_values(["author", "timestamp"]).reset_index(drop=True)
        chat["session_id"] = sessionize(chat, "timestamp", "author", 60 * 60)
        chat_units = merge_messages(chat, ["author", "session_id"])
        session_units = (
            chat_units.loc[chat_units["n_messages"] >= 10]
            .sort_values(["author", "session_id"])
            .reset_index(drop=True)
            .copy()
        )
        if session_units.empty:
            raise ValueError("No sessions with at least 10 messages were found.")
        logger.info(
            "Sessies met minimaal tien berichten: %s van %s (%.1f%%).",
            len(session_units),
            len(chat_units),
            len(session_units) / len(chat_units) * 100,
        )

        trigram_vectorizer = TfidfVectorizer(
            analyzer="char", ngram_range=(3, 3), min_df=2
        )
        trigram_matrix = trigram_vectorizer.fit_transform(session_units["message"])
        pca_matrix = trigram_matrix.astype(np.float32).toarray()
        pca = PCA(n_components=2, svd_solver="randomized", random_state=42)
        coordinates = pca.fit_transform(pca_matrix)
        high_pc1 = coordinates[:, 0] > 0.5
        pca_variance = pca.explained_variance_ratio_
        logger.info(
            "PCA-variantie: component 1 %.1f%%; component 2 %.1f%%; samen %.1f%%."
            "Alleen Sessies met minimaal 10 berichten zijn meegenomen",
            pca_variance[0] * 100,
            pca_variance[1] * 100,
            pca_variance.sum() * 100,
        )

        figure, axis = plt.subplots(figsize=(13, 8))
        try:
            axis.scatter(
                coordinates[~high_pc1, 0],
                coordinates[~high_pc1, 1],
                color="gray",
                label="Gewoon Nederlands",
                s=12,
                alpha=0.55,
            )
            axis.scatter(
                coordinates[high_pc1, 0],
                coordinates[high_pc1, 1],
                color="red",
                label="Straat taal",
                s=12,
                alpha=0.75,
            )
            axis.set_title(
                "Straattaal in de groep. Trigrams tonen een verschil tussen het "
                "taalgebruik in de vriendengroep."
            )
            axis.set_xlabel("PCA-component 1")
            axis.set_ylabel("PCA-component 2")
            axis.legend(title="Sessies")
            figure.tight_layout()
            self.plot_path = Plotter().save_figure(
                figure, filename="dimension_model.png", dpi=100
            )
        finally:
            plt.close(figure)

        logger.info(
            "Saved PCA plot for %s sessions (%s trigrams; combined explained variance %.1f%%).",
            len(session_units),
            trigram_matrix.shape[1],
            pca.explained_variance_ratio_.sum() * 100,
        )
        self._log_shuffle_analysis(pca, pca_matrix, coordinates)
        self._log_high_score_analysis(coordinates)

    @staticmethod
    def _log_shuffle_analysis(
        pca: PCA, pca_matrix: np.ndarray, coordinates: np.ndarray
    ) -> None:
        rng = np.random.default_rng(42)
        shuffled_matrix = np.column_stack(
            [rng.permutation(column) for column in pca_matrix.T]
        )
        shuffled_pca = PCA(n_components=2, svd_solver="randomized", random_state=42)
        shuffled_pca.fit(shuffled_matrix)
        logger.info(
            "Verklaarde variantie in 2 componenten: oorspronkelijk %.1f%%; "
            "geschud %.1f%%.",
            pca.explained_variance_ratio_.sum() * 100,
            shuffled_pca.explained_variance_ratio_.sum() * 100,
        )

        pc1_threshold = 0.5
        pc2_lower, pc2_upper = -0.1, 0.05

        def count_sessions_in_region(projected: np.ndarray) -> int:
            return int(
                (
                    (projected[:, 0] > pc1_threshold)
                    & (projected[:, 1] >= pc2_lower)
                    & (projected[:, 1] <= pc2_upper)
                ).sum()
            )

        observed_count = count_sessions_in_region(coordinates)
        repetitions = 999
        null_counts = np.empty(repetitions, dtype=int)
        rng = np.random.default_rng(42)
        for repetition in range(repetitions):
            row_permutations = np.argsort(rng.random(pca_matrix.shape), axis=0)
            shuffled_rows = np.take_along_axis(pca_matrix, row_permutations, axis=0)
            null_counts[repetition] = count_sessions_in_region(
                pca.transform(shuffled_rows)
            )

        p_value = (1 + np.count_nonzero(null_counts >= observed_count)) / (
            repetitions + 1
        )
        logger.info(
            "Geobserveerd: %s/%s sessies. Shuffle-nulmodel (n=%s): gemiddelde "
            "%.2f, 95e percentiel %.0f; eenzijdige p-waarde %.4f.",
            observed_count,
            len(pca_matrix),
            repetitions,
            null_counts.mean(),
            np.quantile(null_counts, 0.95),
            p_value,
        )

    @staticmethod
    def _log_high_score_analysis(
        coordinates: np.ndarray,
    ) -> None:
        high_score_counts = {}
        for component in range(2):
            scores = coordinates[:, component]
            cutoff = np.quantile(scores, 0.9)
            high_score = scores >= cutoff
            high_score_counts[component + 1] = (int(high_score.sum()), float(cutoff))
        logger.info(
            "Top 10%% hoge scores: PC1 %s sessies (score ≥ %.3f); PC2 %s sessies "
            "(score ≥ %.3f). De verschillen zijn gemiddelde trigrambijdragen in "
            "hoge-score-sessies ten opzichte van de overige sessies.",
            high_score_counts[1][0],
            high_score_counts[1][1],
            high_score_counts[2][0],
            high_score_counts[2][1],
        )

"""Reproduce the Squad plus chicks character-trigram PCA plot."""

import logging

import matplotlib.pyplot as plt
import numpy as np
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import TfidfVectorizer

from scripts.plotter import Plotter
from scripts.preprocess_squad_chats import RAW_DIR, _read_archive
from scripts.sessionize import merge_messages, sessionize

logger = logging.getLogger(__name__)


class DimensionModel:
    """Project Squad plus chicks chat sessions to the first two PCA components."""

    def __init__(self) -> None:
        messages, _, _ = _read_archive(
            RAW_DIR / "Squad plus chicks 🐥.zip",
            classify_authors=False,
            continuation_separator="\n",
        )
        unnamed_author = messages["author"].str.fullmatch(r"\+?[\d\s().-]+") | (
            messages["author"].str.casefold().isin({"", "null", "unknown"})
        )
        messages = messages.loc[~unnamed_author].copy()

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

        trigram_vectorizer = TfidfVectorizer(
            analyzer="char", ngram_range=(3, 3), min_df=2
        )
        trigram_matrix = trigram_vectorizer.fit_transform(session_units["message"])
        pca_matrix = trigram_matrix.astype(np.float32).toarray()
        pca = PCA(n_components=2, svd_solver="randomized", random_state=42)
        coordinates = pca.fit_transform(pca_matrix)
        high_pc1 = coordinates[:, 0] > 0.5

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

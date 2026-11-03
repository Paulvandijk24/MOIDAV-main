"""Run the Squad chat preprocessing and analysis entry points."""

import logging
from pathlib import Path

from scripts.comparing_categories import ComparingCategories
from scripts.dimension_model import DimensionModel
from scripts.distribution import Distribution
from scripts.network import Network
from scripts.preprocess_squad_chats import preprocess_squad_chats
from scripts.relationship import Relationship
from scripts.time_series import TimeSeries
from wa_analyzer.logging_config import configure_logging

ROOT = Path(__file__).resolve().parent
logger = logging.getLogger(__name__)


def main() -> None:
    configure_logging(ROOT)
    logger.info("Starting chat preprocessing.")
    chats = preprocess_squad_chats()
    messages = chats["squad_plus_chicks"]
    ComparingCategories(messages)
    TimeSeries(messages)
    Distribution(messages)
    Relationship(messages)
    DimensionModel(messages)
    Network(messages)
    logger.info("Project run completed.")


if __name__ == "__main__":
    main()

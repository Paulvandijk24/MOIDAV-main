"""Run the Squad chat preprocessing and analysis entry points."""

import logging
from pathlib import Path

from scripts.comparing_categories import ComparingCategories
from scripts.preprocess_squad_chats import preprocess_squad_chats
from wa_analyzer.logging_config import configure_logging

ROOT = Path(__file__).resolve().parent
logger = logging.getLogger(__name__)


def main() -> None:
    configure_logging(ROOT)
    logger.info("Starting chat preprocessing.")
    preprocess_squad_chats()
    ComparingCategories()
    logger.info("Project run completed.")


if __name__ == "__main__":
    main()

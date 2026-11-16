"""Run the Squad chat preprocessing and analysis entry points."""

import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"

logger = logging.getLogger(__name__)


def main() -> None:
    if str(SRC) not in sys.path:
        sys.path.insert(0, str(SRC))

    from scripts.comparing_categories import ComparingCategories
    from scripts.dimension_model import DimensionModel
    from scripts.distributions import Distributions
    from scripts.network import Network
    from scripts.preprocess_squad_chats import preprocess_squad_chats
    from scripts.relationship import Relationship
    from scripts.time_series import TimeSeries
    from wa_analyzer.logging_config import configure_logging

    configure_logging(ROOT)
    logger.info("Starting chat preprocessing.")
    chats = preprocess_squad_chats()
    messages = chats["squad_plus_chicks"]
    ComparingCategories(chats["squad_vol"])
    TimeSeries(chats["squad_vol"])
    Distributions(messages, chats["squad_vol"])
    Relationship(messages)
    DimensionModel()
    Network(messages)
    logger.info("Project run completed.")


if __name__ == "__main__":
    main()

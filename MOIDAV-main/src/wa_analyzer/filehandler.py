import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


class FileHandler:
    def __init__(self, config):
        self.config = config

    def load(self, filepath: Path) -> pd.DataFrame:
        """Load preprocessed WhatsApp data."""
        timecol = self.config.time_col
        data = pd.read_csv(filepath, parse_dates=[timecol])
        logger.info("Loaded data from %s", filepath)
        return data

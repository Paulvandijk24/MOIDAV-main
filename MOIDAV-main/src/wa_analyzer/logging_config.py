"""Shared standard-library logging configuration for project entry points."""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def configure_logging(project_root: Path) -> None:
    """Log to the console and a rotating file under the project root."""
    log_dir = project_root / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    if not root_logger.handlers:
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
        console = logging.StreamHandler()
        console.setFormatter(formatter)
        root_logger.addHandler(console)

    log_path = (log_dir / "project.log").resolve()
    if not any(
        isinstance(handler, RotatingFileHandler)
        and Path(handler.baseFilename).resolve() == log_path
        for handler in root_logger.handlers
    ):
        file_handler = RotatingFileHandler(
            log_path, maxBytes=5_000_000, backupCount=3, encoding="utf-8"
        )
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
        )
        root_logger.addHandler(file_handler)

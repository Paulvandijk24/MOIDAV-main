"""Project settings shared by analysis scripts."""

import tomllib
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = PROJECT_ROOT / "output.toml"


def _read_config() -> dict[str, Any]:
    if not CONFIG_PATH.is_file():
        raise FileNotFoundError(f"Output configuration not found: {CONFIG_PATH}")
    with CONFIG_PATH.open("rb") as config_file:
        return tomllib.load(config_file)


def _resolve_plot_directory() -> Path:
    config = _read_config()
    output_settings = config.get("output")
    if not isinstance(output_settings, dict):
        raise ValueError("output.toml must define an [output] section.")
    configured_path = output_settings.get("plots")
    if not isinstance(configured_path, str) or not configured_path.strip():
        raise ValueError("output.toml [output].plots must be a non-empty path.")
    output_path = Path(configured_path).expanduser()
    if not output_path.is_absolute():
        output_path = PROJECT_ROOT / output_path
    return output_path.resolve()


PLOTS_DIR = _resolve_plot_directory()

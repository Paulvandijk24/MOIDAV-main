#!/usr/bin/env python3
"""Check that `ParseIRCLines` hasn't drifted between lesson 1 and `scripts/pipelines.py`.

Lesson 1 derives `ParseIRCLines` from scratch as the exercise; `scripts/pipelines.py`
carries an intentional copy so lesson 2 onward can import the parsed frame instead of
re-deriving the regex. Two copies of one class stay identical right up until the day one
of them is fixed and the other isn't — nothing catches that drift on its own, so this does.

    uv run tools/check_pipeline_drift.py
"""

from __future__ import annotations

import ast
import inspect
import json
import logging
from pathlib import Path

from wa_analyzer.logging_config import configure_logging

logger = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "notebooks" / "lesson1" / "01.2-irc-chat.ipynb"
CLASS_NAME = "ParseIRCLines"


def notebook_class_source(path: Path, class_name: str) -> str:
    """Find the cell that defines `class_name` and return its source, normalised."""
    nb = json.loads(path.read_text())
    for cell in nb["cells"]:
        if cell["cell_type"] != "code":
            continue
        source = "".join(cell["source"])
        if source.strip().startswith(f"class {class_name}("):
            return source.strip()
    raise ValueError(f"No cell in {path} defines `class {class_name}`")


def library_class_source() -> str:
    from scripts.pipelines import ParseIRCLines

    return inspect.getsource(ParseIRCLines).strip()


def normalise(source: str) -> str:
    """Compare by AST dump, not text — so formatting-only diffs (e.g. via ruff/black
    reformatting one copy but not the other) don't count as drift."""
    return ast.dump(ast.parse(source))


def main() -> int:
    configure_logging(ROOT)
    notebook_source = notebook_class_source(NOTEBOOK, CLASS_NAME)
    library_source = library_class_source()

    if normalise(notebook_source) == normalise(library_source):
        logger.info("%s: lesson 1 and scripts/pipelines.py agree", CLASS_NAME)
        return 0

    logger.error(
        f"{CLASS_NAME} has drifted between {NOTEBOOK} and scripts/pipelines.py.\n"
        "They are duplicated on purpose (see PTT-91) — bring them back in sync by hand.\n"
    )
    logger.error("--- notebook version ---\n%s", notebook_source)
    logger.error("--- scripts/pipelines.py version ---\n%s", library_source)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

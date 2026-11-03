"""Read, classify, and save the two Squad WhatsApp exports."""

from __future__ import annotations

import logging
import re
from io import TextIOWrapper
from pathlib import Path
from zipfile import ZipFile

import pandas as pd

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
CHAT_DATETIME_FORMAT = "%d-%m-%Y %H:%M"
MESSAGE_HEADER = re.compile(r"^(\d{2}-\d{2}-\d{4} \d{2}:\d{2}) - (.*?): (.*)$")
TIMESTAMPED_LINE = re.compile(r"^(\d{2}-\d{2}-\d{4} \d{2}:\d{2}) - (.*)$")

AUTHOR_ALIASES = {
    "Eikel": "Joel",
    "Vincent": "Vincent Kruithof",
}
AUTHOR_GENDER = {
    "Eef": "vrouw",
    "Ijsie": "man",
    "Joel": "man",
    "Kevin": "man",
    "Marijn": "man",
    "Nick": "man",
    "null": "vrouw",
    "Paul": "man",
    "Rheno": "man",
    "Rik": "man",
    "Rüberhaupt": "man",
    "Schwéhn": "man",
    "Thijsje": "man",
    "Tim Wapenaar": "man",
    "Vincent Kruithof": "man",
    "+31 6 20878246": "vrouw",
    "+31 6 27594625": "vrouw",
    "+31 6 28262831": "vrouw",
    "+31 6 28514891": "vrouw",
    "+31 6 30196468": "vrouw",
    "+31 6 37556157": "vrouw",
    "+31 6 37556177": "vrouw",
    "+31 6 39190988": "vrouw",
    "+31 6 39512381": "vrouw",
    "+31 6 43437377": "vrouw",
    "+31 6 43970301": "vrouw",
    "+31 6 48559406": "vrouw",
    "+31 6 54220861": "vrouw",
    "+31 6 82000019": "vrouw",
    "+31 6 83801855": "vrouw",
}


def _read_archive(
    zip_path: Path, *, classify_authors: bool
) -> tuple[pd.DataFrame, pd.DataFrame, int]:
    """Parse one WhatsApp ZIP, returning messages, system events, and continuations."""
    if not zip_path.is_file():
        raise FileNotFoundError(f"Chatarchief niet gevonden: {zip_path}")

    with ZipFile(zip_path) as archive:
        text_members = [
            name for name in archive.namelist() if name.lower().endswith(".txt")
        ]
        if len(text_members) != 1:
            raise ValueError(
                f"Verwacht precies één .txt-chatbestand in {zip_path.name}; "
                f"gevonden: {len(text_members)}."
            )

        message_records: list[tuple[pd.Timestamp, str, str]] = []
        event_records: list[tuple[pd.Timestamp, str]] = []
        last_record_kind: str | None = None
        continuation_lines = 0

        with TextIOWrapper(
            archive.open(text_members[0]), encoding="utf-8-sig"
        ) as chat_file:
            for line_number, raw_line in enumerate(chat_file, start=1):
                line = raw_line.rstrip("\r\n")
                message_match = MESSAGE_HEADER.match(line)
                if message_match:
                    timestamp_text, author, message = message_match.groups()
                    timestamp = pd.to_datetime(
                        timestamp_text,
                        format=CHAT_DATETIME_FORMAT,
                        utc=True,
                        errors="raise",
                    )
                    author = author.strip().strip("\u200e\u200f")
                    message_records.append((timestamp, author, message.strip()))
                    last_record_kind = "message"
                    continue

                timestamp_match = TIMESTAMPED_LINE.match(line)
                if timestamp_match:
                    timestamp_text, event_text = timestamp_match.groups()
                    timestamp = pd.to_datetime(
                        timestamp_text,
                        format=CHAT_DATETIME_FORMAT,
                        utc=True,
                        errors="raise",
                    )
                    event_records.append((timestamp, event_text.strip()))
                    last_record_kind = "event"
                    continue

                if last_record_kind == "message":
                    timestamp, author, message = message_records[-1]
                    message_records[-1] = (
                        timestamp,
                        author,
                        f"{message}\n{line}".strip(),
                    )
                    continuation_lines += 1
                elif last_record_kind == "event":
                    timestamp, event = event_records[-1]
                    event_records[-1] = (timestamp, f"{event}\n{line}".strip())
                    continuation_lines += 1
                elif line.strip():
                    raise ValueError(
                        f"Onverwachte regel zonder tijdstempel of voorafgaand record "
                        f"op regel {line_number} in {zip_path.name}."
                    )

    messages = pd.DataFrame(message_records, columns=["timestamp", "author", "message"])
    events = pd.DataFrame(event_records, columns=["timestamp", "event"])
    messages["author"] = messages["author"].replace(AUTHOR_ALIASES)
    messages["message_length"] = messages["message"].str.len()
    messages["word_count"] = messages["message"].str.split().str.len()

    if classify_authors:
        unclassified = set(messages["author"].unique()) - set(AUTHOR_GENDER)
        if unclassified:
            raise ValueError(
                f"Geen auteursclassificatie opgegeven voor: {sorted(unclassified)}"
            )
        messages["author_gender"] = messages["author"].map(AUTHOR_GENDER)

    logger.info(
        "%s: parsed %s messages, %s system events, %s continuation lines",
        zip_path.name,
        f"{len(messages):,}",
        f"{len(events):,}",
        f"{continuation_lines:,}",
    )
    return messages, events, continuation_lines


def preprocess_squad_chats(
    raw_dir: Path = RAW_DIR, output_dir: Path = PROCESSED_DIR
) -> dict[str, pd.DataFrame]:
    """Preprocess both ZIP exports and save their message/event tables as Parquet."""
    chats = {
        "squad_plus_chicks": _read_archive(
            raw_dir / "Squad plus chicks 🐥.zip", classify_authors=True
        ),
        "squad_vol": _read_archive(raw_dir / "Squad vol.zip", classify_authors=False),
    }
    output_dir.mkdir(parents=True, exist_ok=True)

    result: dict[str, pd.DataFrame] = {}
    for name, (messages, events, _) in chats.items():
        message_path = output_dir / f"{name}.parquet"
        event_path = output_dir / f"{name}_events.parquet"
        messages.to_parquet(message_path, index=False)
        events.to_parquet(event_path, index=False)
        logger.info("Saved %s messages to %s", len(messages), message_path)
        logger.info("Saved %s system events to %s", len(events), event_path)
        result[name] = messages
    return result

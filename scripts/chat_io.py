"""Shared helpers for chat-prompt JSON inputs and JSONL outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


Message = dict[str, Any]
ChatBatch = list[list[Message]]


def load_json(path: str | Path) -> Any:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def dump_jsonl(path: str | Path, rows: list[dict[str, Any]]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def validate_chat_batch(batch: Any) -> ChatBatch:
    """Validate the JSON format used by the inference runners.

    Expected format: a JSON list of chat-message lists, where each message is a
    dictionary containing at least `role` and `content` fields.
    """
    if not isinstance(batch, list):
        raise ValueError("Input JSON must be a list of chat-message lists.")

    for example_index, messages in enumerate(batch):
        if not isinstance(messages, list):
            raise ValueError(f"Item {example_index} must be a list of messages.")
        if not messages:
            raise ValueError(f"Item {example_index} is an empty message list.")
        for message_index, message in enumerate(messages):
            if not isinstance(message, dict):
                raise ValueError(
                    f"Item {example_index}, message {message_index} must be an object."
                )
            missing = {"role", "content"} - set(message)
            if missing:
                raise ValueError(
                    f"Item {example_index}, message {message_index} is missing fields: "
                    f"{', '.join(sorted(missing))}."
                )
            if not isinstance(message["content"], str):
                raise ValueError(
                    f"Item {example_index}, message {message_index} field `content` must be a string."
                )
    return batch


def load_chat_batch(path: str | Path, limit: int | None = None) -> ChatBatch:
    batch = validate_chat_batch(load_json(path))
    if limit is not None:
        return batch[:limit]
    return batch

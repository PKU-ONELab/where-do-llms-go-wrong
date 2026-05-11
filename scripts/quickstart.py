#!/usr/bin/env python3
"""Zero-dependency quickstart for the AI-reviewer diagnostic release.

This script is intentionally lightweight: it validates the repository layout,
checks the example schemas, and writes a tiny demo artifact. It does not call any
model API and does not require the companion dataset.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "outputs" / "quickstart"

REQUIRED_PATHS = [
    "README.md",
    "CITATION.bib",
    "CITATION.cff",
    "LICENSE",
    "Makefile",
    "examples/example.json",
    "examples/openreview_comments_minimal.json",
    "examples/system_outputs_baseline.jsonl",
    "examples/system_outputs_perturbed_soundness.jsonl",
    "scripts/run_openrouter.py",
    "scripts/run_gemini.py",
    "scripts/run_vllm.py",
    "scripts/clean_openreview.py",
    "scripts/generate_diagnostic_report.py",
    "scripts/summarize_release_data.py",
    "prompts/base_prompt.jsonl",
    "prompts/perturb_prompt.jsonl",
    "docs/GETTING_STARTED.md",
    "docs/DATA.md",
    "docs/REPRODUCIBILITY.md",
]


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_chat_examples(path: Path) -> int:
    data = load_json(path)
    if not isinstance(data, list) or not data:
        raise ValueError(f"{path} must be a non-empty JSON list.")
    for item_index, messages in enumerate(data):
        if not isinstance(messages, list) or not messages:
            raise ValueError(f"{path}: item {item_index} must be a non-empty message list.")
        for message_index, message in enumerate(messages):
            if not isinstance(message, dict):
                raise ValueError(f"{path}: item {item_index}, message {message_index} must be an object.")
            if not isinstance(message.get("role"), str) or not isinstance(message.get("content"), str):
                raise ValueError(
                    f"{path}: item {item_index}, message {message_index} must contain string role/content fields."
                )
    return len(data)


def validate_openreview_fixture(path: Path) -> int:
    data = load_json(path)
    if not isinstance(data, list) or not data:
        raise ValueError(f"{path} must be a non-empty OpenReview fixture list.")

    # `clean_openreview.py` accepts either a flat note list or a list of forum-level
    # note lists. The release example uses the forum-level shape.
    if all(isinstance(item, list) for item in data):
        notes = [note for forum_notes in data for note in forum_notes]
    else:
        notes = data

    required = {"id", "content"}
    for index, note in enumerate(notes):
        if not isinstance(note, dict):
            raise ValueError(f"{path}: note {index} must be an object.")
        missing = required - set(note)
        if missing:
            raise ValueError(f"{path}: note {index} missing fields {sorted(missing)}.")
    return len(notes)


def count_jsonl(path: Path) -> int:
    with path.open("r", encoding="utf-8") as handle:
        return sum(1 for line in handle if line.strip())


def main() -> None:
    missing = [rel for rel in REQUIRED_PATHS if not (ROOT / rel).exists()]
    if missing:
        raise FileNotFoundError("Missing required release files:\n" + "\n".join(f"  - {item}" for item in missing))

    chat_examples = validate_chat_examples(ROOT / "examples" / "example.json")
    openreview_notes = validate_openreview_fixture(ROOT / "examples" / "openreview_comments_minimal.json")
    base_prompts = count_jsonl(ROOT / "prompts" / "base_prompt.jsonl")
    perturb_prompts = count_jsonl(ROOT / "prompts" / "perturb_prompt.jsonl")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    artifact = {
        "status": "ok",
        "what_ran": "zero-dependency layout and schema validation",
        "model_calls": 0,
        "dataset_required": False,
        "validated": {
            "chat_examples": chat_examples,
            "openreview_notes": openreview_notes,
            "base_prompt_rows": base_prompts,
            "perturb_prompt_rows": perturb_prompts,
        },
        "next_steps": [
            "uv run make smoke-test",
            "uv run hf download leejamesssss/ai-reviewer-diagnostic-data --repo-type dataset --local-dir ai-reviewer-diagnostic-data",
            "uv run python scripts/summarize_release_data.py --data-dir ai-reviewer-diagnostic-data/data",
        ],
        "citation": {
            "doi": "10.1145/3746252.3761274",
            "bibtex": "CITATION.bib",
            "cff": "CITATION.cff",
        },
    }
    output_path = OUTPUT_DIR / "quickstart_summary.json"
    output_path.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print("AI-reviewer diagnostic release quickstart: OK")
    print(f"Validated {chat_examples} chat example(s), {openreview_notes} OpenReview note(s).")
    print(f"Prompt rows: base={base_prompts}, perturb={perturb_prompts}.")
    print(f"Wrote {output_path.relative_to(ROOT)}")
    print("Next: run `uv run make smoke-test`, then download the Hugging Face dataset if you need full artifacts.")


if __name__ == "__main__":
    main()

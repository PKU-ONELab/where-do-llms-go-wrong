#!/usr/bin/env python3
"""Summarize the release data directory without external dependencies."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def human_size(num_bytes: int) -> str:
    units = ["B", "KB", "MB", "GB"]
    size = float(num_bytes)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.2f} {unit}" if unit != "B" else f"{int(size)} B"
        size /= 1024
    return f"{size:.2f} GB"


def count_jsonl_rows(path: Path) -> int:
    with path.open("rb") as f:
        return sum(1 for line in f if line.strip())


def sample_jsonl_keys(path: Path) -> list[str]:
    try:
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                obj = json.loads(line)
                if isinstance(obj, dict):
                    return sorted(obj.keys())[:30]
                return [type(obj).__name__]
    except Exception as exc:  # noqa: BLE001 - diagnostic CLI should keep going
        return [f"<could not parse sample: {exc}>"]
    return []


def summarize(data_dir: Path, top_n: int) -> None:
    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")

    files = [p for p in data_dir.rglob("*") if p.is_file()]
    total_size = sum(p.stat().st_size for p in files)
    suffix_counts = Counter(p.suffix.lower() or "<none>" for p in files)

    print(f"Data directory: {data_dir}")
    print(f"Files: {len(files)}")
    print(f"Total size: {human_size(total_size)}")
    print()

    print("File types:")
    for suffix, count in suffix_counts.most_common():
        print(f"  {suffix}: {count}")
    print()

    jsonl_files = sorted(p for p in files if p.suffix.lower() == ".jsonl")
    if jsonl_files:
        print("JSONL files:")
        for path in jsonl_files[:top_n]:
            rel = path.relative_to(data_dir)
            rows = count_jsonl_rows(path)
            keys = sample_jsonl_keys(path)
            print(f"  {rel}: {rows} rows; sample keys={keys}")
        if len(jsonl_files) > top_n:
            print(f"  ... {len(jsonl_files) - top_n} more JSONL files omitted")
        print()

    print(f"Largest {min(top_n, len(files))} files:")
    for path in sorted(files, key=lambda p: p.stat().st_size, reverse=True)[:top_n]:
        print(f"  {human_size(path.stat().st_size):>10}  {path.relative_to(data_dir)}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize release data artifacts.")
    parser.add_argument("--data-dir", required=True, type=Path, help="Local dataset directory, e.g. ai-reviewer-diagnostic-data/data.")
    parser.add_argument("--top-n", default=20, type=int, help="Number of JSONL/largest-file entries to print.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summarize(args.data_dir, args.top_n)


if __name__ == "__main__":
    main()

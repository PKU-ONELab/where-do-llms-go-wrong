"""Generate perturbation-sensitivity reports for automated review systems.

The script compares baseline outputs against outputs on paired perturbed inputs.
It is intentionally dependency-free so users can evaluate a new review system by
exporting JSONL files with an `id` field plus score/decision fields.

Two modes are supported:

1. Explicit pair mode:
   ai-reviewer-diagnostics \
     --baseline outputs/my_system_baseline.jsonl \
     --perturbed outputs/my_system_perturbed_soundness.jsonl \
     --condition paper/soundness \
     --output-md reports/my_system_report.md

2. Built-in demo mode after pip install:
   ai-reviewer-diagnostics --demo --output-md outputs/demo_diagnostic_report.md

3. Directory mode using the public filename convention:
   ai-reviewer-diagnostics \
     --scores-dir ai-reviewer-diagnostic-data/data/annotation_scores \
     --output-md reports/released_scores_report.md
"""

from __future__ import annotations

import argparse
import json
import math
import re
from contextlib import ExitStack
from importlib.resources import as_file, files
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Any, Iterable

DEFAULT_SCORE_FIELDS = [
    "overall_score",
    "contribution_score",
    "soundness_score",
    "presentation_score",
]
DECISION_FIELD = "final_decision"


@dataclass(frozen=True)
class PairSpec:
    baseline: Path
    perturbed: Path
    condition: str
    target: str | None = None
    prompt: str | None = None


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_no}: invalid JSONL row: {exc}") from exc
            if not isinstance(row, dict):
                raise ValueError(f"{path}:{line_no}: each row must be a JSON object")
            if "id" not in row:
                raise ValueError(f"{path}:{line_no}: missing required `id` field")
            rows.append(row)
    if not rows:
        raise ValueError(f"{path}: no JSONL rows found")
    return rows


def to_number(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value) if math.isfinite(float(value)) else None
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        # Handles strings like "6", "6.0", or "Score: 6" while avoiding IDs.
        match = re.search(r"[-+]?\d+(?:\.\d+)?", text)
        if match:
            try:
                return float(match.group(0))
            except ValueError:
                return None
    return None


def normalize_decision(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text if text else None


def metadata_from_name(path: Path) -> dict[str, str]:
    stem = path.stem
    parts = stem.split("__")
    meta: dict[str, str] = {}
    if parts:
        meta["kind"] = parts[0]
    for part in parts[1:]:
        if "-" in part:
            key, value = part.split("-", 1)
            meta[key] = value
    return meta


def discover_pairs(scores_dir: Path) -> list[PairSpec]:
    files = sorted(scores_dir.glob("*.jsonl"))
    baselines: dict[tuple[str | None, str | None], Path] = {}
    perturbeds: list[Path] = []

    for path in files:
        meta = metadata_from_name(path)
        target = meta.get("target")
        prompt = meta.get("prompt")
        kind = meta.get("kind")
        if kind == "baseline":
            baselines[(target, prompt)] = path
        elif kind == "perturbed":
            perturbeds.append(path)

    pairs: list[PairSpec] = []
    for perturbed in perturbeds:
        meta = metadata_from_name(perturbed)
        key = (meta.get("target"), meta.get("prompt"))
        baseline = baselines.get(key)
        if baseline is None:
            continue
        source = meta.get("source", "unknown-source")
        aspect = meta.get("aspect", "unknown-aspect")
        pairs.append(
            PairSpec(
                baseline=baseline,
                perturbed=perturbed,
                condition=f"{source}/{aspect}",
                target=meta.get("target"),
                prompt=meta.get("prompt"),
            )
        )
    if not pairs:
        raise ValueError(f"No baseline/perturbed JSONL pairs discovered in {scores_dir}")
    return pairs


def compare_pair(pair: PairSpec, score_fields: list[str], decision_field: str) -> dict[str, Any]:
    baseline_rows = {str(row["id"]): row for row in load_jsonl(pair.baseline)}
    perturbed_rows = {str(row["id"]): row for row in load_jsonl(pair.perturbed)}
    shared_ids = sorted(set(baseline_rows) & set(perturbed_rows))
    if not shared_ids:
        raise ValueError(f"{pair.condition}: no overlapping ids between {pair.baseline} and {pair.perturbed}")

    score_summary: dict[str, dict[str, Any]] = {}
    for field in score_fields:
        deltas: list[float] = []
        improved = worsened = unchanged = 0
        for item_id in shared_ids:
            base = to_number(baseline_rows[item_id].get(field))
            pert = to_number(perturbed_rows[item_id].get(field))
            if base is None or pert is None:
                continue
            delta = pert - base
            deltas.append(delta)
            if delta > 0:
                improved += 1
            elif delta < 0:
                worsened += 1
            else:
                unchanged += 1
        if deltas:
            score_summary[field] = {
                "n": len(deltas),
                "mean_delta": mean(deltas),
                "mean_abs_delta": mean(abs(x) for x in deltas),
                "min_delta": min(deltas),
                "max_delta": max(deltas),
                "decreased": worsened,
                "unchanged": unchanged,
                "increased": improved,
            }

    decision_changed = 0
    decision_total = 0
    transition_counts: Counter[str] = Counter()
    for item_id in shared_ids:
        base_decision = normalize_decision(baseline_rows[item_id].get(decision_field))
        pert_decision = normalize_decision(perturbed_rows[item_id].get(decision_field))
        if base_decision is None or pert_decision is None:
            continue
        decision_total += 1
        transition = f"{base_decision} -> {pert_decision}"
        transition_counts[transition] += 1
        if base_decision != pert_decision:
            decision_changed += 1

    return {
        "condition": pair.condition,
        "target": pair.target,
        "prompt": pair.prompt,
        "baseline_file": str(pair.baseline),
        "perturbed_file": str(pair.perturbed),
        "shared_ids": len(shared_ids),
        "score_fields": score_summary,
        "decision": {
            "field": decision_field,
            "n": decision_total,
            "changed": decision_changed,
            "change_rate": (decision_changed / decision_total) if decision_total else None,
            "top_transitions": transition_counts.most_common(10),
        },
    }


def aggregate(results: Iterable[dict[str, Any]]) -> dict[str, Any]:
    by_aspect: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    decision_rates: dict[str, list[float]] = defaultdict(list)
    pair_count = 0
    for result in results:
        pair_count += 1
        aspect = result["condition"].split("/", 1)[-1]
        for field, stats in result["score_fields"].items():
            by_aspect[aspect][field].append(float(stats["mean_delta"]))
        rate = result["decision"].get("change_rate")
        if rate is not None:
            decision_rates[aspect].append(float(rate))

    aspect_summary: dict[str, Any] = {}
    for aspect, fields in sorted(by_aspect.items()):
        aspect_summary[aspect] = {
            "mean_delta_by_field": {field: mean(values) for field, values in sorted(fields.items()) if values},
            "mean_decision_change_rate": mean(decision_rates[aspect]) if decision_rates.get(aspect) else None,
        }
    return {"pair_count": pair_count, "aspect_summary": aspect_summary}


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    lines: list[str] = []
    lines.append("# Diagnostic Report")
    lines.append("")
    lines.append("This report compares baseline outputs against paired perturbed outputs from an automated review system.")
    lines.append("")
    overview = payload["aggregate"]
    lines.append("## Overview")
    lines.append("")
    lines.append(f"- Compared condition pairs: {overview['pair_count']}")
    lines.append(f"- Score fields: {', '.join(payload['score_fields'])}")
    lines.append(f"- Decision field: `{payload['decision_field']}`")
    lines.append("")

    if overview["aspect_summary"]:
        lines.append("## Aspect summary")
        lines.append("")
        lines.append("| Aspect | Mean decision-change rate | Mean score deltas |")
        lines.append("| --- | ---: | --- |")
        for aspect, stats in overview["aspect_summary"].items():
            rate = stats.get("mean_decision_change_rate")
            rate_text = "n/a" if rate is None else f"{rate:.3f}"
            delta_text = ", ".join(
                f"{field}={value:+.3f}" for field, value in stats.get("mean_delta_by_field", {}).items()
            ) or "n/a"
            lines.append(f"| {aspect} | {rate_text} | {delta_text} |")
        lines.append("")

    lines.append("## Condition-level results")
    lines.append("")
    for result in payload["results"]:
        lines.append(f"### {result['condition']}")
        meta = []
        if result.get("target"):
            meta.append(f"target={result['target']}")
        if result.get("prompt"):
            meta.append(f"prompt={result['prompt']}")
        if meta:
            lines.append(f"- Metadata: {', '.join(meta)}")
        lines.append(f"- Shared examples: {result['shared_ids']}")
        lines.append(f"- Baseline file: `{Path(result['baseline_file']).name}`")
        lines.append(f"- Perturbed file: `{Path(result['perturbed_file']).name}`")
        decision = result["decision"]
        if decision["n"]:
            lines.append(
                f"- Decision changes: {decision['changed']}/{decision['n']} "
                f"({decision['change_rate']:.3f})"
            )
        else:
            lines.append("- Decision changes: n/a")

        if result["score_fields"]:
            lines.append("")
            lines.append("| Field | n | mean Δ | mean |Δ| | min Δ | max Δ | decreased | unchanged | increased |")
            lines.append("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
            for field, stats in result["score_fields"].items():
                lines.append(
                    f"| {field} | {stats['n']} | {stats['mean_delta']:+.3f} | "
                    f"{stats['mean_abs_delta']:.3f} | {stats['min_delta']:+.3f} | "
                    f"{stats['max_delta']:+.3f} | {stats['decreased']} | "
                    f"{stats['unchanged']} | {stats['increased']} |"
                )
        if decision["top_transitions"]:
            lines.append("")
            lines.append("Top decision transitions:")
            for transition, count in decision["top_transitions"][:5]:
                lines.append(f"- `{transition}`: {count}")
        lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo", action="store_true", help="Run the packaged toy baseline/perturbed example bundled with the pip package.")
    parser.add_argument("--scores-dir", type=Path, help="Directory containing baseline__/perturbed__ JSONL score files.")
    parser.add_argument("--baseline", type=Path, help="Baseline JSONL file for explicit pair mode.")
    parser.add_argument("--perturbed", type=Path, help="Perturbed JSONL file for explicit pair mode.")
    parser.add_argument("--condition", default="custom/perturbation", help="Condition label for explicit pair mode, e.g. paper/soundness.")
    parser.add_argument("--score-fields", nargs="+", default=DEFAULT_SCORE_FIELDS, help="Numeric score fields to compare.")
    parser.add_argument("--decision-field", default=DECISION_FIELD, help="Decision field to compare.")
    parser.add_argument("--output-md", type=Path, default=Path("outputs/diagnostic_report.md"), help="Markdown report output path.")
    parser.add_argument("--output-json", type=Path, help="Optional JSON summary output path.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with ExitStack() as stack:
        if args.demo:
            demo_files = files("ai_reviewer_diagnostics.examples")
            baseline = stack.enter_context(as_file(demo_files / "system_outputs_baseline.jsonl"))
            perturbed = stack.enter_context(as_file(demo_files / "system_outputs_perturbed_soundness.jsonl"))
            pairs = [PairSpec(baseline=baseline, perturbed=perturbed, condition="paper/soundness")]
        elif args.scores_dir:
            pairs = discover_pairs(args.scores_dir)
        else:
            if not args.baseline or not args.perturbed:
                raise SystemExit("Provide --demo, --scores-dir, or both --baseline and --perturbed.")
            pairs = [PairSpec(baseline=args.baseline, perturbed=args.perturbed, condition=args.condition)]

        results = [compare_pair(pair, args.score_fields, args.decision_field) for pair in pairs]
        payload = {
            "score_fields": args.score_fields,
            "decision_field": args.decision_field,
            "aggregate": aggregate(results),
            "results": results,
        }

        write_markdown(args.output_md, payload)
        if args.output_json:
            args.output_json.parent.mkdir(parents=True, exist_ok=True)
            args.output_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

        print(f"Compared {len(results)} condition pair(s).")
        print(f"Wrote {args.output_md}")
        if args.output_json:
            print(f"Wrote {args.output_json}")


if __name__ == "__main__":
    main()

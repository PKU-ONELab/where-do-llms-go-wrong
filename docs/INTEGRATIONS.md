# Integrating a Review System

This guide shows how to connect any automated peer-review system to `ai-reviewer-diagnostics`.

The toolkit is intentionally black-box: it does not need to know how your system generates reviews, scores, or recommendations. It only needs paired outputs on baseline and perturbed inputs.

## 1. Run your system on paired inputs

For each example, run your system on:

- a baseline/original paper, review, or rebuttal input; and
- the paired perturbed input for a known condition such as `paper/soundness` or `review/tone`.

The Hugging Face dataset provides released paired artifacts. You can also use your own paired perturbation data.

## 2. Export JSONL outputs

Each row must have an `id` field shared between the baseline and perturbed files.

Minimal example:

```json
{"id":"paper_001","overall_score":8,"soundness_score":4,"final_decision":"Accept as Poster"}
```

Recommended fields:

| Field | Meaning |
| --- | --- |
| `id` | Shared identifier for aligning baseline and perturbed outputs. |
| `overall_score` | Overall score or rating. |
| `contribution_score` | Contribution/novelty score, if available. |
| `soundness_score` | Soundness/validity score, if available. |
| `presentation_score` | Presentation/clarity score, if available. |
| `final_decision` | Accept/reject-style decision or recommendation. |

You can use custom field names with `--score-fields` and `--decision-field`.

## 3. Generate a report

```bash
ai-reviewer-diagnostics \
  --baseline outputs/my_system_baseline.jsonl \
  --perturbed outputs/my_system_soundness_perturbed.jsonl \
  --condition paper/soundness \
  --output-md reports/my_system_soundness_report.md \
  --output-json reports/my_system_soundness_report.json
```

The Markdown report contains:

- shared example count;
- mean score deltas;
- mean absolute score shifts;
- increased/decreased/unchanged score counts;
- decision-change rate;
- most common decision transitions.

## 4. Directory mode

If your files follow the public dataset naming convention, the CLI can discover pairs automatically:

```text
baseline__target-<review_type>__prompt-<prompt_setting>.jsonl
perturbed__source-<source>__aspect-<aspect>__target-<review_type>__prompt-<prompt_setting>.jsonl
```

Run:

```bash
ai-reviewer-diagnostics \
  --scores-dir ai-reviewer-diagnostic-data/data/annotation_scores \
  --output-md reports/released_scores_report.md \
  --output-json reports/released_scores_report.json
```

## 5. Custom score fields

For a system that outputs `rating`, `confidence`, and `recommendation`:

```bash
ai-reviewer-diagnostics \
  --baseline outputs/baseline.jsonl \
  --perturbed outputs/perturbed.jsonl \
  --condition review/tone \
  --score-fields rating confidence \
  --decision-field recommendation \
  --output-md reports/custom_report.md
```

## 6. Common pitfalls

- IDs must overlap. If there are no shared `id` values, the CLI cannot compare rows.
- Numeric scores can be numbers or strings containing numbers, but clean numeric fields are safer.
- Decision labels are compared as strings; normalize variants such as `accept`, `Accept`, and `Accept as Poster` before export if needed.
- Do not include private peer-review text, deanonymizing metadata, or API keys in public examples or issues.
- Use `--demo` first to verify the installation:

```bash
ai-reviewer-diagnostics --demo --output-md outputs/demo_diagnostic_report.md
```

## 7. How to cite

If this toolkit or dataset helps your evaluation, cite the CIKM 2025 paper using `CITATION.bib` or `CITATION.cff`.

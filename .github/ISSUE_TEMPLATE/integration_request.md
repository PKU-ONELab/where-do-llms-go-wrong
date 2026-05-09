---
name: Integration request
about: Request support or examples for a new automated-review system, benchmark, or output schema
title: "[Integration] "
labels: enhancement, integration
assignees: ""
---

## System or benchmark

Name/link of the automated review system, benchmark, or workflow you want to integrate:

## Output format

Paste 1-3 anonymized rows or a schema summary. The CLI needs shared `id` values across baseline and perturbed outputs.

```json
{"id":"paper_001","overall_score":8,"soundness_score":4,"final_decision":"Accept as Poster"}
```

## What should the report compare?

- Score fields:
- Decision field:
- Perturbation condition(s):
- Any special score direction or scale:

## Desired user-facing command

```bash
ai-reviewer-diagnostics \
  --baseline outputs/my_system_baseline.jsonl \
  --perturbed outputs/my_system_perturbed.jsonl \
  --condition paper/soundness \
  --output-md reports/my_system_report.md
```

## Privacy / data notes

Do not upload private peer reviews, deanonymizing metadata, API keys, or non-public conference data.

---
name: Metric or report idea
about: Suggest a new diagnostic metric, output table, or visualization
title: "[Metric] "
labels: enhancement, metric
assignees: ""
---

## Proposed metric or report section

Describe the metric, table, or visualization.

## Why is it useful for automated peer-review diagnostics?

Explain what failure mode or sensitivity pattern it reveals.

## Required input fields

List the JSONL fields needed by the metric:

- `id`
- `overall_score`
- ...

## Expected output

Markdown/JSON sketch:

```text
| Condition | Metric | Value |
| --- | ---: | ---: |
```

## Generality check

- [ ] Works for multiple review systems, not only one private implementation.
- [ ] Does not require private data or API keys.
- [ ] Can be tested with a tiny fixture.

# Examples

Tiny examples that make the repository runnable immediately after cloning.

## Files

- `example.json`: one chat-style prompt batch for API/local-LLM runners.
- `openreview_comments_minimal.json`: minimal OpenReview-style notes used by `scripts/clean_openreview.py`.

These fixtures are schema demonstrations, not benchmark data. They exist so new users can validate the code path without API keys, GPUs, or the companion dataset.

## Fast checks

```bash
make quickstart
make smoke-test
```

## Input schema for inference runners

The model runners expect a JSON list of chat-message lists:

```json
[
  [
    {"role": "system", "content": "You are a concise academic-review assistant."},
    {"role": "user", "content": "Summarize the review."}
  ]
]
```

Use `--validate-only` with any runner to check the schema without calling an API or loading a local model.

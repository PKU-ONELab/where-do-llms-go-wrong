# Prompts

Machine-readable prompt templates used by the release:

| File | Purpose |
| --- | --- |
| `base_prompt.jsonl` | baseline automated-review prompts |
| `perturb_prompt.jsonl` | aspect-guided perturbation prompts |

Each row is JSONL so prompts can be filtered, versioned, and reused in batch runners. `make quickstart` validates that the prompt files parse and contain the expected fields.

Reuse notes:
- keep prompt IDs stable when comparing runs;
- record model, decoding settings, and prompt file commit;
- cite the paper if these prompts support follow-up work.

# Prompts

Curated prompt files for automated peer-review diagnosis.

## Files

- `base_prompt.jsonl`: base review/meta-review prompts.
- `perturb_prompt.jsonl`: aspect-guided perturbation prompts.

Both files are machine-readable JSONL and are validated by `make quickstart`.

## Why only curated JSONL prompts?

The public release intentionally keeps reusable prompt templates and removes private working drafts, Word-document prompt experiments, raw rebuttal/review samples, and versioned intermediate files. This keeps the repository easier to cite, easier to reuse, and safer for public audiences.

## Reuse

You can load the prompt files with standard JSONL readers. Each line is a prompt record intended to document or reproduce the diagnostic prompt families used by the paper.

## Citation

If you reuse these prompts, cite the associated paper using `CITATION.bib`, `CITATION.cff`, or the BibTeX block in `README.md`.

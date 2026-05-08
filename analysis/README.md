# Analysis Scripts

These scripts support analysis of the annotation-score artifacts under:

```text
../HuggingFace-Dataset/data/annotation_scores/
```

Install analysis dependencies first:

```bash
pip install -r requirements-analysis.txt
```

## Files

- `acc_ratio.py`: acceptance-ratio and decision-distribution analysis.
- `hyp_test_proportion_gap.py`: proportion-gap hypothesis tests.
- `hyp_test_proportion_gap_print.py`: print-oriented variant of proportion-gap tests.
- `hyp_test_simple_gap.py`: simple-gap hypothesis tests.
- `hyp_test_simple_gap_V2.py`: extended simple-gap analysis with agreement metrics.
- `hyp_test_simple_gap_V2_print.py`: print-oriented variant of the extended analysis.

## Notes

The analysis scripts were preserved from the project release artifacts and may require running from the directory containing the relevant JSONL score files. See `docs/REPRODUCIBILITY.md` for current smoke tests and known gaps.

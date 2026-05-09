## Summary

What does this PR change?

## Type of change

- [ ] CLI/report behavior
- [ ] Documentation
- [ ] Example fixture
- [ ] Dataset workflow
- [ ] Analysis/reproducibility
- [ ] Packaging/CI

## Commands run

```bash
git diff --check
python -m compileall -q ai_reviewer_diagnostics scripts analysis
ai-reviewer-diagnostics --demo --output-md outputs/demo_diagnostic_report.md
make smoke-test
```

## Public-release checklist

- [ ] No API keys, `.env` files, checkpoints, generated outputs, or local absolute paths are added.
- [ ] Default install remains lightweight; heavy dependencies are optional.
- [ ] README/docs updated for any public command changes.
- [ ] New CLI behavior has a tiny fixture or demo path.
- [ ] Citation and dataset links remain intact.

## Notes

Anything reviewers should pay special attention to?

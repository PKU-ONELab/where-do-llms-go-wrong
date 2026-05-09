#!/usr/bin/env python3
"""Backward-compatible wrapper for the packaged diagnostic-report CLI.

Prefer:
    ai-reviewer-diagnostics --baseline ... --perturbed ... --output-md ...

This wrapper is kept so older README snippets and Makefile commands continue to work.
"""

from ai_reviewer_diagnostics.report import main

if __name__ == "__main__":
    main()

DATA_DIR ?= ai-reviewer-diagnostic-data/data
PYTHON ?= python
UV ?= uv

.PHONY: quickstart install install-analysis install-vllm smoke-test summarize-data demo-report clean

quickstart:
	$(PYTHON) scripts/quickstart.py

install:
	$(UV) sync

install-analysis:
	$(UV) sync --extra analysis

install-vllm:
	$(UV) sync --extra vllm

summarize-data:
	$(PYTHON) scripts/summarize_release_data.py --data-dir $(DATA_DIR)

demo-report:
	$(PYTHON) -m ai_reviewer_diagnostics.report \
		--baseline examples/system_outputs_baseline.jsonl \
		--perturbed examples/system_outputs_perturbed_soundness.jsonl \
		--condition paper/soundness \
		--output-md outputs/demo_diagnostic_report.md \
		--output-json outputs/demo_diagnostic_report.json

smoke-test: quickstart demo-report
	$(PYTHON) -m compileall -q scripts analysis
	$(PYTHON) -m json.tool examples/example.json >/dev/null
	$(PYTHON) -m json.tool examples/openreview_comments_minimal.json >/dev/null
	$(PYTHON) scripts/run_openrouter.py --input examples/example.json --output outputs/validate_openrouter.jsonl --model dummy --validate-only
	$(PYTHON) scripts/run_gemini.py --input examples/example.json --output outputs/validate_gemini.jsonl --validate-only
	$(PYTHON) scripts/run_vllm.py --input examples/example.json --output outputs/validate_vllm.jsonl --model-path dummy --validate-only
	$(PYTHON) scripts/clean_openreview.py --input examples/openreview_comments_minimal.json --output outputs/openreview_conversations.json --forum-id forum_example

clean:
	rm -rf outputs __pycache__ scripts/__pycache__ analysis/__pycache__ ai_reviewer_diagnostics/__pycache__ *.egg-info .pytest_cache

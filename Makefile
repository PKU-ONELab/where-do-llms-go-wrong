DATA_DIR ?= ai-reviewer-diagnostic-data/data
PYTHON ?= python

.PHONY: quickstart install-core install-analysis smoke-test summarize-data clean

quickstart:
	$(PYTHON) scripts/quickstart.py

install-core:
	$(PYTHON) -m pip install -r requirements-core.txt

install-analysis:
	$(PYTHON) -m pip install -r requirements-analysis.txt

summarize-data:
	$(PYTHON) scripts/summarize_release_data.py --data-dir $(DATA_DIR)

smoke-test: quickstart
	$(PYTHON) -m compileall -q scripts analysis
	$(PYTHON) -m json.tool examples/example.json >/dev/null
	$(PYTHON) -m json.tool examples/openreview_comments_minimal.json >/dev/null
	$(PYTHON) scripts/run_openrouter.py --input examples/example.json --output outputs/validate_openrouter.jsonl --model dummy --validate-only
	$(PYTHON) scripts/run_gemini.py --input examples/example.json --output outputs/validate_gemini.jsonl --validate-only
	$(PYTHON) scripts/run_vllm.py --input examples/example.json --output outputs/validate_vllm.jsonl --model-path dummy --validate-only
	$(PYTHON) scripts/clean_openreview.py --input examples/openreview_comments_minimal.json --output outputs/openreview_conversations.json --forum-id forum_example

clean:
	rm -rf outputs __pycache__ scripts/__pycache__ analysis/__pycache__

DATA_DIR ?= ai-reviewer-diagnostic-data/data

.PHONY: install-core install-analysis smoke-test summarize-data clean

install-core:
	pip install -r requirements-core.txt

install-analysis:
	pip install -r requirements-analysis.txt

summarize-data:
	python scripts/summarize_release_data.py --data-dir $(DATA_DIR)

smoke-test:
	python -m compileall -q scripts analysis
	python -m json.tool examples/example.json >/dev/null
	python -m json.tool examples/openreview_comments_minimal.json >/dev/null
	python scripts/run_openrouter.py --input examples/example.json --output outputs/validate_openrouter.jsonl --model dummy --validate-only
	python scripts/run_gemini.py --input examples/example.json --output outputs/validate_gemini.jsonl --validate-only
	python scripts/run_vllm.py --input examples/example.json --output outputs/validate_vllm.jsonl --model-path dummy --validate-only
	python scripts/clean_openreview.py --input examples/openreview_comments_minimal.json --output outputs/openreview_conversations.json --forum-id forum_example

clean:
	rm -rf outputs __pycache__ scripts/__pycache__ analysis/__pycache__

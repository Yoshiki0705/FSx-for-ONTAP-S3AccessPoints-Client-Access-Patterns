# Local gate set. CI calls the same targets (see .github/workflows/lint.yml).
PYTHON ?= python3
SCRIPTS := scripts

.DEFAULT_GOAL := help
.PHONY: help install lint drift drift-hub secrets test bench-dry-run all

help: ## List targets
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | sed -E 's/:.*## /\t/' | sort

install: ## Install pinned development dependencies
	$(PYTHON) -m pip install -r requirements-dev.txt

lint: ## Markdown structure, ruff (if installed), shellcheck (if installed)
	$(PYTHON) $(SCRIPTS)/check_markdown.py
	@if command -v ruff >/dev/null 2>&1; then ruff check . && ruff format --check .; else echo "ruff: not installed (skipped; make install)"; fi
	@if command -v shellcheck >/dev/null 2>&1; then find . -name '*.sh' -not -path './.git/*' -not -path './.kiro/specs/*' -exec shellcheck {} +; else echo "shellcheck: not installed (skipped)"; fi

drift: ## Hub pin, naming, public safety, ja/en parity, matrix, make targets
	$(PYTHON) $(SCRIPTS)/check_hub_pin.py
	$(PYTHON) $(SCRIPTS)/check_naming.py
	$(PYTHON) $(SCRIPTS)/check_public_safety.py
	$(PYTHON) $(SCRIPTS)/check_parity.py
	$(PYTHON) $(SCRIPTS)/check_matrix.py
	$(PYTHON) $(SCRIPTS)/check_make_targets.py

drift-hub: ## Manual, needs network: pinned Hub tag exists and matches the recorded commit
	$(PYTHON) $(SCRIPTS)/check_hub_tag_exists.py

secrets: ## gitleaks over the working tree and git history (if installed)
	@if command -v gitleaks >/dev/null 2>&1; then gitleaks dir . --config .gitleaks.toml --no-banner && gitleaks git . --config .gitleaks.toml --no-banner; else echo "gitleaks: not installed (skipped)"; fi

test: ## Gate tests (negative cases and coverage)
	$(PYTHON) -m unittest discover -s $(SCRIPTS)/tests

bench-dry-run: ## Benchmark dry run. Never connects to a file system
	$(PYTHON) benchmarks/scripts/run_benchmark.py --dry-run

all: lint drift test secrets ## Full local gate set

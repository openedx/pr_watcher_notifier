.PHONY: help
help: ## Display this help message
	@echo "Please use \`make <target>' where <target> is one of"
	@awk -F ':.*?## ' '/^[a-zA-Z]/ && NF==2 {printf "\033[36m  %-25s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

.PHONY: upgrade
upgrade: ## Update uv.lock with the latest versions of the dependencies
	uv run --with edx-lint edx_lint write_uv_constraints pyproject.toml
	uv lock --upgrade

.PHONY: requirements
requirements: ## Install the Python development requirements
	uv sync --group dev

.PHONY: test
test: ## Run the Python tests
	pytest -rfe --cov=pr_watcher_notifier

.PHONY: test.quality
test.quality:
	prospector --profile opencraft --uses flask

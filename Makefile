.PHONY: help
help: ## Display this help message
	@echo "Please use \`make <target>' where <target> is one of"
	@awk -F ':.*?## ' '/^[a-zA-Z]/ && NF==2 {printf "\033[36m  %-25s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

.PHONY: requirements
requirements: ## Install the Python development requirements\
	# The dev requirements have to be installed first to resolve a conflicting dependency.
	pip install -r requirements-dev.txt -r requirements.txt

.PHONY: test
test: ## Run the Python tests
	pytest --cov=pr_watcher_notifier

.PHONY: test.quality
test.quality:
	prospector --profile opencraft --uses flask

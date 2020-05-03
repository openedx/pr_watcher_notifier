.PHONY: help
help: ## Display this help message
	@echo "Please use \`make <target>' where <target> is one of"
	@awk -F ':.*?## ' '/^[a-zA-Z]/ && NF==2 {printf "\033[36m  %-25s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

.PHONY: requirements
requirements: ## Install the Python development requirements
	pip install -r requirements.txt -r requirements-dev.txt

.PHONY: test
test: ## Run the Python tests
	pytest --cov=pr_watcher_notifier

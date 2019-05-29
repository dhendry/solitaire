SHELL := /bin/bash

.DEFAULT_GOAL := help
.PHONY: clean init proto format typecheck test all-local

clean: ## Very basic clean functionality
	rm -rf dist/ build/ .mypy_cache/ .pytest_cache/ collected_static/ .coverage db.sqlite3

	find ./ -name "*.pyc" -and -type f -and -not -path ".//.git/*" -delete
	find ./ -name "test.log" -and -type f -and  -not -path ".//.git/*" -delete
	find ./ -name "__pycache__" -and -type d -and -not -path ".//.git/*" -delete

	# This will totally remove the virtual environment, you will need to run  init  after
	# A less invasive alternative could be to just use  pipenv --clean  (which uninstalls removed packages)
	pipenv --rm

	# git gc is really just minor tidying - https://git-scm.com/docs/git-gc
	git gc --aggressive

init: ## Initialize or update the local environment using pipenv.
	@command -v pipenv >/dev/null 2>&1  || echo "Pipenv not installed, please install with  brew install pipenv  or appropriate"
	pipenv install --dev

proto: ## Just run unit tests.
	pipenv run protoc -I=solitaire_core --python_out=solitaire_core --mypy_out=solitaire_core solitaire_core/*.proto

format: ## Autoformat
	@# https://github.com/timothycrosley/isort/issues/725
	source $(shell pipenv --venv)/bin/activate && isort --atomic -rc -y . $(EXTRA_FLAGS) && deactivate
	pipenv run black --safe --line-length=110 . $(EXTRA_FLAGS)

typecheck: ## Run mypy
	env MYPYPATH="$(shell ls -d $$(pipenv --venv)/src/* | paste -sd ':' -)" pipenv run mypy --strict --config-file=mypy.ini \
		-p solitaire_core \
		-p solitaire_ai

# TODO: Add typecheck dep
test: proto format ## Just run unit tests (no init)
	pipenv run pytest -v  tests/ --durations=50

all-local: init proto format typecheck test ## Execute all local setup, build and test steps. This is probably the command you are looking for.

play: proto format test ## Play CLI game
	pipenv run python cli_game.py

# Self-Documented Makefile see https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
help: ## When you just dont know what to do with your life, look for inspiration here!
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

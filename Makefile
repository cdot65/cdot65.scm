.PHONY: help build install clean all lint format lint-fix lint-check flake8 mypy ruff-check quality test sanity unit-test integration-test test-integration tox tox-sanity tox-units tox-integration dev-setup example run-examples run-example shell poetry-cmd ansible-cmd playbook docker-test docker-lint docs-serve docs-stop rebuild

COLLECTION_NAMESPACE := cdot65
COLLECTION_NAME := scm
COLLECTION_PATH := $(COLLECTION_NAMESPACE)-$(COLLECTION_NAME)
DC_RUN = docker compose run --rm ansible

# --- Help ---
help:
	@echo "\nCollection Build & Install:"
	@echo "  make build         Build the Ansible collection"
	@echo "  make install       Build & install the collection"
	@echo "  make clean         Remove build artifacts & installed collection"
	@echo "\nLinting & Formatting:"
	@echo "  make lint          Run ansible-lint"
	@echo "  make format        Run black & isort on plugins and tests"
	@echo "  make lint-fix      Auto-fix lint errors with ruff, black, isort"
	@echo "  make flake8        Run flake8 on plugins and tests"
	@echo "  make mypy          Run mypy type checks"
	@echo "  make ruff-check    Run ruff checks"
	@echo "  make quality       Run all code quality checks"
	@echo "\nDocker/Compose Dev:"
	@echo "  make shell         Start a shell in the ansible dev container"
	@echo "  make playbook      Build & install the collection, then run a playbook: make playbook PLAYBOOK=examples/your_playbook.yml"
	@echo "  make docs-serve    Serve docs live (docs container)"
	@echo "  make docs-stop     Stop docs server"
	@echo "  make docker-build	Rebuild the ansible container"
	@echo "  make playbook      Run a playbook in the ansible container"
	@echo "\n"

# --- Collection Build & Install ---
build:
	poetry run ansible-galaxy collection build --force

install: build
	poetry run ansible-galaxy collection install $(COLLECTION_PATH)-*.tar.gz --force

clean:
	rm -f $(COLLECTION_PATH)-*.tar.gz
	rm -rf ~/.ansible/collections/ansible_collections/$(COLLECTION_NAMESPACE)/$(COLLECTION_NAME)

# --- Linting & Formatting ---
lint:
	poetry run ansible-lint

format:
	poetry run black plugins tests
	poetry run isort plugins tests

flake8:
	poetry run flake8 plugins tests

mypy:
	poetry run mypy --config-file pyproject.toml plugins

ruff-check:
	poetry run ruff check plugins tests

lint-fix:
	poetry run ruff check --fix plugins tests
	poetry run black plugins tests
	poetry run isort plugins tests

quality:
	poetry run ruff format --config pyproject.toml plugins
	poetry run flake8 plugins
	poetry run mypy --config-file pyproject.toml plugins

# --- Docker/Compose Development ---
DC_RUN = docker compose run --rm ansible

shell:
	$(DC_RUN) /bin/sh

# Build docker image, copying in the latest collection tarball
docker-build: install
	docker compose build ansible

# Run playbook in container (ensure docker image is up-to-date)
playbook: docker-build
	@if [ -z "$(PLAYBOOK)" ]; then \
		echo "Error: PLAYBOOK parameter is required. Usage: make playbook PLAYBOOK=examples/your_playbook.yml"; \
		exit 1; \
	fi
	$(DC_RUN) ansible-playbook --vault-pass-file .vault_pass $(PLAYBOOK) -v

.DEFAULT_GOAL := help

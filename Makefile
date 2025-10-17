.PHONY: help build install clean all test lint sanity unit-test integration-test sanity-local unit-test-local integration-test-local test-local test-integration dev-setup tox-sanity tox-units tox-integration tox-test tox-flake8 tox-black tox-isort tox-ruff tox-mypy tox-ansible-lint tox-format tox-lint tox-all format lint-all lint-fix lint-check flake8 mypy ruff-check quality run-examples run-example shell playbook docker-build docker-test docker-lint docs-serve docs-stop

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
	rm -rf ansible_collections

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

# --- Testing options (Docker-based) ---
sanity:
	cd ~/.ansible/collections/ansible_collections/$(COLLECTION_NAMESPACE)/$(COLLECTION_NAME) && \
	ansible-test sanity --docker default

unit-test:
	cd ~/.ansible/collections/ansible_collections/$(COLLECTION_NAMESPACE)/$(COLLECTION_NAME) && \
	ansible-test units --docker default

integration-test:
	cd ~/.ansible/collections/ansible_collections/$(COLLECTION_NAMESPACE)/$(COLLECTION_NAME) && \
	ansible-test integration --docker default

# --- Docker/Compose Development ---
shell:
	$(DC_RUN) /bin/sh

# Build docker image, copying in the latest collection tarball
docker-build: install
	docker compose build ansible

# --- Testing options (Local - no Docker) ---
sanity-local:
	cd ~/.ansible/collections/ansible_collections/$(COLLECTION_NAMESPACE)/$(COLLECTION_NAME) && \
	ansible-test sanity --local

unit-test-local:
	cd ~/.ansible/collections/ansible_collections/$(COLLECTION_NAMESPACE)/$(COLLECTION_NAME) && \
	ansible-test units --local

integration-test-local:
	cd ~/.ansible/collections/ansible_collections/$(COLLECTION_NAMESPACE)/$(COLLECTION_NAME) && \
	ansible-test integration --local

test-local: sanity-local unit-test-local

# --- Tox testing (with multiple Python/Ansible versions) ---
tox-sanity:
	poetry run tox -e sanity

tox-units:
	poetry run tox -e ansible2.18-py313-without_constraints

tox-integration:
	poetry run tox -e integration

tox-test: tox-sanity tox-units tox-integration

# Tox linting and formatting
tox-flake8:
	poetry run tox -e flake8-lint

tox-black:
	poetry run tox -e black-format

tox-isort:
	poetry run tox -e isort-format

tox-ruff:
	poetry run tox -e ruff-format

tox-mypy:
	poetry run tox -e mypy

tox-ansible-lint:
	poetry run tox -e ansible-lint

tox-format: tox-black tox-isort tox-ruff

tox-lint: tox-flake8 tox-ruff tox-mypy tox-ansible-lint

# Run all tox environments
tox-all: tox-format tox-lint tox-test

# --- Development setup ---
dev-setup:
	poetry install
	poetry run python -m pip install -r test-requirements.txt

# --- Example playbook runs ---
# Run all example playbooks
run-examples:
	@echo "Running all example playbooks..."
	@for playbook in examples/*.yml; do \
		echo "\n=== Running $$playbook ==="; \
		poetry run ansible-playbook --vault-pass-file .vault_pass $$playbook || exit 1; \
	done
	@echo "\nAll example playbooks executed successfully!"

# Run a specific example playbook
# Usage: make run-example EXAMPLE=application_info
run-example:
	@if [ -z "$(EXAMPLE)" ]; then \
		echo "Error: EXAMPLE parameter is required. Usage: make run-example EXAMPLE=application_info"; \
		exit 1; \
	fi
	@echo "Running example playbook: examples/$(EXAMPLE).yml"
	poetry run ansible-playbook --vault-pass-file .vault_pass examples/$(EXAMPLE).yml

# Run playbook in container (ensure docker image is up-to-date)
playbook: docker-build
	@if [ -z "$(PLAYBOOK)" ]; then \
		echo "Error: PLAYBOOK parameter is required. Usage: make playbook PLAYBOOK=examples/your_playbook.yml"; \
		exit 1; \
	fi
	$(DC_RUN) ansible-playbook --vault-pass-file .vault_pass $(PLAYBOOK) -v

test-integration:
	cd ~/.ansible/collections/ansible_collections/$(COLLECTION_NAMESPACE)/$(COLLECTION_NAME) && \
	ansible-test integration --color --docker

# --- All-in-one targets ---
all: clean build install

.DEFAULT_GOAL := help

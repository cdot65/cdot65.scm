.PHONY: build install clean test lint sanity unit-test integration-test sanity-local unit-test-local integration-test-local test-local dev-setup tox-sanity tox-units tox-integration tox-test tox-flake8 tox-black tox-isort tox-ruff tox-mypy tox-ansible-lint tox-format tox-lint tox-all format lint-all lint-fix run-examples run-example

COLLECTION_NAMESPACE := cdot65
COLLECTION_NAME := scm
COLLECTION_PATH := $(COLLECTION_NAMESPACE)-$(COLLECTION_NAME)

# Basic collection operations
build:
	poetry run ansible-galaxy collection build --force

install: build
	poetry run ansible-galaxy collection install $(COLLECTION_PATH)-*.tar.gz --force

clean:
	rm -f $(COLLECTION_PATH)-*.tar.gz
	rm -rf ~/.ansible/collections/ansible_collections/$(COLLECTION_NAMESPACE)/$(COLLECTION_NAME)

# Linting and formatting
lint:
	poetry run ansible-lint

format:
	poetry run black plugins tests
	poetry run isort plugins tests

lint-all:
	./scripts/lint_and_format.sh || true

lint-check:
	./scripts/check-linting.sh

flake8:
	poetry run flake8 plugins tests

ruff-check:
	poetry run ruff check plugins tests

lint-fix:
	poetry run ruff check --fix plugins tests
	poetry run black plugins tests
	poetry run isort plugins tests

# Testing options with poetry (Docker-based)
sanity:
	cd ~/.ansible/collections/ansible_collections/$(COLLECTION_NAMESPACE)/$(COLLECTION_NAME) && \
	poetry run ansible-test sanity --docker default

unit-test:
	cd ~/.ansible/collections/ansible_collections/$(COLLECTION_NAMESPACE)/$(COLLECTION_NAME) && \
	poetry run ansible-test units --docker default tests/unit/plugins/module_utils/test_scm.py

integration-test:
	cd ~/.ansible/collections/ansible_collections/$(COLLECTION_NAMESPACE)/$(COLLECTION_NAME) && \
	poetry run ansible-test integration --docker default

test: sanity unit-test integration-test

# Testing options with poetry (Local - no Docker)
sanity-local:
	cd ~/.ansible/collections/ansible_collections/$(COLLECTION_NAMESPACE)/$(COLLECTION_NAME) && \
	poetry run ansible-test sanity --local

unit-test-local:
	cd ~/.ansible/collections/ansible_collections/$(COLLECTION_NAMESPACE)/$(COLLECTION_NAME) && \
	poetry run ansible-test units --local tests/unit/plugins/module_utils/test_scm.py

integration-test-local:
	cd ~/.ansible/collections/ansible_collections/$(COLLECTION_NAMESPACE)/$(COLLECTION_NAME) && \
	poetry run ansible-test integration --local

test-local: sanity-local unit-test-local

# Tox testing (with multiple Python/Ansible versions)
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

# Development setup
dev-setup:
	poetry install
	poetry run python -m pip install -r test-requirements.txt

# Example runs
example:
	poetry run ansible-playbook docs/examples/folder_management.yml

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
	@if [ ! -f "examples/$(EXAMPLE).yml" ]; then \
		echo "Error: examples/$(EXAMPLE).yml not found"; \
		exit 1; \
	fi
	@echo "Running examples/$(EXAMPLE).yml"
	poetry run ansible-playbook --vault-pass-file .vault_pass examples/$(EXAMPLE).yml

test-integration:
	poetry run ansible-test integration --color --docker

# All-in-one targets
all: clean build install

.DEFAULT_GOAL := build

.PHONY: build install clean test lint sanity unit-test integration-test dev-setup tox-sanity tox-units tox-integration format

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

# Testing options with poetry
sanity:
	poetry run ansible-test sanity --docker default

unit-test:
	cd ~/.ansible/collections/ansible_collections/$(COLLECTION_NAMESPACE)/$(COLLECTION_NAME) && \
	poetry run ansible-test units --docker default tests/unit/plugins/module_utils/test_scm.py

integration-test:
	cd ~/.ansible/collections/ansible_collections/$(COLLECTION_NAMESPACE)/$(COLLECTION_NAME) && \
	poetry run ansible-test integration --docker default

test: sanity unit-test integration-test

# Tox testing (with multiple Python/Ansible versions)
tox-sanity:
	poetry run tox -e sanity

tox-units:
	poetry run tox -e py312-ansible2.14

tox-integration:
	poetry run tox -e integration

tox: tox-sanity tox-units tox-integration

# Development setup
dev-setup:
	poetry install
	poetry run python -m pip install -r test-requirements.txt

# Example run
example:
	poetry run ansible-playbook docs/examples/folder_management.yml

test-integration:
	poetry run ansible-test integration --color --docker

# All-in-one targets
all: clean build install

.DEFAULT_GOAL := build

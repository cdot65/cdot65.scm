# TODO: cdot65.scm Ansible Collection Development (MVP)

This document outlines the development tasks required to create the initial Minimum Viable Product (MVP) release of the `cdot65.scm` Ansible collection.

The amazon.aws collection as a starting point provides a good example and can be found in the tmp/amazon.aws directory.

## Phase 1: Foundation & Setup

-   [ ] The amazon.aws collection as a starting point provides a good example and can be found in the tmp/amazon.aws directory.
-   [ ] Initialize Collection Directory Structure (mirroring `amazon.aws` conventions: `plugins/modules`, `plugins/module_utils`, `docs`, `tests`, etc.). The amazon.aws collection as a starting point provides a good example and can be found in the tmp/amazon.aws directory.
-   [ ] Create initial `galaxy.yml` file defining collection metadata (namespace: `cdot65`, name: `scm`, dependencies: `pan-scm-sdk==0.3.25`, ansible-core version, python version).
-   [ ] Set up basic testing infrastructure (e.g., `ansible-test sanity` configuration, placeholder for unit/integration tests).
-   [ ] Establish baseline `README.md` with collection purpose and initial installation instructions.
-   [ ] Define and document parameter naming conventions to be used across all modules.
-   [ ] Define and document standard return value structures for modules.

## Phase 2: Core Utilities (`module_utils`)

-   [ ] Develop `module_utils` component for SCM API client initialization.
-   [ ] The amazon.aws collection as a starting point provides a good example and can be found in the tmp/amazon.aws directory.
-   [ ] Implement API Key authentication logic within `module_utils`, supporting retrieval from module parameters and environment variables (`SCM_API_KEY`, `SCM_API_URL`).
-   [ ] Implement standardized error handling within `module_utils` to translate SDK/API errors into Ansible `fail_json` messages.
-   [ ] Implement helper functions in `module_utils` for common SCM interactions needed by multiple modules (e.g., object lookup by name/ID, checking existence).
-   [ ] Write unit tests for core `module_utils` functions (authentication, error handling, helpers).

## Phase 3: Module Implementation (MVP Resources & Actions)

**Note:** Each module implementation includes ensuring idempotency, check mode support, standard parameter handling, correct return values, and basic docstrings.

-   [ ] Implement `scm_folder` module (`state: present`, `state: absent`).
-   [ ] Implement `scm_folder_info` module.
-   [ ] Implement `scm_snippet` module (`state: present`, `state: absent`).
-   [ ] Implement `scm_snippet_info` module.
-   [ ] Implement `scm_config_scope` module (`state: present`, `state: absent`).
-   [ ] Implement `scm_config_scope_info` module.
-   [ ] Implement `scm_device` module (basic `state: present` for onboarding if feasible, `state: absent`).
-   [ ] Implement `scm_device_info` module.
-   [ ] Implement `scm_address_object` module (`state: present`, `state: absent`).
-   [ ] Implement `scm_address_object_info` module.
-   [ ] Implement `scm_address_group` module (`state: present`, `state: absent`).
-   [ ] Implement `scm_address_group_info` module.
-   [ ] Implement `scm_service_object` module (`state: present`, `state: absent`).
-   [ ] Implement `scm_service_object_info` module.
-   [ ] Implement `scm_service_group` module (`state: present`, `state: absent`).
-   [ ] Implement `scm_service_group_info` module.
-   [ ] Implement `scm_deployment` action module (trigger push/deployment).
-   [ ] Implement `scm_job_info` action module (check job status).

## Phase 4: Testing (Integration)

-   [ ] Set up integration test environment (e.g., using Molecule, defining required SCM test instance access).
-   [ ] Write integration tests for `scm_folder` / `scm_folder_info`.
-   [ ] Write integration tests for `scm_snippet` / `scm_snippet_info`.
-   [ ] Write integration tests for `scm_config_scope` / `scm_config_scope_info`.
-   [ ] Write integration tests for `scm_device` / `scm_device_info`.
-   [ ] Write integration tests for `scm_address_object` / `scm_address_object_info`.
-   [ ] Write integration tests for `scm_address_group` / `scm_address_group_info`.
-   [ ] Write integration tests for `scm_service_object` / `scm_service_object_info`.
-   [ ] Write integration tests for `scm_service_group` / `scm_service_group_info`.
-   [ ] Write integration tests for `scm_deployment`.
-   [ ] Write integration tests for `scm_job_info`.
-   [ ] Ensure all integration tests cover create, update (where applicable), delete, info gathering, and check mode functionality.

## Phase 5: Documentation & Examples

-   [ ] Write complete Ansible docstrings for all implemented MVP modules (Synopsis, Parameters, Notes, Examples, Return Values).
-   [ ] Update `README.md` with detailed authentication instructions (API Key, environment variables, precedence).
-   [ ] Update `README.md` with basic usage examples.
-   [ ] Create example playbooks in the `docs/examples/` directory demonstrating common use cases for MVP modules.
-   [ ] Add contribution guidelines to `README.md` or a separate `CONTRIBUTING.md`.
-   [ ] Document collection dependencies clearly in `README.md`.

## Phase 6: Final Checks & Release Prep

-   [ ] Run `ansible-test sanity` and resolve all reported issues.
-   [ ] Perform code review focusing on consistency, security (credential handling), and adherence to Ansible best practices.
-   [ ] Verify all MVP requirements from the PRD ([Section 4.1](#41-in-scope-initial-release---mvp)) are met.
-   [ ] Verify all MVP Release Criteria ([Section 9](#9-release-criteria-mvp)) are met.
-   [ ] Prepare final `galaxy.yml` for release.
-   [ ] Build the collection artifact (`ansible-galaxy collection build`).
-   [ ] (Optional but Recommended) Test installation of the built artifact (`ansible-galaxy collection install <artifact>`).
-   [ ] Tag the release in version control.
-   [ ] Publish the collection to Ansible Galaxy.

---

*Note: Tasks related to future scope items (Inventory Plugins, Lookup Plugins, additional resources, etc.) are deferred until after the MVP release.*
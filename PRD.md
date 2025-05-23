# PRD: Ansible Collection - cdot65.scm (Strata Cloud Manager Integration)

**Version:** 1.2
**Date:** 2025.05.15
**Author:** Calvin Remsburg
**Status:** In Development

---

## Table of Contents

1.  [Introduction](#1-introduction)
2.  [Goals](#2-goals)
3.  [Target Audience / User Personas](#3-target-audience--user-personas)
4.  [Scope](#4-scope)
    *   [In Scope (Initial Release - MVP)](#41-in-scope-initial-release---mvp)
    *   [In Scope (Future Releases)](#42-in-scope-future-releases)
    *   [Out of Scope](#43-out-of-scope)
5.  [Requirements & Features](#5-requirements--features)
    *   [5.1 Collection Structure & Philosophy](#51-collection-structure--philosophy)
    *   [5.2 Core Modules (Resource Management)](#52-core-modules-resource-management)
    *   [5.3 Action/Operational Modules](#53-actionoperational-modules)
    *   [5.4 Supporting Plugins](#54-supporting-plugins)
    *   [5.5 Authentication](#55-authentication)
    *   [5.6 Idempotency & Check Mode](#56-idempotency--check-mode)
    *   [5.7 Error Handling & Reporting](#57-error-handling--reporting)
6.  [Non-Functional Requirements](#6-non-functional-requirements)
    *   [6.1 Usability](#61-usability)
    *   [6.2 Performance](#62-performance)
    *   [6.3 Security](#63-security)
    *   [6.4 Reliability](#64-reliability)
    *   [6.5 Testability](#65-testability)
    *   [6.6 Maintainability](#66-maintainability)
    *   [6.7 Documentation](#67-documentation)
    *   [6.8 SDK Model Standards](#68-sdk-model-standards)
7.  [Design & Implementation Considerations](#7-design--implementation-considerations)
    *   [7.1 SDK Dependency](#71-sdk-dependency)
    *   [7.2 Module Design Pattern](#72-module-design-pattern)
    *   [7.3 Parameter Naming Conventions](#73-parameter-naming-conventions)
    *   [7.4 Return Values](#74-return-values)
8.  [Dependencies](#8-dependencies)
9.  [Current Status & Implementation Progress](#9-current-status--implementation-progress)
10. [Next Steps & Immediate Tasks](#10-next-steps--immediate-tasks)
11. [Future Considerations](#11-future-considerations)
12. [Open Issues / Questions](#12-open-issues--questions)
13. [Recent Progress](#13-recent-progress)

---

## 1. Introduction

This document outlines the requirements for a new Ansible collection, `cdot65.scm`. This collection will provide Ansible modules, plugins, and potentially roles to enable users to interact with and manage Palo Alto Networks' Strata Cloud Manager (SCM) platform. The goal is to allow users to automate SCM configuration, deployment, and operational tasks using familiar Ansible workflows, promoting Infrastructure as Code (IaC) practices for SCM environments.

The development philosophy and structure will closely mirror established Ansible collections like `ansible.aws` to provide a familiar and consistent user experience for Ansible users.

## 2. Goals

*   **Automate SCM Management:** Enable users to automate the configuration and management of SCM resources (e.g., Folders, Snippets, Devices, Configuration Scopes, Deployments).
*   **Provide Idempotent Operations:** Ensure modules operate idempotently, allowing playbooks to be run multiple times with the same predictable outcome.
*   **Integrate with Ansible Ecosystem:** Allow seamless integration of SCM management into broader Ansible automation workflows (e.g., provisioning infrastructure, deploying applications, managing security policies).
*   **Familiar User Experience:** Adhere to Ansible best practices and mirror the structure/feel of popular collections like `ansible.aws`.
*   **Leverage Official SDK:** Utilize the `pan-scm-sdk` for reliable and maintainable interaction with the SCM API.
*   **Support Modern Development Practices:** Utilize Poetry for dependency management and build processes to ensure consistent development environments.

## 3. Target Audience / User Personas

*   **Network Engineers:** Managing network configurations, device onboarding, and policy deployments within SCM.
*   **Security Engineers:** Automating security policy management, compliance checks, and threat response configurations via SCM.
*   **DevOps/Automation Engineers:** Integrating SCM management into CI/CD pipelines and larger infrastructure automation scripts.
*   **Cloud Administrators:** Managing SCM resources as part of a broader cloud environment managed by Ansible.

Users are expected to be familiar with Ansible concepts (playbooks, modules, roles, inventory) and have a working knowledge of Strata Cloud Manager concepts and objects.

## 4. Scope

### 4.1 In Scope (Initial Release - MVP)

The initial release focuses on core SCM objects and actions, with a strong emphasis on robust, reusable Ansible module patterns for each resource type. All new resource modules will follow the folder/folder_info design as the canonical template for structure, authentication, and serialization.

*   **Resource Modules (`_info` and main stateful modules):**
    *   Folders (`folder`, `folder_info`) — Complete ✅
    *   Labels (`label`, `label_info`) — Complete ✅
    *   Snippets (`snippet`, `snippet_info`) — Complete ✅
    *   Devices (`device_info`) — Complete ✅ (read-only operations due to SCM API limitations)
    *   Variables (`variable`, `variable_info`) — Complete ✅
    *   Address Objects (`address`, `address_info`) — Complete ✅
    *   Address Groups (`address_group`, `address_group_info`) — Complete ✅
    *   Application Objects (`application`, `application_info`) — Complete ✅
    *   Application Groups (`application_group`, `application_group_info`) — Complete ✅
    *   Application Filters (`application_filter`, `application_filter_info`) — Complete ✅
    *   Dynamic User Groups (`dynamic_user_group`, `dynamic_user_group_info`) — Complete ✅
    *   External Dynamic Lists (`external_dynamic_list`, `external_dynamic_list_info`) — Complete ✅
    *   Host Information Profiles (`hip_object`, `hip_object_info`) — Complete ✅
    *   HIP Profiles (`hip_profile`, `hip_profile_info`) — Complete ✅
    *   HTTP Server Profiles (`http_server_profile`, `http_server_profile_info`) — Complete ✅
    *   Log Forwarding Profiles (`log_forwarding_profile`, `log_forwarding_profile_info`) — Complete ✅
    *   Quarantined Devices (`quarantined_devices`, `quarantined_devices_info`) — In Progress
    *   Service Objects (`service_object`, `service_object_info`)
    *   Service Groups (`service_group`, `service_group_info`)
*   **Action Modules:**
    *   Trigger Configuration Push/Deployment (`deployment`)
    *   Check Job Status (`job_info`)
*   **Authentication:** Support for multiple authentication methods, including OAuth2 and bearer token (now implemented, see Progress).
*   **Basic Documentation:** README, module documentation following Ansible standards, simple examples.
*   **Testing Infrastructure:** Unit tests for module utilities, integration tests for core modules.

### 4.2 In Scope (Future Releases)

*   Broader SCM resource coverage (Security Rules, NAT Rules, Regions, Applications, etc.)
*   More complex Device Management operations.
*   Inventory Plugin for dynamic SCM inventory.
*   Lookup Plugins for querying specific SCM data.
*   Enhanced error handling and reporting.
*   Roles for common SCM tasks.

### 4.3 Out of Scope

*   Managing the underlying infrastructure hosting SCM itself.
*   Directly managing individual PAN-OS devices *unless* done via SCM APIs (e.g., configuration pushes). Use `paloaltonetworks.panos` for direct device interaction.
*   Features not exposed by the `pan-scm-sdk` or the SCM API.
*   Providing a graphical user interface.

## 5. Requirements & Features

### 5.1 Collection Structure & Philosophy

*   **Namespace:** `cdot65`
*   **Collection Name:** `scm`
*   **Full Name:** `cdot65.scm`
*   **Structure:** Mirror `ansible.aws` directory structure:
    *   `galaxy.yml`
    *   `README.md`
    *   `plugins/modules/`: Ansible modules
    *   `plugins/module_utils/`: Shared Python code for modules
    *   `plugins/inventory/`: (Future) Inventory plugins
    *   `plugins/lookup/`: (Future) Lookup plugins
    *   `roles/`: (Future) Ansible roles
    *   `docs/`: Collection documentation, examples
    *   `tests/`: Unit and integration tests
*   **Philosophy:** Modules should map closely to SCM API resources/actions, providing granular control. Follow Ansible module development guidelines strictly.
*   **Development Environment:** Use Poetry for dependency management, virtual environment creation, and consistent development workflows.

### 5.2 Core Modules (Resource Management)

*   For each major SCM resource type (e.g., Folder, Snippet, Address Object):
    *   Implement a main stateful module (e.g., `folder`).
        *   Support `state: present` (Create/Update).
        *   Support `state: absent` (Delete).
        *   Parameters should map clearly to SCM resource attributes.
        *   Must be idempotent.
    *   Implement a corresponding `_info` module (e.g., `folder_info`).
        *   Used for gathering information about existing resources without making changes.
        *   Support filtering/querying where possible via the SCM API.

### 5.3 Action/Operational Modules

*   Implement modules for actions that don't map directly to a CRUD resource lifecycle.
    *   Example: `deployment` to trigger a config push to devices/scopes.
    *   Example: `job_info` to query the status of asynchronous operations initiated via SCM.
*   These modules may not always be idempotent in the traditional sense but should report status clearly.

### 5.4 Supporting Plugins

*   **Module Utils:** Create shared Python code in `plugins/module_utils/` for common tasks like:
    *   SCM API client initialization and authentication.
    *   Error handling and mapping SCM API errors to Ansible failures.
    *   Common data manipulation or validation logic.
*   **Inventory Plugin (Future):** Develop a dynamic inventory plugin to source SCM-managed devices or other resources into Ansible inventory.
*   **Lookup Plugin (Future):** Develop lookup plugins for retrieving specific data points from SCM (e.g., lookup an object ID by name).

### 5.5 Authentication

*   Modules must securely handle SCM authentication credentials.
*   **Support Multiple Methods:** 
    *   **OAuth2 Authentication:** Primary method using client_id, client_secret, and TSG ID.
    *   **API Key (Future):** If supported by SCM API.
*   **Credential Handling:** 
    *   Credentials should be passable via:
        1.  Module parameters (e.g., `client_id`, `client_secret`, `tsg_id`, `api_url`).
        2.  Environment variables (e.g., `SCM_CLIENT_ID`, `SCM_CLIENT_SECRET`, `SCM_TSG_ID`, `SCM_API_URL`).
        3.  (Potentially) Ansible configuration files or Vault.
*   Clear documentation on credential precedence and recommended secure practices (use Vault, environment variables).

### 5.6 Idempotency & Check Mode

*   All resource management modules (`state: present`/`absent`) MUST be idempotent. They should check the current state in SCM before attempting changes.
*   Modules MUST accurately report `changed: true` only when a change was actually made to the SCM environment.
*   Modules MUST support Ansible's `check_mode` (`--check`). In check mode, modules should predict changes without actually making them and report `changed: true` if a change *would* have occurred.

### 5.7 Error Handling & Reporting

*   Modules MUST gracefully handle errors from the `pan-scm-sdk` and the SCM API.
*   API errors should be translated into informative Ansible failure messages (`module.fail_json(...)`).
*   Include relevant details in error messages (e.g., SCM error codes/messages, resource identifiers).
*   Return informative messages on success, including relevant resource details.

## 6. Non-Functional Requirements

### 6.1 Usability

*   Module parameters should be clearly named and documented.
*   Consistent parameter naming across modules (e.g., `state`, `name`, identifiers).
*   Provide clear examples in module documentation.
*   Return values should be useful and predictable.

### 6.2 Performance

*   Modules should execute in a reasonable timeframe.
*   Avoid unnecessary API calls. Leverage SDK features for efficiency.
*   Consider pagination and filtering for `_info` modules handling large datasets.

### 6.3 Security

*   Prioritize secure handling of authentication credentials (as outlined in [5.5 Authentication](#55-authentication)).
*   Use `no_log: True` for sensitive parameters.
*   Avoid logging sensitive information unless explicitly enabled for debugging.
*   Code should be reviewed for potential security vulnerabilities.

### 6.4 Reliability

*   Modules should be robust against transient API issues where possible (e.g., through retries if appropriate, though often handled by SDK).
*   Idempotency must be rigorously tested.

### 6.5 Testability

*   Develop unit tests for `module_utils` code.
*   Develop integration tests that run against a live (test) SCM instance or a mocked environment. Integration tests should cover common use cases (create, update, delete, gather info, check mode).
*   Tests should be runnable within standard CI/CD pipelines (e.g., GitHub Actions, Molecule).
*   Support testing via Docker containers for consistent test environments.

### 6.6 Maintainability

*   Code should follow Python best practices (PEP 8).
*   Use Poetry for dependency management and development environment consistency.
*   Code should be well-commented, especially complex logic.
*   Use `module_utils` effectively to avoid code duplication.
*   Keep the `pan-scm-sdk` dependency updated as needed.
*   Use static analysis tools like ruff, ansible-lint, and yamllint.

### 6.7 Documentation

*   **Collection `README.md`:** Overview, installation instructions, authentication guide, contribution guidelines.
*   **Module Documentation:** Standard Ansible doc strings for every module, including:
    *   Synopsis
    *   Parameters (type, description, required, choices, default)
    *   Notes
    *   Examples (practical use cases)
    *   Return values
*   **Examples Directory:** Include example playbooks demonstrating common workflows.

## 7. Design & Implementation Considerations

### 7.1 SDK Dependency

*   The collection MUST use the latest version of the SCM Python SDK built on Pydantic for all interactions with the SCM API.
*   The SDK provides data models and service functions for API interactions, which should be leveraged in the collection.
*   Abstract SDK usage within `module_utils` to simplify module code and facilitate future SDK updates.
*   Some SCM API endpoints require special handling for boolean fields:
    * For many resources (e.g., application_filter), boolean fields should only be included in API requests when set to `True`.
    * Setting boolean fields to `False` can cause API validation errors in some endpoints.
    * Modules should implement special handling for boolean fields: only adding `True` values to payloads and omitting `False` values.

### 7.2 Module Design Pattern

*   Follow the standard Ansible module structure (using `AnsibleModule` from `ansible.module_utils.basic`).
*   Encapsulate SCM interaction logic within helper functions or classes in `module_utils`.
*   Modules should primarily handle parameter parsing, calling `module_utils` functions, and formatting results/errors.
*   Use a consistent client module pattern for SDK interactions.

### 7.3 Parameter Naming Conventions

*   Use `state` with `present`/`absent` for resource lifecycle management.
*   Use descriptive names matching SCM concepts where possible, converted to `snake_case`.
*   Be consistent with identifier parameters (e.g., `name`, `folder`, `snippet`, `id`).
*   Authentication parameters should align with SDK/environment variable conventions.

### 7.4 Return Values

*   Modules should return standard Ansible results (e.g., `changed`, `failed`, `msg`).
*   On success, return relevant information about the resource(s) managed or queried (e.g., resource ID, attributes). Use a predictable key (e.g., `resource`, `facts`).
*   `_info` modules should return found resources under a consistent key (e.g., `resources`, `folders`, `snippets`).

## 8. Dependencies

*   **Ansible:** `ansible-core >= 2.14` 
*   **Python:** `python >= 3.7` (with support up to Python 3.12)
*   **Palo Alto Networks SDK:** `pan-scm-sdk >= 0.3.25`
*   **Development Environment:** Poetry 2.1.1
*   **Testing & Quality Tools:** ansible-lint, yamllint, ruff, isort

## 9. Current Status & Implementation Progress

**Completed:**
- Folder management modules (`folder`, `folder_info`) fully implemented with modern authentication (bearer token), robust serialization (Pydantic `.model_dump_json()`), and idempotent CRUD/query workflows. These serve as the reference for all future resource modules.
- Label management modules (`label`, `label_info`) fully implemented.
- Snippet management modules (`snippet`, `snippet_info`) fully implemented.
- Device information module (`device_info`) implemented for read-only operations with display_name search support.
- Variable management modules (`variable`, `variable_info`) fully implemented.
- Address object modules (`address`, `address_info`) fully implemented.
- Address group modules (`address_group`, `address_group_info`) fully implemented with support for both static and dynamic address groups.
- Application modules (`application`, `application_info`) fully implemented with support for application categorization and risk attributes.
- Application group modules (`application_group`, `application_group_info`) fully implemented with support for static application groups and references.
- Application filter modules (`application_filter`, `application_filter_info`) fully implemented with proper handling of boolean fields.
- Dynamic user group modules (`dynamic_user_group`, `dynamic_user_group_info`) fully implemented with tag-based filter expressions.
- External dynamic list modules (`external_dynamic_list`, `external_dynamic_list_info`) fully implemented with support for URL-based external lists.
- Authentication role and workflow complete; token can be passed to all modules.
- Example playbooks for all implemented modules.
- Comprehensive README documentation with module matrix and usage examples.

**In Progress / Next:**
- Implement Quarantined Devices modules (quarantined_devices, quarantined_devices_info) - PRIORITY FOCUS
  - Module design following established patterns from folder, address, application modules
  - Support for container-based resource management (folder, snippet, device)
  - Rich filtering capabilities for the info module
  - Complete CRUD operations for managing quarantined device configurations
- Implement Service objects modules (service_object, service_object_info).
- Implement Service Group modules (service_group, service_group_info).
- Expand test coverage for recently added modules.
- Standardize all other info modules to follow the same pattern as folder_info/device_info.
- Expand test coverage and integration tests for all modules.
- Add integration tests for the dynamic_user_group and external_dynamic_list modules.

**Blocked/Issues:**
- None major; dependency and serialization issues resolved.
- Device management limited to read-only operations due to SCM API constraints.

## 10. Next Steps & Immediate Tasks

- Implement `quarantined_devices` and `quarantined_devices_info` modules for managing quarantined device configurations in SCM.
- Add integration tests for quarantined_devices modules.
- Create comprehensive example playbooks for quarantined_devices management.
- Document quarantined device operations and container-based resource management.
- Add support for quarantine reasons, timestamps, and status management.
- Implement filtering capabilities for quarantined_devices_info module.
- Update module inventory and documentation to reflect quarantined_devices implementation.
- After quarantined_devices, implement `service_object` and `service_object_info` modules for service object management.
- Continue to enhance documentation and examples with real-world use cases.

## 11. Future Considerations

*   Explore integration with Ansible Vault for credential management.
*   Investigate advanced SCM features (e.g., template stacks, insights API).
*   Community feedback collection and incorporation.
*   Regular updates to align with new SCM API features and SDK releases.
*   Potential certification by Palo Alto Networks or Red Hat.
*   CI/CD integration for automated testing and deployment.

## 12. Open Issues / Questions

*   Are there specific SCM API rate limits to consider in module design?
*   What is the best approach for handling potentially long-running asynchronous jobs (e.g., deployments) in Ansible modules? (Polling, async status checks?)
*   How to best handle pagination for large resource collections?
*   Most effective approach for testing modules against real SCM instances versus mocked responses?

## 13. Recent Progress

- Beginning implementation of Quarantined Devices modules (`quarantined_devices`, `quarantined_devices_info`) as the next priority for the collection.
- Implemented Log Forwarding Profile modules (`log_forwarding_profile`, `log_forwarding_profile_info`) for managing log forwarding configurations and match lists.
- Created comprehensive example playbooks for log forwarding profile creation, update, and filtering.
- Fixed HTTP server profile modules with proper handling of URL format field mapping between Ansible module (`uri_format`) and SDK model (`url_format`).
- Updated the `http_server_profile_info.py` module to use client-side filtering for protocol and tag registration status due to API limitations.
- Resolved issue with invalid certificate profile references by updating documentation and removing default values.
- Added authentication parameters to all example playbook tasks to ensure proper authentication.
- Updated documentation in both the module and example playbooks to clarify proper usage.
- Completed all HTTP server profile-related tasks with comprehensive examples.
- Updated documentation to reflect completed modules and new priorities for service object implementation.
- Implemented `hip_profile` and `hip_profile_info` modules for managing Host Information Profiles.
- Created comprehensive example playbooks for HIP profiles demonstrating various match expressions (AND, OR, NOT, nested).
- Supported match expressions using boolean logic to reference HIP objects for security policy use.
- Implemented robust validation and error handling for match expressions.
- Added container-based profile management (folder, snippet, device) with proper validation.
- Implemented `hip_object` and `hip_object_info` modules for managing Host Information Profile (HIP) objects.
- Created example playbooks for HIP object management and retrieval with comprehensive examples.
- Implemented support for all HIP criteria types (host_info, network_info, patch_management, disk_encryption, mobile_device, certificate).
- Added support for complex criteria specifications with proper nesting and validation.
- Fixed error in `external_dynamic_list_info` module related to filtering by list types, specifically addressing the "'NoneType' object has no attribute '__dict__'" error.
- Improved type checking in modules by using model_dump_json for safer serialization and comparison.
- Followed the established pattern for other resource modules with robust error handling and validation.
- Updated documentation (README.md, modules.md, TODO.md, PRD.md) to reflect completion of new modules.
- Updated development roadmap to focus on service_object modules as our next implementation target.
- Implemented `dynamic_user_group` and `dynamic_user_group_info` modules for managing tag-based dynamic user groups.
- Created comprehensive example playbooks demonstrating dynamic user group creation, filtering, and management.
- Followed the established pattern for other resource modules with robust error handling and validation.
- Updated documentation to reflect completion of the dynamic_user_group modules.
- Changed focus from config_scope modules to dynamic_user_group modules based on priority needs.
- Completed implementation of `application_filter` and `application_filter_info` modules for filtering applications based on criteria.
- Added special handling for boolean fields in application_filter module to handle API requirements (only True values are sent to the API).
- Implemented `application_group` and `application_group_info` modules with support for static application groups.
- Determined that dynamic application groups in SCM must reference existing static groups as filters.
- Updated documentation to clarify proper usage patterns for application groups.
- Created example playbooks demonstrating both static and reference-based application groups.
- Implemented `application` and `application_info` modules with support for application categorization and risk attributes.
- Enhanced `device_info` module to use display_name for name searches, improving usability.
- Fixed response format handling in device_info module to properly process the nested data structure from SCM API.
- Improved error handling for API response formats across all modules.
- Implemented `address_group` and `address_group_info` modules (create/retrieve both static and dynamic address groups).
- Added support for static address groups with member management and dynamic address groups with filter expressions.
- Created comprehensive example playbooks for all modules with various usage patterns.
- Added support for multiple filter types in address_group_info and application_info modules.
- Standardized container-based resource handling (folder, snippet, device) across all network object modules.
- Added consistent error handling and parameter validation across modules.
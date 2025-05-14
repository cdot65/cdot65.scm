# TODO: cdot65.scm Ansible Collection (Strata Cloud Manager)

_Last updated: 2025-05-16_

## Immediate Tasks

- [x] Implement authentication role (`roles/auth`)
    - [x] Example playbook at `playbooks/auth.yml`
- [x] Implement folder management module:
    - [x] `plugins/modules/folder.py` (CRUD operations for SCM folders)
    - [x] `plugins/modules/folder_info.py` (query/info for SCM folders)
- [x] Example playbooks for folder and folder_info modules
- [x] Resolve serialization issues (UUIDs, Pydantic)
- [x] Implement label management modules (template: folder modules):
    - [x] `plugins/modules/label.py`
    - [x] `plugins/modules/label_info.py`
- [x] Implement snippet management modules (template: folder modules):
    - [x] `plugins/modules/snippet.py`
    - [x] `plugins/modules/snippet_info.py`
- [x] Implement device management modules:
    - [x] `plugins/modules/device_info.py` (read-only operations for SCM devices)
- [x] Implement variable management modules (template: folder modules):
    - [x] `plugins/modules/variable.py`
    - [x] `plugins/modules/variable_info.py`
- [x] Update README documentation with module matrix and examples
- [x] Implement address object management modules:
    - [x] `plugins/modules/address.py`
    - [x] `plugins/modules/address_info.py`
- [x] Implement address group management modules:
    - [x] `plugins/modules/address_group.py`
    - [x] `plugins/modules/address_group_info.py`
- [x] Implement application management modules:
    - [x] `plugins/modules/application.py`
    - [x] `plugins/modules/application_info.py`
- [x] Implement application group management modules:
    - [x] `plugins/modules/application_group.py`
    - [x] `plugins/modules/application_group_info.py`
- [x] Implement application filter management modules:
    - [x] `plugins/modules/application_filter.py`
    - [x] `plugins/modules/application_filter_info.py`
- [x] Implement dynamic user group management modules:
    - [x] `plugins/modules/dynamic_user_group.py`
    - [x] `plugins/modules/dynamic_user_group_info.py`
- [x] Implement external dynamic list management modules:
    - [x] `plugins/modules/external_dynamic_list.py`
    - [x] `plugins/modules/external_dynamic_list_info.py`
- [ ] Enhance error handling for all modules with consistent patterns
- [ ] Create integration tests for all resource modules

## Short-term Goals (MVP)

- [x] Implement host information profile modules (`hip_object`, `hip_object_info`)
- [ ] Implement service object modules (`service_object`, `service_object_info`) 
- [ ] Implement service group modules (`service_group`, `service_group_info`)
- [ ] Develop comprehensive test coverage (unit + integration)
- [ ] Create example playbooks for all resource types
- [ ] Enhance documentation with real-world usage patterns
- [ ] Ensure all modules support idempotency and check_mode

## Process & Quality Reminders

- Use `poetry run` for all build, test, and lint commands (see Makefile)
- Maintain dependency management with Poetry (pyproject.toml)
- Use ruff, ansible-lint, yamllint, and isort for code quality
- All sensitive parameters must use `no_log: true`
- All info modules should follow consistent error handling pattern
- Use Pydantic's model_dump_json(exclude_unset=True) for serialization
- Follow standardized parameter naming and usage across all modules
- Update examples directory with each new module implementation
- For modules with boolean fields (like application_filter):
  - Only include boolean fields that are True in API requests
  - Do not attempt to set boolean fields to False as this can cause validation errors
  - When updating existing resources, only include boolean fields that should be True
  - Document this behavior in the module description and examples

## [2025-05-16] Host Information Profile (HIP) Modules Completed

- Implemented hip_object.py and hip_object_info.py modules for HIP object management
- Created comprehensive example playbooks demonstrating HIP object creation, modification, and querying
- Implemented support for all HIP criteria types (host_info, network_info, patch_management, disk_encryption, mobile_device, certificate)
- Added support for complex nested criteria structures with proper validation
- Followed the established pattern for other resource modules with robust error handling and validation
- Added support for multiple container types (folder, snippet, device)
- Created example playbooks that demonstrate idempotency, filtering capabilities, and proper cleanup
- Added comprehensive filtering by criteria types and container context in the info module
- Added consistent documentation in the modules and example playbooks
- Updated module inventory and workflow pattern documentation
- Next focus will be on implementing service_object and service_object_info modules

## [2025-05-15] External Dynamic List Modules Completed

- Fixed critical issue in external_dynamic_list_info.py related to filtering by list types
- Implemented safer type checking with model_dump_json to handle None values properly
- Completely implemented external_dynamic_list.py and external_dynamic_list_info.py modules
- Created comprehensive example playbooks demonstrating external dynamic list creation and management
- Implemented support for all EDL types (predefined_ip, predefined_url, ip, domain, url, imsi, imei)
- Added support for complex recurring schedule configurations (five_minute, hourly, daily, weekly, monthly)
- Followed the established pattern for other resource modules with robust error handling and validation
- Added support for multiple container types (folder, snippet, device)
- Created example playbooks that demonstrate idempotency, filtering capabilities, and proper cleanup
- Added comprehensive filtering by list type, URL, and container context in the info module
- Added consistent documentation in the modules and example playbooks
- Updated module inventory and workflow pattern documentation

## [2025-05-13] Dynamic User Group Modules Completed

- Implemented dynamic_user_group.py and dynamic_user_group_info.py modules
- Created comprehensive example playbooks demonstrating dynamic user group creation, filtering, and management
- Implemented tag-based filter expressions support for user matching
- Followed the established pattern for other resource modules with robust error handling and validation
- Added support for multiple container types (folder, snippet, device)
- Created example playbooks that demonstrate idempotency, filtering capabilities, and proper cleanup
- Added consistent documentation in the modules and example playbooks
- Updated module inventory and workflow pattern documentation
- Next focus will be on implementing external_dynamic_list and external_dynamic_list_info modules

## [2025-05-13] Application Filter Modules Completed

- Implemented application_filter.py and application_filter_info.py modules
- Added special handling for boolean fields in SCM API (only sending True values)
- Created comprehensive example playbooks demonstrating various filter criteria combinations
- Fixed subcategory parameter handling with proper SCM API field mapping (sub_category)
- Improved module documentation to clarify usage patterns and required parameters
- Handled cleanup operations in playbooks with separate tasks for different container types
- Follows the same pattern established for other resource modules (folder, address, etc.)
- Updated documentation (README.md, modules.md, TODO.md, PRD.md) to reflect module completion
- Changed focus from config_scope modules to dynamic_user_group modules as the next priority

## Open Issues / Watch Items

- Confirm and document minimum supported ansible-core and Python versions
- Monitor for SCM API/SDK changes and update dependencies as needed
- Assess SCM API rate limits and async job handling strategies
- Plan for future: Vault integration, inventory/lookup plugins, CI/CD automation

## [2025-05-11] Application Group Modules Completed

- Implemented application_group.py module with support for static application groups
- Implemented application_group_info.py module with comprehensive filtering capabilities
- Discovered that dynamic application groups in SCM must reference existing application groups
- Updated documentation to clarify proper usage patterns for application groups
- Created example playbooks demonstrating static application groups and group references
- Added application group filtering by type, member, and tags
- Standardized serialization, error handling, and parameter validation

## [2025-05-11] Address Group Modules Completed

- Implemented address_group.py module with support for both static and dynamic address groups
- Implemented address_group_info.py module with comprehensive filtering capabilities
- Added example playbooks for address_group and address_group_info modules
- Standardized container-based resource handling for all network object modules
- Consistent error handling and parameter validation across modules
- Both static (list of addresses) and dynamic (filter expression) address groups are supported
- All modules maintain the established pattern for SCM resource management

## [2025-05-11] Application Modules and Device Info Enhancement

- Implemented application.py and application_info.py modules
- Enhanced device_info.py to search by display_name instead of internal name
- Fixed device_info.py to properly handle the SCM API response structure with pagination
- Added pagination metadata (limit, offset, total) to device_info response
- Improved error handling for API response formats across info modules
- Created example playbooks demonstrating application and display_name lookup usage

## [2025-05-15] Info Modules - Standardized Error Handling and Client Usage

- All info modules now follow a consistent pattern for client initialization, error handling, and result formatting
- Standardized approach for getting resources by ID versus list filtering
- Unified exception handling with specific patterns for different error types
- Consistent serialization using `model_dump_json(exclude_unset=True)` + `json.loads()` for all SCM objects
- Added folder parameter requirement validation for variable modules when getting by name
- All example playbooks updated to demonstrate proper usage patterns
- Comprehensive README documentation with module matrix and usage examples

## [2025-05-10] plugins/modules/folder.py - Workflow & Serialization Improvements

- Refactored the module to keep Pydantic model objects (`folder_obj`) native throughout workflow, only serializing for Ansible output.
- Switched all result serialization to use `model_dump_json(exclude_unset=True)` + `json.loads()` for folder objects.
    - This ensures UUIDs and other non-JSON-serializable types are always safely converted to strings for Ansible.
    - Prevents fatal errors from UUID serialization when returning results.
- Removed previous manual UUID conversion logic and unnecessary uses of `serialize_as_any`.
- Improved code maintainability and robustness by leveraging Pydantic's JSON encoder for all output.
- This pattern should be adopted for other modules returning Pydantic models to Ansible.

---

Refer to [PRD.md](./PRD.md) for full requirements, design, and future considerations.
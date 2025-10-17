# Development TODO

Priority list for implementing remaining `pan-scm-sdk` object resources in the `cdot65.scm` Ansible collection.

## Current Implementation Status

### ✅ Completed Modules

| Resource | Module | Info Module | SDK Support |
|----------|--------|-------------|-------------|
| Address | ✅ | ✅ | ✅ |
| Address Group | ✅ | ✅ | ✅ |
| Application | ✅ | ✅ | ✅ |
| Application Group | ✅ | ✅ | ✅ |
| Application Filter | ✅ | ✅ | ✅ |
| Dynamic User Group | ✅ | ✅ | ✅ |
| External Dynamic List | ✅ | ✅ | ✅ |
| Folder | ✅ | ✅ | ✅ |
| HIP Object | ✅ | ✅ | ✅ |
| HIP Profile | ✅ | ✅ | ✅ |
| HTTP Server Profile | ✅ | ✅ | ✅ |
| Label | ✅ | ✅ | ✅ |
| Service | ✅ | ✅ | ✅ |
| Service Group | ✅ | ✅ | ✅ |
| Snippet | ✅ | ✅ | ✅ |
| Tag | ✅ | ✅ | ✅ |
| Variable | ✅ | ✅ | ✅ |
| Region | ✅ | ✅ | ✅ |
| Schedule | ✅ | ✅ | ✅ |
| Device | - | ✅ | ✅ |

### 🔴 Missing Modules (SDK Supported)

The following resources are supported by `pan-scm-sdk` but do not have Ansible modules yet:

## Priority 1: Core Objects ✅ COMPLETED

These are fundamental objects commonly used in security policies and should be prioritized.

- [x] **Service Objects** (`service.py`, `service_info.py`) ✅
  - SDK Models: `ServiceCreateModel`, `ServiceResponseModel`, `ServiceUpdateModel`
  - Template: Used `address.py` as template
  - Complexity: Medium (similar to address objects)
  - Status: Completed and tested

- [x] **Service Groups** (`service_group.py`, `service_group_info.py`) ✅
  - SDK Models: `ServiceGroupCreateModel`, `ServiceGroupResponseModel`, `ServiceGroupUpdateModel`
  - Template: Used `address_group.py` as template
  - Complexity: Medium (similar to address groups)
  - Status: Completed and tested

- [x] **Tags** (`tag.py`, `tag_info.py`) ✅
  - SDK Models: `TagCreateModel`, `TagResponseModel`, `TagUpdateModel`
  - Template: Used `label.py` as template
  - Complexity: Low (similar to labels)
  - Status: Completed and tested

## Priority 2: Application Management ✅ COMPLETED

- [x] **Application Filters** (`application_filter.py`, `application_filter_info.py`) ✅
  - SDK Models: `ApplicationFiltersCreateModel`, `ApplicationFiltersResponseModel`, `ApplicationFiltersUpdateModel`
  - Template: Used `application.py` as template
  - Complexity: Medium
  - Status: Completed

## Priority 3: User and Device Management ✅ COMPLETED

- [x] **Dynamic User Groups** (`dynamic_user_group.py`, `dynamic_user_group_info.py`) ✅
  - SDK Models: `DynamicUserGroupCreateModel`, `DynamicUserGroupResponseModel`, `DynamicUserGroupUpdateModel`
  - Template: Used `address_group.py` as template
  - Complexity: Medium
  - Status: Completed

- [x] **HIP Objects** (`hip_object.py`, `hip_object_info.py`) ✅
  - SDK Models: `HIPObjectCreateModel`, `HIPObjectResponseModel`, `HIPObjectUpdateModel`
  - Template: Used `address.py` as template
  - Complexity: Medium-High (complex nested structures)
  - Status: Completed

- [x] **HIP Profiles** (`hip_profile.py`, `hip_profile_info.py`) ✅
  - SDK Models: `HIPProfileCreateModel`, `HIPProfileResponseModel`, `HIPProfileUpdateModel`
  - Template: Used `address.py` as template
  - Complexity: High (complex nested structures)
  - Status: Completed

## Priority 4: External Resources ✅ COMPLETED

- [x] **External Dynamic Lists** (`external_dynamic_list.py`, `external_dynamic_list_info.py`) ✅
  - SDK Models: `ExternalDynamicListsCreateModel`, `ExternalDynamicListsResponseModel`, `ExternalDynamicListsUpdateModel`
  - Template: Used `address.py` as template
  - Complexity: Medium
  - Status: Completed

- [x] **HTTP Server Profiles** (`http_server_profile.py`, `http_server_profile_info.py`) ✅
  - SDK Models: `HTTPServerProfileCreateModel`, `HTTPServerProfileResponseModel`, `HTTPServerProfileUpdateModel`
  - Template: Used `address.py` as template
  - Complexity: Medium
  - Status: Completed

- [x] **Regions** (`region.py`, `region_info.py`) ✅
  - SDK Models: `RegionCreateModel`, `RegionResponseModel`, `RegionUpdateModel`
  - Additional Models: `GeoLocation`
  - Template: Used `address.py` as template
  - Complexity: Medium (has nested GeoLocation model)
  - Status: Completed and tested

## Priority 5: Scheduling ✅ COMPLETED

- [x] **Schedules** (`schedule.py`, `schedule_info.py`) ✅
  - SDK Models: `ScheduleCreateModel`, `ScheduleResponseModel`, `ScheduleUpdateModel`
  - Template: Used `address.py` as template
  - Complexity: Medium-High (complex nested schedule_type with recurring/non-recurring)
  - Status: Completed and tested

## Priority 6: Logging and Monitoring

- [ ] **HTTP Server Profiles** (`http_server_profile.py`, `http_server_profile_info.py`)
  - SDK Models: `HTTPServerProfileCreateModel`, `HTTPServerProfileResponseModel`, `HTTPServerProfileUpdateModel`
  - Additional Models: `ServerModel`
  - Template: Use `address.py` as template
  - Complexity: Medium-High (nested server configurations)

- [ ] **Syslog Server Profiles** (`syslog_server_profile.py`, `syslog_server_profile_info.py`)
  - SDK Models: `SyslogServerProfileCreateModel`, `SyslogServerProfileResponseModel`, `SyslogServerProfileUpdateModel`
  - Additional Models: `SyslogServerModel`, `FormatModel`, `EscapingModel`
  - Template: Use `address.py` as template
  - Complexity: High (complex nested structures)

- [ ] **Log Forwarding Profiles** (`log_forwarding_profile.py`, `log_forwarding_profile_info.py`)
  - SDK Models: `LogForwardingProfileCreateModel`, `LogForwardingProfileResponseModel`, `LogForwardingProfileUpdateModel`
  - Additional Models: `MatchListItem`
  - Template: Use `address.py` as template
  - Complexity: High (complex nested structures)

## Priority 7: Device Management

- [ ] **Quarantined Devices** (`quarantined_device.py`, `quarantined_device_info.py`)
  - SDK Models: `QuarantinedDevicesCreateModel`, `QuarantinedDevicesResponseModel`
  - Additional Models: `QuarantinedDevicesListParamsModel`
  - Template: Use `address.py` as template
  - Complexity: Medium
  - Note: May be read-only or have special handling

## Implementation Guidelines

For each new module:

1. **Copy Template**: Use appropriate existing module as template
2. **Update Documentation**: Modify DOCUMENTATION, EXAMPLES, and RETURN blocks
3. **Update Parameters**: Match SDK model parameters in `module_args`
4. **Update Client Calls**: Change `client.<resource>` references
5. **Update Imports**: Import correct models from `scm.models.objects`
6. **Test**: Build, install, and test with example playbooks
7. **Lint**: Run `make lint-all` and fix any issues
8. **Create Examples**: Add example playbook to `examples/` directory
9. **Update CLAUDE.md**: Add to resource modules status list

## Estimated Effort

- **Priority 1** (Core Network Objects): ~8-12 hours
- **Priority 2** (Application Management): ~4-6 hours
- **Priority 3** (User and Device Management): ~12-16 hours
- **Priority 4** (External Resources): ~8-10 hours
- **Priority 5** (Scheduling): ~4-6 hours
- **Priority 6** (Logging and Monitoring): ~16-20 hours
- **Priority 7** (Device Management): ~6-8 hours

**Total Estimated Effort**: 58-78 hours

## Quick Wins

Start with these for rapid progress:

1. **Tags** - Very similar to existing label module (2-3 hours)
2. **Service Objects** - Similar to address objects (4-5 hours)
3. **Service Groups** - Similar to address groups (4-5 hours)

These three modules provide immediate value for network security automation.

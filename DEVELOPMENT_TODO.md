# Development TODO

Priority list for implementing remaining `pan-scm-sdk` object resources in the `cdot65.scm` Ansible collection.

## SDK Coverage Status

**SDK Version**: 0.3.44 (Latest)
**Total SDK Services**: 45
**Implemented Modules**: 33 resource types (65 modules total)
**Remaining to Implement**: 12 SDK services (24 potential modules)
**Coverage**: 73% of available SDK services

### SDK Services Not Yet in Collection

The following services are available in pan-scm-sdk v0.3.44 but not yet implemented as Ansible modules:

**Network & VPN (Priority 8):**
- `ike_crypto_profile` - IKE crypto profiles
- `ike_gateway` - IKE gateways
- `ipsec_crypto_profile` - IPsec crypto profiles
- `security_zone` - Security zones
- `bgp_routing` - BGP routing configuration
- `nat_rule` - NAT rules

**Deployment & Infrastructure (Priority 9):**
- `remote_network` - Remote networks
- `service_connection` - Service connections

**Mobile Agent & Other:**
- `agent_version` - Mobile agent versions
- `auth_setting` - Authentication settings
- `auto_tag_action` - Auto tag actions
- `alerts` - Prisma Insights alerts

**Not Available in SDK:**
- ❌ `dns_server_profiles` - Does not exist in current SDK
- ❌ `security_profiles_group` - Does not exist in current SDK

## Current Implementation Status

### ✅ Completed Modules (Current Collection)

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
| Syslog Server Profile | ✅ | ✅ | ⚠️ |
| Quarantined Device | ✅ | ✅ | ⚠️ |
| Log Forwarding Profile | ✅ | ✅ | ✅ |
| Security Rule | ✅ | ✅ | ✅ |
| URL Categories | ✅ | ✅ | ✅ |
| Anti-Spyware Profile | ✅ | ✅ | ✅ |
| Vulnerability Protection Profile | ✅ | ✅ | ✅ |
| WildFire Antivirus Profile | ✅ | ✅ | ✅ |
| Decryption Profile | ✅ | ✅ | ✅ |
| DNS Security Profile | ✅ | ✅ | ✅ |
| Internal DNS Server | ✅ | ✅ | ✅ |
| Security Zone | ✅ | ✅ | ✅ |
| Bandwidth Allocation | ✅ | ✅ | ⚠️ |
| Network Location | - | ✅ | ✅ |
| Device | - | ✅ | ✅ |

**Total Current**: 65 modules (33 types: 32 resource + 33 info modules)

**Notes:**
- ⚠️ Bandwidth Allocation: Update/Delete operations have API limitations in SCM v0.3.44. Create and Read operations work correctly.
- Network Location: Read-only resource (info module only, no CRUD operations available)

### 🔴 Missing Modules (From Previous Collection)

The following modules exist in the previous iteration but need to be ported to this collection:

## Priority 8: Network Configuration & VPN

### Security Zones
- [ ] **Security Zone** (`security_zone.py`, `security_zone_info.py`) 🟢 SDK Available
  - Description: Manage security zones
  - Complexity: Medium
  - SDK Service: `security_zone`
  - SDK Module: `scm.config.network.security_zone.SecurityZone`
  - Template: Use `address.py` as template
  - Status: Available in SDK, ready to implement

### VPN & Crypto
- [ ] **IKE Crypto Profile** (`ike_crypto_profile.py`, `ike_crypto_profile_info.py`) 🟢 SDK Available
  - Description: Manage IKE crypto profiles
  - Complexity: Medium-High
  - SDK Service: `ike_crypto_profile`
  - SDK Module: `scm.config.network.ike_crypto_profile.IKECryptoProfile`
  - Template: Use existing profile modules as template
  - Status: Available in SDK, ready to implement

- [ ] **IKE Gateway** (`ike_gateway.py`, `ike_gateway_info.py`) 🟢 SDK Available
  - Description: Manage IKE gateways
  - Complexity: High (complex VPN configuration)
  - SDK Service: `ike_gateway`
  - SDK Module: `scm.config.network.ike_gateway.IKEGateway`
  - Template: Use existing modules as template
  - Status: Available in SDK, ready to implement

- [ ] **IPsec Crypto Profile** (`ipsec_crypto_profile.py`, `ipsec_crypto_profile_info.py`) 🟢 SDK Available
  - Description: Manage IPsec crypto profiles
  - Complexity: Medium-High
  - SDK Service: `ipsec_crypto_profile`
  - SDK Module: `scm.config.network.ipsec_crypto_profile.IPsecCryptoProfile`
  - Template: Use `ike_crypto_profile.py` as template
  - Status: Available in SDK, ready to implement

- [ ] **IPsec Tunnel** (`ipsec_tunnel.py`, `ipsec_tunnel_info.py`) ❌ NOT IN SDK
  - Description: Manage IPsec tunnels
  - Complexity: High (complex tunnel configuration)
  - Template: Use `ike_gateway.py` as template
  - Status: Not available in current SDK

### Routing
- [ ] **BGP Routing** (`bgp_routing.py`, `bgp_routing_info.py`) 🟢 SDK Available
  - Description: Manage BGP routing configuration
  - Complexity: Very High (complex routing protocols)
  - SDK Service: `bgp_routing`
  - SDK Module: `scm.config.deployment.bgp_routing.BGPRouting`
  - Template: Use existing modules as template
  - Status: Available in SDK, ready to implement

- [ ] **NAT Rule** (`nat_rule.py`, `nat_rule_info.py`) 🟢 SDK Available
  - Description: Manage NAT rules
  - Complexity: High (complex NAT policy)
  - SDK Service: `nat_rule`
  - SDK Module: `scm.config.network.nat_rules.NatRule`
  - Template: Use `security_rule.py` as template
  - Status: Available in SDK, ready to implement

## Priority 9: Deployment & Infrastructure

### Bandwidth & Network Management
- [ ] **Bandwidth Allocations** (`bandwidth_allocation.py`, `bandwidth_allocation_info.py`) 🟢 SDK Available
  - Description: Manage bandwidth allocations
  - Complexity: Medium
  - SDK Service: `bandwidth_allocation`
  - SDK Module: `scm.config.deployment.bandwidth_allocations.BandwidthAllocations`
  - Template: Use `address.py` as template
  - Status: Available in SDK, ready to implement

- [x] **Internal DNS Servers** (`internal_dns_server.py`, `internal_dns_server_info.py`) ✅
  - Description: Manage internal DNS servers
  - Complexity: Low-Medium
  - SDK Service: `internal_dns_server`
  - Template: Used server profile modules as template
  - Status: Completed and committed to feature/priority-8-10-modules branch
  - Note: Priority 9 module - **COMPLETE!**

- [ ] **Remote Networks** (`remote_network.py`, `remote_network_info.py`) 🟢 SDK Available
  - Description: Manage remote networks
  - Complexity: Medium-High
  - SDK Service: `remote_network`
  - SDK Module: `scm.config.deployment.remote_networks.RemoteNetworks`
  - Template: Use existing network modules as template
  - Status: Available in SDK, ready to implement

- [ ] **Network Locations** (`network_location.py`, `network_location_info.py`) 🟢 SDK Available
  - Description: Manage network locations
  - Complexity: Medium
  - SDK Service: `network_location`
  - SDK Module: `scm.config.deployment.network_locations.NetworkLocations`
  - Template: Use `region.py` as template
  - Status: Available in SDK, ready to implement

- [ ] **Service Connections** (`service_connection.py`, `service_connection_info.py`) 🟢 SDK Available
  - Description: Manage service connections
  - Complexity: Medium-High
  - SDK Service: `service_connection`
  - SDK Module: `scm.config.deployment.service_connections.ServiceConnection`
  - Template: Use existing connection modules as template
  - Status: Available in SDK, ready to implement

## Priority 10: Security Services & Policies

### Security Rules

- [x] **Security Rule** (`security_rule.py`, `security_rule_info.py`) ✅
  - Description: Manage security rules
  - Complexity: Very High (complex policy management)
  - Template: Used existing modules as template
  - Status: Completed and committed to feature/priority-8-10-modules branch
  - Note: Core functionality - HIGHEST PRIORITY - **COMPLETE!**

### Security Profiles
- [x] **Anti-Spyware Profile** (`anti_spyware_profile.py`, `anti_spyware_profile_info.py`) ✅
  - Description: Manage anti-spyware profiles
  - Complexity: High
  - Template: Used profile modules as template
  - Status: Completed and committed to feature/priority-8-10-modules branch
  - Note: Short Term priority - **COMPLETE!**

- [x] **Decryption Profile** (`decryption_profile.py`, `decryption_profile_info.py`) ✅
  - Description: Manage decryption profiles
  - Complexity: High
  - Template: Used profile modules as template
  - Status: Completed and committed to feature/priority-8-10-modules branch
  - Note: Short Term priority - **COMPLETE!**

- [x] **DNS Security Profile** (`dns_security_profile.py`, `dns_security_profile_info.py`) ✅
  - Description: Manage DNS security profiles
  - Complexity: Medium-High
  - Template: Used profile modules as template
  - Status: Completed and committed to feature/priority-8-10-modules branch
  - Note: Short Term priority - **COMPLETE!**

- [ ] **DNS Server Profiles** (`dns_server_profiles.py`, `dns_server_profiles_info.py`)
  - Description: Manage DNS server profiles
  - Complexity: Medium
  - Template: Use `http_server_profile.py` as template
  - Status: ❌ **NOT AVAILABLE IN CURRENT SDK** - Does not exist in pan-scm-sdk
  - Note: May have existed in previous collection but not in current SDK version

- [ ] **Security Profiles Group** (`security_profiles_group.py`, `security_profiles_group_info.py`)
  - Description: Manage security profile groups
  - Complexity: Medium
  - Template: Use group modules as template
  - Status: ❌ **NOT AVAILABLE IN CURRENT SDK** - Does not exist in pan-scm-sdk
  - Note: May have existed in previous collection but not in current SDK version

- [x] **URL Categories** (`url_categories.py`, `url_categories_info.py`) ✅
  - Description: Manage custom URL categories
  - Complexity: Medium
  - Template: Used `tag.py` as template
  - Status: Completed and committed to feature/priority-8-10-modules branch
  - Note: Short Term priority #1 - **COMPLETE!**

- [x] **Vulnerability Protection Profile** (`vulnerability_protection_profile.py`, `vulnerability_protection_profile_info.py`) ✅
  - Description: Manage vulnerability protection profiles
  - Complexity: High
  - Template: Used profile modules as template
  - Status: Completed and committed to feature/priority-8-10-modules branch
  - Note: Short Term priority #3 - **COMPLETE!**

- [x] **WildFire Antivirus Profile** (`wildfire_antivirus_profile.py`, `wildfire_antivirus_profile_info.py`) ✅
  - Description: Manage WildFire antivirus profiles
  - Complexity: Medium-High
  - Template: Used profile modules as template
  - Status: Completed and committed to feature/priority-8-10-modules branch
  - Note: Short Term priority #4 - **COMPLETE!**

## Additional SDK Services (Not in Original TODO)

The following services are available in pan-scm-sdk v0.3.44 but were not in the original previous collection TODO:

### Mobile Agent Management
- [ ] **Agent Version** (`agent_version.py`, `agent_version_info.py`) 🟢 SDK Available
  - Description: Manage mobile agent versions
  - Complexity: Low
  - SDK Service: `agent_version`
  - SDK Module: `scm.config.mobile_agent.agent_versions.AgentVersions`
  - Template: Use simple resource module as template
  - Status: Available in SDK, ready to implement

- [ ] **Auth Setting** (`auth_setting.py`, `auth_setting_info.py`) 🟢 SDK Available
  - Description: Manage authentication settings for mobile agents
  - Complexity: Medium
  - SDK Service: `auth_setting`
  - SDK Module: `scm.config.mobile_agent.auth_settings.AuthSettings`
  - Template: Use profile modules as template
  - Status: Available in SDK, ready to implement

### Object Automation
- [ ] **Auto Tag Action** (`auto_tag_action.py`, `auto_tag_action_info.py`) 🟢 SDK Available
  - Description: Manage automatic tagging actions
  - Complexity: Medium
  - SDK Service: `auto_tag_action`
  - SDK Module: `scm.config.objects.auto_tag_actions.AutoTagActions`
  - Template: Use `tag.py` as template
  - Status: Available in SDK, ready to implement

### Prisma Insights
- [ ] **Alerts** (`alerts.py`, `alerts_info.py`) 🟢 SDK Available
  - Description: Manage Prisma Insights alerts
  - Complexity: Medium
  - SDK Service: `alerts`
  - SDK Module: `scm.insights.alerts.Alerts`
  - Template: Use existing modules as template
  - Status: Available in SDK, ready to implement
  - Note: Insights API, different endpoint structure

## Summary of Remaining Work

### Module Count to Add

| Category | Resource Modules | Info Modules | Total | SDK Available |
|----------|-----------------|--------------|-------|---------------|
| Network Configuration & VPN | 6 | 6 | 12 | 10 🟢 / 2 ❌ |
| Deployment & Infrastructure | 4 | 4 | 8 | 8 🟢 |
| Security Services & Policies | 0 | 0 | 0 | All Complete ✅ |
| Mobile Agent & Automation | 3 | 3 | 6 | 6 🟢 |
| Prisma Insights | 1 | 1 | 2 | 2 🟢 |
| **Total Remaining (SDK Available)** | **14** | **14** | **28** | **26 🟢 / 2 ❌** |
| **Completed from Priority 10** | **7** | **7** | **14** | **14 ✅** |
| **Completed from Priority 9** | **1** | **1** | **2** | **2 ✅** |

### Current vs Target Status

- **Current Implementation**: 60 modules (30 resource + 30 info) = **67% SDK coverage**
- **SDK Available Services**: 45 total
- **Remaining SDK Services to Implement**: 15 (can create 30 modules)
- **Not in SDK**: 2 services (dns_server_profiles, security_profiles_group)
- **Target (100% SDK Coverage)**: 90 modules (45 resource + 45 info modules)

### When All SDK Services Are Complete

- **Current**: 60 modules (30 resource + 30 info)
- **Remaining to implement from SDK**: 30 modules (15 resource + 15 info)
- **After 100% SDK coverage**: 90 modules (45 resource + 45 info modules)

### Estimated Effort

- **Priority 8** (Network Configuration & VPN): ~24-32 hours
- **Priority 9** (Deployment & Infrastructure): ~18-24 hours
- **Priority 10** (Security Services & Policies): ~28-40 hours (reduced by 8 hours for completed modules)

**Total Remaining Effort**: 70-96 hours

## Implementation Priorities

### Completed

1. ✅ **Security Rule** - Core functionality, most important - **DONE!**
2. ✅ **URL Categories** - Common use case - **DONE!**
3. ✅ **Anti-Spyware Profile** - Security essential - **DONE!**
4. ✅ **Vulnerability Protection Profile** - Security essential - **DONE!**
5. ✅ **WildFire Antivirus Profile** - Security essential - **DONE!**
6. ✅ **Decryption Profile** - Advanced security capability - **DONE!**
7. ✅ **DNS Security Profile** - DNS protection - **DONE!**

### Immediate (Next Sprint)

1. ~~**DNS Server Profiles**~~ - ❌ NOT AVAILABLE IN SDK (verified - does not exist in current pan-scm-sdk)
2. ~~**Security Profiles Group**~~ - ❌ NOT AVAILABLE IN SDK (verified - does not exist in current pan-scm-sdk)

**Note**: All Priority 10 (Security) modules that exist in the current SDK have been completed! Moving to other priorities.

### Short Term

(All Short Term priorities complete!)

### Medium Term

1. **IKE Crypto Profile** - VPN foundation
2. **IPsec Crypto Profile** - VPN foundation
3. **IKE Gateway** - VPN implementation
4. **IPsec Tunnel** - VPN implementation
5. **Security Zone** - Network segmentation

### Long Term

1. **Remote Networks** - SD-WAN functionality
2. **Service Connections** - SD-WAN functionality
3. **BGP Routing** - Advanced routing
4. **Bandwidth Allocations** - QoS functionality
5. **Network Locations** - Deployment management
6. **Internal DNS Servers** - Infrastructure management
7. **Decryption Profile** - Advanced security
8. **DNS Security Profile** - DNS protection

## Implementation Guidelines

For each new module:

1. **Copy Template**: Use appropriate existing module as template
2. **Review Previous Implementation**: Check the previous collection's implementation for reference
3. **Update Documentation**: Modify DOCUMENTATION, EXAMPLES, and RETURN blocks
4. **Update Parameters**: Match SDK model parameters in `module_args`
5. **Update Client Calls**: Change `client.<resource>` references
6. **Update Imports**: Import correct models from appropriate SDK locations
7. **Test**: Build, install, and test with example playbooks
8. **Lint**: Run `make lint-all` and fix any issues
9. **Create Examples**: Add example playbook to `examples/` directory
10. **Update CLAUDE.md**: Add to resource modules status list
11. **Update README.md**: Add to available modules section

## Notes

- Modules marked with ⚠️ have API limitations but are fully implemented
- All modules should follow the patterns established in current collection
- Previous collection used `provider` parameter; current collection uses `scm_access_token`
- Need to verify SDK support for all modules before implementation
- Some modules in previous collection may need significant refactoring for new architecture


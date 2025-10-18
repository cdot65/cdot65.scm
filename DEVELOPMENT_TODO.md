# Development TODO

Priority list for implementing remaining `pan-scm-sdk` object resources in the `cdot65.scm` Ansible collection.

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
| Device | - | ✅ | ✅ |

**Total Current**: 58 modules (29 resource + 29 info modules)

### 🔴 Missing Modules (From Previous Collection)

The following modules exist in the previous iteration but need to be ported to this collection:

## Priority 8: Network Configuration & VPN

### Security Zones
- [ ] **Security Zone** (`security_zone.py`)
  - Description: Manage security zones
  - Complexity: Medium
  - Template: Use `address.py` as template
  - Status: In previous collection, needs porting

### VPN & Crypto
- [ ] **IKE Crypto Profile** (`ike_crypto_profile.py`, `ike_crypto_profile_info.py`)
  - Description: Manage IKE crypto profiles
  - Complexity: Medium-High
  - Template: Use existing profile modules as template
  - Status: In previous collection, needs porting

- [ ] **IKE Gateway** (`ike_gateway.py`)
  - Description: Manage IKE gateways
  - Complexity: High (complex VPN configuration)
  - Template: Use existing modules as template
  - Status: In previous collection, needs porting

- [ ] **IPsec Crypto Profile** (`ipsec_crypto_profile.py`)
  - Description: Manage IPsec crypto profiles
  - Complexity: Medium-High
  - Template: Use `ike_crypto_profile.py` as template
  - Status: In previous collection, needs porting

- [ ] **IPsec Tunnel** (`ipsec_tunnel.py`)
  - Description: Manage IPsec tunnels
  - Complexity: High (complex tunnel configuration)
  - Template: Use `ike_gateway.py` as template
  - Status: In previous collection, needs porting

### Routing
- [ ] **BGP Routing** (`bgp_routing.py`, `bgp_routing_info.py`)
  - Description: Manage BGP routing configuration
  - Complexity: Very High (complex routing protocols)
  - Template: Use existing modules as template
  - Status: In previous collection, needs porting

## Priority 9: Deployment & Infrastructure

### Bandwidth & Network Management
- [ ] **Bandwidth Allocations** (`bandwidth_allocations.py`, `bandwidth_allocations_info.py`)
  - Description: Manage bandwidth allocations
  - Complexity: Medium
  - Template: Use `address.py` as template
  - Status: In previous collection, needs porting

- [ ] **Internal DNS Servers** (`internal_dns_servers.py`, `internal_dns_servers_info.py`)
  - Description: Manage internal DNS servers
  - Complexity: Low-Medium
  - Template: Use server profile modules as template
  - Status: In previous collection, needs porting

- [ ] **Remote Networks** (`remote_networks.py`, `remote_networks_info.py`)
  - Description: Manage remote networks
  - Complexity: Medium-High
  - Template: Use existing network modules as template
  - Status: In previous collection, needs porting

- [ ] **Network Locations** (`network_locations.py`)
  - Description: Manage network locations
  - Complexity: Medium
  - Template: Use `region.py` as template
  - Status: In previous collection, needs porting

- [ ] **Service Connections** (`service_connections.py`, `service_connections_info.py`)
  - Description: Manage service connections
  - Complexity: Medium-High
  - Template: Use existing connection modules as template
  - Status: In previous collection, needs porting

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
  - Status: In previous collection, needs porting

- [ ] **Security Profiles Group** (`security_profiles_group.py`, `security_profiles_group_info.py`)
  - Description: Manage security profile groups
  - Complexity: Medium
  - Template: Use group modules as template
  - Status: In previous collection, needs porting

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

## Summary of Remaining Work

### Module Count to Add

| Category | Resource Modules | Info Modules | Total |
|----------|-----------------|--------------|-------|
| Network Configuration & VPN | 6 | 2 | 8 |
| Deployment & Infrastructure | 5 | 4 | 9 |
| Security Services & Policies | 3 | 3 | 6 |
| **Total Remaining** | **14** | **9** | **23** |
| **Completed from Priority 10** | **7** | **7** | **14** |

### When Complete

- **Current**: 58 modules (29 resource + 29 info)
- **Remaining to add**: 23 modules (14 resource + 9 info)
- **After adding previous collection**: 79 modules (42 resource + 37 info)

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

1. **DNS Server Profiles** - Commonly used, medium complexity (Note: Needs SDK verification)
2. **Security Profiles Group** - Ties together other profiles (Note: Needs SDK verification)

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


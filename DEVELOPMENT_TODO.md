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
| Device | - | ✅ | ✅ |

**Total Current**: 44 modules (22 resource + 22 info modules)

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
- [ ] **Security Rule** (`security_rule.py`, `security_rule_info.py`)
  - Description: Manage security rules
  - Complexity: Very High (complex policy management)
  - Template: Use existing rule modules as template
  - Status: In previous collection, needs porting
  - Note: Core functionality - high priority

### Security Profiles
- [ ] **Anti-Spyware Profile** (`anti_spyware_profile.py`, `anti_spyware_profile_info.py`)
  - Description: Manage anti-spyware profiles
  - Complexity: High
  - Template: Use profile modules as template
  - Status: In previous collection, needs porting

- [ ] **Decryption Profile** (`decryption_profile.py`, `decryption_profile_info.py`)
  - Description: Manage decryption profiles
  - Complexity: High
  - Template: Use profile modules as template
  - Status: In previous collection, needs porting

- [ ] **DNS Security Profile** (`dns_security_profile.py`, `dns_security_profile_info.py`)
  - Description: Manage DNS security profiles
  - Complexity: Medium-High
  - Template: Use profile modules as template
  - Status: In previous collection, needs porting

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

- [ ] **URL Categories** (`url_categories.py`, `url_categories_info.py`)
  - Description: Manage URL categories
  - Complexity: Medium
  - Template: Use `tag.py` as template
  - Status: In previous collection, needs porting

- [ ] **Vulnerability Protection Profile** (`vulnerability_protection_profile.py`, `vulnerability_protection_profile_info.py`)
  - Description: Manage vulnerability protection profiles
  - Complexity: High
  - Template: Use profile modules as template
  - Status: In previous collection, needs porting

- [ ] **WildFire Antivirus Profiles** (`wildfire_antivirus_profiles.py`, `wildfire_antivirus_profiles_info.py`)
  - Description: Manage WildFire antivirus profiles
  - Complexity: Medium-High
  - Template: Use profile modules as template
  - Status: In previous collection, needs porting

## Summary of Remaining Work

### Module Count to Add

| Category | Resource Modules | Info Modules | Total |
|----------|-----------------|--------------|-------|
| Network Configuration & VPN | 6 | 2 | 8 |
| Deployment & Infrastructure | 5 | 4 | 9 |
| Security Services & Policies | 9 | 9 | 18 |
| **Total** | **20** | **15** | **35** |

### When Complete

- **Current**: 44 modules (22 resource + 22 info)
- **After adding previous collection**: 79 modules (42 resource + 37 info)

### Estimated Effort

- **Priority 8** (Network Configuration & VPN): ~24-32 hours
- **Priority 9** (Deployment & Infrastructure): ~18-24 hours
- **Priority 10** (Security Services & Policies): ~36-48 hours

**Total Estimated Effort**: 78-104 hours

## Implementation Priorities

### Immediate (Next Sprint)
1. **Security Rule** - Core functionality, most important
2. **DNS Server Profiles** - Commonly used, medium complexity
3. **Security Profiles Group** - Ties together other profiles

### Short Term
4. **URL Categories** - Common use case
5. **Anti-Spyware Profile** - Security essential
6. **Vulnerability Protection Profile** - Security essential
7. **WildFire Antivirus Profiles** - Security essential

### Medium Term
8. **IKE Crypto Profile** - VPN foundation
9. **IPsec Crypto Profile** - VPN foundation
10. **IKE Gateway** - VPN implementation
11. **IPsec Tunnel** - VPN implementation
12. **Security Zone** - Network segmentation

### Long Term
13. **Remote Networks** - SD-WAN functionality
14. **Service Connections** - SD-WAN functionality
15. **BGP Routing** - Advanced routing
16. **Bandwidth Allocations** - QoS functionality
17. **Network Locations** - Deployment management
18. **Internal DNS Servers** - Infrastructure management
19. **Decryption Profile** - Advanced security
20. **DNS Security Profile** - DNS protection

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

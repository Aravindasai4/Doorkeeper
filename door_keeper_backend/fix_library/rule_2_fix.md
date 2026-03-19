### door_keeper_backend/fix_library/rule_2_fix.md
```markdown
# Encryption Standards Fix

## Issue
Your encryption configuration uses outdated or weak protocols.

## Immediate Actions Required

1. **Upgrade Protocol**: Use TLS 1.2 or TLS 1.3 only
2. **Disable Weak Protocols**: Remove SSL, TLS 1.0, and TLS 1.1
3. **Configure Strong Ciphers**: Use AES-256 or ChaCha20-Poly1305

## Implementation Steps

1. Update server configuration
2. Test connectivity with clients
3. Monitor for compatibility issues
4. Update client applications if needed

## Configuration Example
```json
{
  "network": {
    "encryption": "TLS1.3",
    "allowed_ciphers": [
      "TLS_AES_256_GCM_SHA384",
      "TLS_CHACHA20_POLY1305_SHA256"
    ],
    "disabled_protocols": ["SSL", "TLS1.0", "TLS1.1"]
  }
}

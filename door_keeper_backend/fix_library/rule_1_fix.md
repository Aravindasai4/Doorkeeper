# Password Policy Compliance Fix

## Issue
Your current password policy does not meet modern security standards.

## Recommended Actions
1. Minimum length: 12+ characters  
2. Require uppercase, lowercase, numbers, special characters  
3. Enable password history, max age, account lockout  
4. Consider passphrase support

## Example
```json
{ "password_policy": { "min_length": 12, "require_uppercase": true, "require_lowercase": true, "require_numbers": true, "require_special": true } }

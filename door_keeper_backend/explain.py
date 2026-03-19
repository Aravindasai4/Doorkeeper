"""
Explanation Engine
Provides detailed explanations and fix suggestions for security findings
"""

import os
from pathlib import Path
from typing import Optional


class ExplanationEngine:
    """
    Provides explanations and fix suggestions for security rules
    """
    
    def __init__(self):
        self.fix_library_path = Path(__file__).parent / "fix_library"
        self.explanations = {
            "rule_1": "Password policies are critical for preventing unauthorized access through weak credentials.",
            "rule_2": "Strong encryption protocols protect data in transit from eavesdropping and tampering.",
            "rule_3": "Minimizing open ports reduces the attack surface available to potential attackers.",
            "rule_4": "Multi-factor authentication significantly reduces the risk of account compromise.",
            "rule_5": "Comprehensive logging enables threat detection and forensic investigation.",
            "rule_6": "Regular encrypted backups ensure business continuity and data protection."
        }
    
    def get_explanation(self, rule_id: str) -> str:
        """
        Get detailed explanation for a specific rule
        
        Args:
            rule_id: The rule identifier
            
        Returns:
            Detailed explanation of why the rule is important
        """
        return self.explanations.get(rule_id, "No explanation available for this rule.")
    
    def get_fix_suggestion(self, rule_id: str) -> Optional[str]:
        """
        Load fix suggestion from markdown file in fix_library
        
        Args:
            rule_id: The rule identifier
            
        Returns:
            Fix suggestion content or None if not found
        """
        fix_file = self.fix_library_path / f"{rule_id}_fix.md"
        
        try:
            if fix_file.exists():
                with open(fix_file, 'r', encoding='utf-8') as f:
                    return f.read().strip()
        except Exception as e:
            print(f"Error reading fix file for {rule_id}: {e}")
        
        return self._get_default_fix(rule_id)
    
    def _get_default_fix(self, rule_id: str) -> str:
        """Provide default fix suggestions if markdown files are not available"""
        defaults = {
            "rule_1": "Implement strong password policy: minimum 12 characters, require uppercase, lowercase, numbers, and special characters.",
            "rule_2": "Upgrade to TLS 1.2 or TLS 1.3. Disable weak protocols like SSL, TLS 1.0, and TLS 1.1.",
            "rule_3": "Close unnecessary ports. Use firewall rules to restrict access. Regularly audit open ports.",
            "rule_4": "Implement multi-factor authentication (MFA) using TOTP, SMS, or hardware tokens.",
            "rule_5": "Enable comprehensive logging with appropriate retention. Implement log monitoring and alerting.",
            "rule_6": "Configure automated daily backups with encryption. Test restore procedures regularly."
        }
        return defaults.get(rule_id, "Consult security documentation for specific remediation steps.")

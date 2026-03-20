"""
Rules Engine for DoorKeeper
Implements 7 security/compliance rule checks
"""

from typing import List, Dict, Any
from .models.schemas import Finding, SeverityLevel
from .explain import ExplanationEngine

class RulesEngine:
    """
    Core rules engine that runs security and compliance checks
    """
    
    def __init__(self):
        self.explanation_engine = ExplanationEngine()
        
        # Define the 7 rules
        self.rules = {
            "rule_1": self._check_password_policy,
            "rule_2": self._check_encryption_standards,
            "rule_3": self._check_open_ports,
            "rule_4": self._check_authentication_method,
            "rule_5": self._check_logging_configuration,
            "rule_6": self._check_backup_settings,
            "rule_7": self._check_ai_model_governance,
        }
    
    def run_all_checks(self, config: Dict[str, Any]) -> List[Finding]:
        """
        Execute all security rules against the provided configuration
        
        Args:
            config: Configuration dictionary to check
            
        Returns:
            List of Finding objects with results
        """
        findings = []
        
        for rule_id, rule_func in self.rules.items():
            try:
                finding = rule_func(config)
                findings.append(finding)
            except Exception as e:
                # Create error finding if rule fails
                findings.append(Finding(
                    rule_id=rule_id,
                    rule_name=f"Rule {rule_id} (Error)",
                    severity=SeverityLevel.HIGH,
                    passed=False,
                    message=f"Rule execution failed: {str(e)}",
                    fix_suggestion="Contact system administrator"
                ))
        
        return findings
    
    def _check_password_policy(self, config: Dict[str, Any]) -> Finding:
        """Rule 1: Check password policy compliance"""
        rule_id = "rule_1"
        rule_name = "Password Policy Compliance"
        
        auth_config = config.get("authentication", {})
        password_policy = auth_config.get("password_policy", {})
        
        issues = []
        min_length = password_policy.get("min_length", 0)
        
        if min_length < 12:
            issues.append(f"Minimum length {min_length} is below recommended 12 characters")
        
        if not password_policy.get("require_uppercase"):
            issues.append("Uppercase letters are not required")
            
        if not password_policy.get("require_numbers"):
            issues.append("Numbers are not required")
            
        if not password_policy.get("require_special"):
            issues.append("Special characters are not required")
        
        passed = len(issues) == 0
        severity = SeverityLevel.HIGH if not passed else SeverityLevel.INFO
        
        message = "Password policy meets security requirements" if passed else f"Password policy issues found: {'; '.join(issues)}"
        
        return Finding(
            rule_id=rule_id,
            rule_name=rule_name,
            severity=severity,
            passed=passed,
            message=message,
            fix_suggestion=self.explanation_engine.get_fix_suggestion(rule_id) if not passed else None,
            affected_items=["authentication.password_policy"]
        )
    
    def _check_encryption_standards(self, config: Dict[str, Any]) -> Finding:
        """Rule 2: Check encryption standards"""
        rule_id = "rule_2"
        rule_name = "Encryption Standards"
        
        network_config = config.get("network", {})
        encryption = network_config.get("encryption", "").upper()
        
        weak_protocols = ["SSL", "TLS1.0", "TLS1.1"]
        strong_protocols = ["TLS1.2", "TLS1.3"]
        
        if encryption in weak_protocols:
            passed = False
            severity = SeverityLevel.CRITICAL
            message = f"Weak encryption protocol detected: {encryption}"
        elif encryption in strong_protocols:
            passed = True
            severity = SeverityLevel.INFO
            message = f"Strong encryption protocol in use: {encryption}"
        else:
            passed = False
            severity = SeverityLevel.HIGH
            message = f"Unknown or missing encryption protocol: {encryption}"
        
        return Finding(
            rule_id=rule_id,
            rule_name=rule_name,
            severity=severity,
            passed=passed,
            message=message,
            fix_suggestion=self.explanation_engine.get_fix_suggestion(rule_id) if not passed else None,
            affected_items=["network.encryption"]
        )
    
    def _check_open_ports(self, config: Dict[str, Any]) -> Finding:
        """Rule 3: Check for unnecessary open ports"""
        rule_id = "rule_3"
        rule_name = "Open Ports Security"
        
        network_config = config.get("network", {})
        open_ports = network_config.get("ports", [])
        
        # Common risky ports
        risky_ports = [21, 23, 53, 135, 139, 445, 1433, 3389, 5432]
        necessary_ports = [80, 443, 22]
        
        found_risky = [port for port in open_ports if port in risky_ports]
        unnecessary_ports = [port for port in open_ports if port not in necessary_ports and port not in risky_ports]
        
        issues = []
        if found_risky:
            issues.append(f"Risky ports open: {found_risky}")
        if len(unnecessary_ports) > 3:
            issues.append(f"Many unnecessary ports open: {len(unnecessary_ports)} ports")
        
        passed = len(issues) == 0
        severity = SeverityLevel.MEDIUM if found_risky else SeverityLevel.LOW
        
        message = "Port configuration is secure" if passed else f"Port security issues: {'; '.join(issues)}"
        
        return Finding(
            rule_id=rule_id,
            rule_name=rule_name,
            severity=severity,
            passed=passed,
            message=message,
            fix_suggestion=self.explanation_engine.get_fix_suggestion(rule_id) if not passed else None,
            affected_items=["network.ports"]
        )
    
    def _check_authentication_method(self, config: Dict[str, Any]) -> Finding:
        """Rule 4: Check authentication method security"""
        rule_id = "rule_4"
        rule_name = "Authentication Method Security"
        
        auth_config = config.get("authentication", {})
        method = auth_config.get("method", "").lower()
        
        if method in ["mfa", "2fa", "multi-factor"]:
            passed = True
            severity = SeverityLevel.INFO
            message = "Multi-factor authentication is enabled"
        elif method in ["oauth", "saml", "sso"]:
            passed = True
            severity = SeverityLevel.INFO
            message = f"Secure authentication method in use: {method.upper()}"
        elif method == "password":
            passed = False
            severity = SeverityLevel.MEDIUM
            message = "Password-only authentication is not recommended"
        else:
            passed = False
            severity = SeverityLevel.HIGH
            message = f"Insecure or unknown authentication method: {method}"
        
        return Finding(
            rule_id=rule_id,
            rule_name=rule_name,
            severity=severity,
            passed=passed,
            message=message,
            fix_suggestion=self.explanation_engine.get_fix_suggestion(rule_id) if not passed else None,
            affected_items=["authentication.method"]
        )
    
    def _check_logging_configuration(self, config: Dict[str, Any]) -> Finding:
        """Rule 5: Check logging and monitoring configuration"""
        rule_id = "rule_5"
        rule_name = "Logging and Monitoring"
        
        logging_config = config.get("logging", {})
        
        issues = []
        if not logging_config.get("enabled", False):
            issues.append("Logging is not enabled")
        
        log_level = logging_config.get("level", "").upper()
        if log_level not in ["INFO", "WARN", "ERROR", "DEBUG"]:
            issues.append(f"Invalid or missing log level: {log_level}")
        
        if not logging_config.get("audit_trail", False):
            issues.append("Audit trail is not configured")
        
        retention_days = logging_config.get("retention_days", 0)
        if retention_days < 30:
            issues.append(f"Log retention too short: {retention_days} days (minimum 30)")
        
        passed = len(issues) == 0
        severity = SeverityLevel.MEDIUM if not passed else SeverityLevel.INFO
        
        message = "Logging configuration is adequate" if passed else f"Logging issues: {'; '.join(issues)}"
        
        return Finding(
            rule_id=rule_id,
            rule_name=rule_name,
            severity=severity,
            passed=passed,
            message=message,
            fix_suggestion=self.explanation_engine.get_fix_suggestion(rule_id) if not passed else None,
            affected_items=["logging"]
        )
    
    def _check_backup_settings(self, config: Dict[str, Any]) -> Finding:
        """Rule 6: Check backup and disaster recovery settings"""
        rule_id = "rule_6"
        rule_name = "Backup and Disaster Recovery"
        
        backup_config = config.get("backup", {})
        
        issues = []
        if not backup_config.get("enabled", False):
            issues.append("Backup is not enabled")
        
        frequency = backup_config.get("frequency", "").lower()
        if frequency not in ["daily", "hourly"]:
            issues.append(f"Backup frequency inadequate: {frequency}")
        
        if not backup_config.get("encrypted", False):
            issues.append("Backups are not encrypted")
        
        if not backup_config.get("offsite", False):
            issues.append("Offsite backup is not configured")
        
        retention_days = backup_config.get("retention_days", 0)
        if retention_days < 30:
            issues.append(f"Backup retention too short: {retention_days} days")
        
        passed = len(issues) == 0
        severity = SeverityLevel.HIGH if not passed else SeverityLevel.INFO
        
        message = "Backup configuration is robust" if passed else f"Backup issues: {'; '.join(issues)}"
        
        return Finding(
            rule_id=rule_id,
            rule_name=rule_name,
            severity=severity,
            passed=passed,
            message=message,
            fix_suggestion=self.explanation_engine.get_fix_suggestion(rule_id) if not passed else None,
            affected_items=["backup"]
        )

    def _check_ai_model_governance(self, config: Dict[str, Any]) -> Finding:
        """Rule 7: Check AI model governance controls"""
        rule_id = "rule_7"
        rule_name = "AI Model Governance Controls"

        ai_config = config.get("ai_model", {})

        issues = []

        if not ai_config.get("version_pinned", False):
            issues.append("Model version is not pinned — unpinned models may change behaviour silently")

        if not ai_config.get("output_logging", False):
            issues.append("Model outputs are not being logged — required for auditing and debugging")

        if not ai_config.get("human_review_threshold"):
            issues.append("No human-in-the-loop threshold defined — high-risk outputs may not be reviewed")

        if not ai_config.get("bias_monitoring", False):
            issues.append("Bias monitoring is not configured — model fairness cannot be verified")

        if not ai_config.get("data_provenance", False):
            issues.append("Input data provenance is not tracked — data lineage and quality cannot be assured")

        passed = len(issues) == 0

        if len(issues) >= 2:
            severity = SeverityLevel.HIGH
        elif len(issues) == 1:
            severity = SeverityLevel.MEDIUM
        else:
            severity = SeverityLevel.INFO

        message = (
            "AI model governance controls are in place"
            if passed
            else f"AI governance issues found: {'; '.join(issues)}"
        )

        return Finding(
            rule_id=rule_id,
            rule_name=rule_name,
            severity=severity,
            passed=passed,
            message=message,
            fix_suggestion=self.explanation_engine.get_fix_suggestion(rule_id) if not passed else None,
            affected_items=[
                "ai_model",
                "NIST AI RMF: GOVERN 1.1",
                "ISO 42001: 6.1.2",
            ]
        )


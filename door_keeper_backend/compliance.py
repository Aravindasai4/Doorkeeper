"""
Compliance Score Calculator
Calculates overall compliance scores based on security findings
"""

from typing import List, Dict, Any
from .models.schemas import Finding, SeverityLevel


class ComplianceCalculator:
    """
    Calculates compliance scores and provides compliance reporting
    """
    
    def __init__(self):
        # Weights for different severity levels
        self.severity_weights = {
            SeverityLevel.CRITICAL: 25,
            SeverityLevel.HIGH: 20,
            SeverityLevel.MEDIUM: 10,
            SeverityLevel.LOW: 5,
            SeverityLevel.INFO: 0
        }
        
        # Maximum possible score
        self.max_score = 100
    
    def calculate_score(self, findings: List[Finding]) -> float:
        """
        Calculate overall compliance score based on findings
        
        Args:
            findings: List of security findings
            
        Returns:
            Compliance score from 0-100
        """
        if not findings:
            return 0.0
        
        total_deductions = 0
        max_possible_deductions = len(findings) * max(self.severity_weights.values())
        
        for finding in findings:
            if not finding.passed:
                deduction = self.severity_weights.get(finding.severity, 0)
                total_deductions += deduction
        
        # Calculate score as percentage
        if max_possible_deductions == 0:
            return 100.0
        
        score = max(0, self.max_score - (total_deductions / max_possible_deductions * self.max_score))
        return round(score, 1)
    
    def get_compliance_grade(self, score: float) -> str:
        """
        Convert numerical score to letter grade
        
        Args:
            score: Compliance score (0-100)
            
        Returns:
            Letter grade (A+ to F)
        """
        if score >= 95:
            return "A+"
        elif score >= 90:
            return "A"
        elif score >= 85:
            return "A-"
        elif score >= 80:
            return "B+"
        elif score >= 75:
            return "B"
        elif score >= 70:
            return "B-"
        elif score >= 65:
            return "C+"
        elif score >= 60:
            return "C"
        elif score >= 55:
            return "C-"
        elif score >= 50:
            return "D"
        else:
            return "F"
    
    def generate_compliance_report(self, findings: List[Finding]) -> Dict[str, Any]:
        """
        Generate detailed compliance report
        
        Args:
            findings: List of security findings
            
        Returns:
            Comprehensive compliance report
        """
        score = self.calculate_score(findings)
        grade = self.get_compliance_grade(score)
        
        # Count findings by severity
        severity_counts = {}
        passed_count = 0
        failed_count = 0
        
        for severity in SeverityLevel:
            severity_counts[severity.value] = 0
        
        for finding in findings:
            severity_counts[finding.severity.value] += 1
            if finding.passed:
                passed_count += 1
            else:
                failed_count += 1
        
        # Identify top issues
        failed_findings = [f for f in findings if not f.passed]
        critical_issues = [f for f in failed_findings if f.severity == SeverityLevel.CRITICAL]
        
        return {
            "overall_score": score,
            "grade": grade,
            "total_checks": len(findings),
            "passed_checks": passed_count,
            "failed_checks": failed_count,
            "severity_breakdown": severity_counts,
            "critical_issues_count": len(critical_issues),
            "improvement_needed": score < 80,
            "next_review_recommended": self._get_review_timeline(score)
        }
    
    def _get_review_timeline(self, score: float) -> str:
        """Recommend next review timeline based on score"""
        if score >= 90:
            return "Quarterly review recommended"
        elif score >= 75:
            return "Monthly review recommended"
        elif score >= 60:
            return "Bi-weekly review recommended"
        else:
            return "Weekly review required"

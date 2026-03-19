"""
AI Simulation Module
Simulates AI-powered analysis and recommendations
"""

from typing import List, Dict, Any
import random
from .models.schemas import Finding, SeverityLevel


class AISimulation:
    """
    Simulates AI-powered security analysis and recommendations
    """
    
    def __init__(self):
        self.ai_insights = [
            "Configuration shows patterns typical of legacy systems",
            "Security posture indicates medium-risk environment", 
            "Authentication mechanisms need modernization",
            "Network configuration follows security best practices",
            "Backup strategy requires immediate attention",
            "Logging configuration meets compliance requirements"
        ]
        
        self.recommendations = [
            "Implement zero-trust network architecture",
            "Upgrade to passwordless authentication",
            "Enable real-time security monitoring",
            "Automate compliance reporting",
            "Implement infrastructure as code",
            "Enable continuous security scanning"
        ]
    
    def generate_ai_summary(self, findings: List[Finding]) -> Dict[str, Any]:
        """
        Generate AI-powered summary of security findings
        
        Args:
            findings: List of security findings from rules engine
            
        Returns:
            Dictionary containing AI analysis summary
        """
        critical_count = sum(1 for f in findings if f.severity == SeverityLevel.CRITICAL)
        high_count = sum(1 for f in findings if f.severity == SeverityLevel.HIGH)
        failed_count = sum(1 for f in findings if not f.passed)
        
        # Simulate AI risk assessment
        risk_level = self._calculate_risk_level(critical_count, high_count, failed_count)
        
        # Generate insights
        insight = random.choice(self.ai_insights)
        recommendation = random.choice(self.recommendations)
        
        return {
            "risk_level": risk_level,
            "confidence": round(random.uniform(0.7, 0.95), 2),
            "primary_insight": insight,
            "top_recommendation": recommendation,
            "security_trends": self._generate_trend_analysis(findings),
            "predicted_vulnerabilities": self._predict_vulnerabilities(findings)
        }
    
    def _calculate_risk_level(self, critical: int, high: int, failed: int) -> str:
        """Calculate overall risk level based on findings"""
        if critical > 0:
            return "CRITICAL"
        elif high > 1 or failed > 3:
            return "HIGH"
        elif high > 0 or failed > 1:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _generate_trend_analysis(self, findings: List[Finding]) -> List[str]:
        """Generate simulated trend analysis"""
        trends = [
            "Authentication security declining over past 30 days",
            "Network security improvements detected",
            "Backup compliance steady",
            "Logging coverage increased by 15%"
        ]
        return random.sample(trends, 2)
    
    def _predict_vulnerabilities(self, findings: List[Finding]) -> List[str]:
        """Predict potential future vulnerabilities"""
        predictions = [
            "Weak password policy may lead to credential stuffing attacks",
            "Open ports could be exploited for lateral movement",
            "Insufficient logging may hide breach indicators",
            "Backup gaps create ransomware risk"
        ]
        return random.sample(predictions, min(2, len([f for f in findings if not f.passed])))

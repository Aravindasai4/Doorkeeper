"""
Pydantic models for API request/response schemas
"""
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from enum import Enum

class SeverityLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class Finding(BaseModel):
    rule_id: str = Field(..., description="Unique identifier for the rule")
    rule_name: str = Field(..., description="Human-readable rule name")
    severity: SeverityLevel = Field(..., description="Severity level of the finding")
    passed: bool = Field(..., description="Whether the rule check passed")
    message: str = Field(..., description="Detailed message about the finding")
    fix_suggestion: Optional[str] = Field(None, description="How to fix this issue")
    affected_items: List[str] = Field(default_factory=list, description="Items affected by this rule")

class ScanRequest(BaseModel):
    config: Dict[str, Any] = Field(..., description="Configuration to scan")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "config": {
                    "authentication": {
                        "method": "password",
                        "password_policy": {
                            "min_length": 8,
                            "require_uppercase": True,
                            "require_numbers": True
                        }
                    },
                    "network": {
                        "encryption": "TLS1.2",
                        "ports": [80, 443, 22]
                    }
                },
                "metadata": {"environment": "production", "team": "security"}
            }
        }

class ScanResponse(BaseModel):
    scan_id: str = Field(..., description="Unique scan identifier")
    findings: List[Finding] = Field(..., description="List of security findings")
    compliance_score: float = Field(..., description="Overall compliance score (0-100)")
    timestamp: str = Field(..., description="Scan execution timestamp")
    ai_summary: Optional[Dict[str, Any]] = Field(None, description="Simulated AI analysis")

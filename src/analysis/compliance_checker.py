"""
Compliance Checker Module
Validates contracts against Indian laws and regulations
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class ComplianceStatus(Enum):
    """Compliance status enumeration."""
    COMPLIANT = "compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NON_COMPLIANT = "non_compliant"
    NEEDS_REVIEW = "needs_review"


@dataclass
class ComplianceIssue:
    """A single compliance issue."""
    issue_id: str
    law_reference: str
    clause_text: str
    issue_description: str
    severity: str  # Low, Medium, High, Critical
    recommendation: str
    risk_if_ignored: str


@dataclass
class ComplianceReport:
    """Complete compliance report."""
    overall_status: ComplianceStatus
    issues: List[ComplianceIssue]
    compliant_areas: List[str]
    missing_requirements: List[str]
    recommendations: List[str]
    laws_checked: List[str]


class ComplianceChecker:
    """
    Checks contract compliance with Indian laws and regulations.
    Validates against Contract Act, Arbitration Act, IT Act, and more.
    """
    
    def __init__(self):
        # Indian law compliance rules
        self.compliance_rules = {
            "indian_contract_act": {
                "name": "Indian Contract Act, 1872",
                "checks": [
                    {
                        "id": "ica_001",
                        "name": "Free Consent",
                        "description": "Agreement must be made with free consent",
                        "patterns": [
                            r"coercion",
                            r"undue\s+influence",
                            r"fraud",
                            r"misrepresentation"
                        ],
                        "check_type": "absence",  # These should be absent
                        "severity": "High"
                    },
                    {
                        "id": "ica_002",
                        "name": "Lawful Object",
                        "description": "Object of agreement must be lawful",
                        "patterns": [
                            r"illegal",
                            r"unlawful",
                            r"against\s+public\s+policy"
                        ],
                        "check_type": "absence",
                        "severity": "Critical"
                    },
                    {
                        "id": "ica_003",
                        "name": "Consideration",
                        "description": "Agreement must have lawful consideration",
                        "patterns": [
                            r"consideration",
                            r"payment",
                            r"compensation",
                            r"in\s+exchange\s+for"
                        ],
                        "check_type": "presence",  # Should be present
                        "severity": "High"
                    },
                    {
                        "id": "ica_004",
                        "name": "Competent Parties",
                        "description": "Parties must be competent to contract",
                        "patterns": [
                            r"minor",
                            r"unsound\s+mind",
                            r"disqualified\s+by\s+law"
                        ],
                        "check_type": "absence",
                        "severity": "Critical"
                    }
                ]
            },
            "arbitration_act": {
                "name": "Arbitration and Conciliation Act, 1996",
                "checks": [
                    {
                        "id": "arb_001",
                        "name": "Written Arbitration Agreement",
                        "description": "Arbitration clause must be in writing",
                        "patterns": [
                            r"arbitration",
                            r"arbitrator",
                            r"arbitral\s+tribunal"
                        ],
                        "check_type": "info",
                        "severity": "Medium"
                    },
                    {
                        "id": "arb_002",
                        "name": "Seat of Arbitration",
                        "description": "Seat/place of arbitration should be specified",
                        "patterns": [
                            r"seat\s+of\s+arbitration",
                            r"place\s+of\s+arbitration",
                            r"arbitration\s+(?:shall\s+be\s+)?(?:held\s+)?(?:in|at)"
                        ],
                        "check_type": "conditional",  # Required if arbitration exists
                        "condition": r"arbitration",
                        "severity": "Medium"
                    },
                    {
                        "id": "arb_003",
                        "name": "Number of Arbitrators",
                        "description": "Number of arbitrators should be specified",
                        "patterns": [
                            r"(?:one|two|three|single|sole)\s+arbitrator",
                            r"(?:1|2|3)\s+arbitrator",
                            r"panel\s+of\s+arbitrators"
                        ],
                        "check_type": "conditional",
                        "condition": r"arbitration",
                        "severity": "Low"
                    }
                ]
            },
            "it_act": {
                "name": "Information Technology Act, 2000",
                "checks": [
                    {
                        "id": "it_001",
                        "name": "Electronic Signatures",
                        "description": "Electronic signatures should comply with IT Act",
                        "patterns": [
                            r"electronic\s+signature",
                            r"digital\s+signature",
                            r"e-sign"
                        ],
                        "check_type": "info",
                        "severity": "Low"
                    },
                    {
                        "id": "it_002",
                        "name": "Data Protection",
                        "description": "Sensitive personal data handling should be addressed",
                        "patterns": [
                            r"personal\s+data",
                            r"sensitive\s+(?:personal\s+)?information",
                            r"data\s+protection",
                            r"privacy"
                        ],
                        "check_type": "info",
                        "severity": "Medium"
                    }
                ]
            },
            "stamp_act": {
                "name": "Indian Stamp Act, 1899",
                "checks": [
                    {
                        "id": "stamp_001",
                        "name": "Stamp Duty Mention",
                        "description": "Stamp duty applicability should be mentioned",
                        "patterns": [
                            r"stamp\s+duty",
                            r"stamped",
                            r"registration"
                        ],
                        "check_type": "recommended",
                        "severity": "Medium"
                    }
                ]
            },
            "competition_act": {
                "name": "Competition Act, 2002",
                "checks": [
                    {
                        "id": "comp_001",
                        "name": "Anti-Competitive Clauses",
                        "description": "Non-compete clauses must be reasonable",
                        "patterns": [
                            r"non[\s-]?compete",
                            r"exclusive\s+(?:dealing|supply|purchase)",
                            r"tie[\s-]?in",
                            r"market\s+(?:allocation|division)"
                        ],
                        "check_type": "warning",
                        "severity": "High"
                    },
                    {
                        "id": "comp_002",
                        "name": "Unreasonable Restrictions",
                        "description": "Restrictions should not be anti-competitive",
                        "patterns": [
                            r"perpetual\s+(?:non[\s-]?compete|restriction)",
                            r"worldwide\s+(?:non[\s-]?compete|restriction)",
                            r"unlimited\s+(?:territory|scope)"
                        ],
                        "check_type": "absence",
                        "severity": "High"
                    }
                ]
            },
            "consumer_protection": {
                "name": "Consumer Protection Act, 2019",
                "checks": [
                    {
                        "id": "cp_001",
                        "name": "Unfair Contract Terms",
                        "description": "Contract should not have unfair terms against consumers",
                        "patterns": [
                            r"non[\s-]?refundable",
                            r"no\s+(?:refund|return)",
                            r"all\s+sales?\s+(?:are\s+)?final"
                        ],
                        "check_type": "warning",
                        "severity": "Medium"
                    }
                ]
            },
            "labour_laws": {
                "name": "Labour Laws (Employment Contracts)",
                "checks": [
                    {
                        "id": "lab_001",
                        "name": "Minimum Wage Compliance",
                        "description": "Wages should meet minimum wage requirements",
                        "patterns": [
                            r"salary",
                            r"wages",
                            r"compensation",
                            r"remuneration"
                        ],
                        "check_type": "info",
                        "severity": "High"
                    },
                    {
                        "id": "lab_002",
                        "name": "Working Hours",
                        "description": "Working hours should comply with regulations",
                        "patterns": [
                            r"working\s+hours",
                            r"work\s+(?:hours|time)",
                            r"overtime"
                        ],
                        "check_type": "info",
                        "severity": "Medium"
                    },
                    {
                        "id": "lab_003",
                        "name": "Leave Provisions",
                        "description": "Leave entitlements should be specified",
                        "patterns": [
                            r"leave",
                            r"holiday",
                            r"vacation",
                            r"paid\s+time\s+off"
                        ],
                        "check_type": "recommended",
                        "severity": "Medium"
                    },
                    {
                        "id": "lab_004",
                        "name": "Termination Notice",
                        "description": "Notice period for termination should be specified",
                        "patterns": [
                            r"notice\s+period",
                            r"termination\s+notice",
                            r"resignation\s+notice"
                        ],
                        "check_type": "recommended",
                        "severity": "Medium"
                    }
                ]
            }
        }
        
        # Contract type specific requirements
        self.type_requirements = {
            "Employment Agreement": [
                "labour_laws",
                "indian_contract_act"
            ],
            "Vendor Contract": [
                "indian_contract_act",
                "stamp_act"
            ],
            "Lease Agreement": [
                "indian_contract_act",
                "stamp_act"
            ],
            "Service Contract": [
                "indian_contract_act",
                "it_act"
            ],
            "Non-Disclosure Agreement": [
                "indian_contract_act",
                "it_act"
            ],
            "Partnership Deed": [
                "indian_contract_act",
                "stamp_act"
            ]
        }
    
    def check_compliance(self, text: str, 
                         contract_type: Optional[str] = None) -> ComplianceReport:
        """
        Check contract compliance with applicable laws.
        
        Args:
            text: Contract text to check
            contract_type: Optional contract type for targeted checks
            
        Returns:
            ComplianceReport with findings
        """
        text_lower = text.lower()
        issues = []
        compliant_areas = []
        missing_requirements = []
        laws_checked = []
        
        # Determine which laws to check
        if contract_type and contract_type in self.type_requirements:
            laws_to_check = self.type_requirements[contract_type]
        else:
            laws_to_check = list(self.compliance_rules.keys())
        
        # Check each applicable law
        for law_key in laws_to_check:
            if law_key not in self.compliance_rules:
                continue
                
            law = self.compliance_rules[law_key]
            laws_checked.append(law["name"])
            
            for check in law["checks"]:
                result = self._perform_check(text_lower, check, law["name"])
                
                if result["status"] == "issue":
                    issues.append(ComplianceIssue(
                        issue_id=check["id"],
                        law_reference=law["name"],
                        clause_text=result.get("matched_text", ""),
                        issue_description=result["description"],
                        severity=check["severity"],
                        recommendation=result["recommendation"],
                        risk_if_ignored=result["risk"]
                    ))
                elif result["status"] == "compliant":
                    compliant_areas.append(f"{law['name']}: {check['name']}")
                elif result["status"] == "missing":
                    missing_requirements.append(f"{check['name']} ({law['name']})")
        
        # Determine overall status
        if any(i.severity == "Critical" for i in issues):
            overall_status = ComplianceStatus.NON_COMPLIANT
        elif any(i.severity == "High" for i in issues):
            overall_status = ComplianceStatus.PARTIALLY_COMPLIANT
        elif issues:
            overall_status = ComplianceStatus.NEEDS_REVIEW
        else:
            overall_status = ComplianceStatus.COMPLIANT
        
        # Generate recommendations
        recommendations = self._generate_recommendations(issues, missing_requirements)
        
        return ComplianceReport(
            overall_status=overall_status,
            issues=issues,
            compliant_areas=compliant_areas,
            missing_requirements=missing_requirements,
            recommendations=recommendations,
            laws_checked=laws_checked
        )
    
    def _perform_check(self, text: str, check: Dict, law_name: str) -> Dict:
        """
        Perform a single compliance check.
        
        Args:
            text: Lowercase contract text
            check: Check configuration
            law_name: Name of the law being checked
            
        Returns:
            Dictionary with check result
        """
        check_type = check["check_type"]
        patterns = check["patterns"]
        
        # Find matches
        matches = []
        for pattern in patterns:
            found = re.findall(pattern, text)
            matches.extend(found)
        
        has_matches = len(matches) > 0
        
        if check_type == "absence":
            # These patterns should NOT be present
            if has_matches:
                return {
                    "status": "issue",
                    "description": f"Found concerning language related to {check['name']}",
                    "matched_text": matches[0] if matches else "",
                    "recommendation": f"Review and remove or modify language related to: {', '.join(matches[:3])}",
                    "risk": f"May violate {law_name}"
                }
            else:
                return {"status": "compliant"}
        
        elif check_type == "presence":
            # These patterns SHOULD be present
            if has_matches:
                return {"status": "compliant"}
            else:
                return {
                    "status": "missing",
                    "description": f"Missing required element: {check['name']}",
                    "recommendation": f"Add {check['name']} clause to comply with {law_name}",
                    "risk": f"Contract may be incomplete under {law_name}"
                }
        
        elif check_type == "conditional":
            # Check only if condition is met
            condition = check.get("condition", "")
            if condition and re.search(condition, text):
                if not has_matches:
                    return {
                        "status": "issue",
                        "description": f"Missing specification for {check['name']}",
                        "matched_text": "",
                        "recommendation": f"Specify {check['name']} as required by {law_name}",
                        "risk": f"Arbitration clause may be incomplete"
                    }
            return {"status": "compliant"}
        
        elif check_type == "warning":
            # Flag for review if present
            if has_matches:
                return {
                    "status": "issue",
                    "description": f"Contains {check['name']} that may need review",
                    "matched_text": matches[0] if matches else "",
                    "recommendation": f"Review {check['name']} for compliance with {law_name}",
                    "risk": f"May have implications under {law_name}"
                }
            return {"status": "compliant"}
        
        elif check_type == "recommended":
            # Recommended but not required
            if not has_matches:
                return {
                    "status": "missing",
                    "description": f"Recommended element missing: {check['name']}",
                    "recommendation": f"Consider adding {check['name']}",
                    "risk": "Best practice not followed"
                }
            return {"status": "compliant"}
        
        else:  # info
            return {"status": "compliant"}
    
    def _generate_recommendations(self, issues: List[ComplianceIssue],
                                   missing: List[str]) -> List[str]:
        """Generate compliance recommendations."""
        recommendations = []
        
        # Critical issues first
        critical = [i for i in issues if i.severity == "Critical"]
        if critical:
            recommendations.append("⚠️ CRITICAL: Address critical compliance issues before signing")
            for issue in critical[:3]:
                recommendations.append(f"  - {issue.recommendation}")
        
        # High severity issues
        high = [i for i in issues if i.severity == "High"]
        if high:
            recommendations.append("⚡ HIGH PRIORITY: Review high-severity issues")
            for issue in high[:3]:
                recommendations.append(f"  - {issue.recommendation}")
        
        # Missing requirements
        if missing:
            recommendations.append("📋 MISSING: Add recommended elements")
            for m in missing[:5]:
                recommendations.append(f"  - Add {m}")
        
        # General recommendations
        if not issues and not missing:
            recommendations.append("✅ Contract appears compliant with checked laws")
            recommendations.append("Consider legal review for complete assurance")
        
        return recommendations
    
    def get_applicable_laws(self, contract_type: str) -> List[Dict]:
        """
        Get list of applicable laws for a contract type.
        
        Args:
            contract_type: Type of contract
            
        Returns:
            List of applicable law information
        """
        law_keys = self.type_requirements.get(contract_type, list(self.compliance_rules.keys()))
        
        laws = []
        for key in law_keys:
            if key in self.compliance_rules:
                law = self.compliance_rules[key]
                laws.append({
                    "key": key,
                    "name": law["name"],
                    "check_count": len(law["checks"]),
                    "checks": [c["name"] for c in law["checks"]]
                })
        
        return laws
    
    def get_compliance_summary(self, report: ComplianceReport) -> Dict:
        """
        Generate a summary of the compliance report.
        
        Args:
            report: ComplianceReport to summarize
            
        Returns:
            Dictionary with summary
        """
        return {
            "status": report.overall_status.value,
            "total_issues": len(report.issues),
            "critical_issues": sum(1 for i in report.issues if i.severity == "Critical"),
            "high_issues": sum(1 for i in report.issues if i.severity == "High"),
            "medium_issues": sum(1 for i in report.issues if i.severity == "Medium"),
            "low_issues": sum(1 for i in report.issues if i.severity == "Low"),
            "compliant_areas_count": len(report.compliant_areas),
            "missing_requirements_count": len(report.missing_requirements),
            "laws_checked": report.laws_checked,
            "top_recommendations": report.recommendations[:5]
        }

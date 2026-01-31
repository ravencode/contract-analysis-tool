"""
Risk Analysis Module
Comprehensive risk scoring and assessment for contracts
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum
import math


class RiskLevel(Enum):
    """Risk level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ClauseRisk:
    """Risk assessment for a single clause."""
    clause_id: str
    clause_type: str
    clause_text: str
    risk_level: RiskLevel
    risk_score: float  # 0.0 to 1.0
    risk_factors: List[str]
    red_flags: List[str]
    impact_description: str
    mitigation_suggestions: List[str]
    category: str


@dataclass
class ContractRisk:
    """Overall contract risk assessment."""
    overall_score: float
    overall_level: RiskLevel
    clause_risks: List[ClauseRisk]
    high_risk_clauses: List[ClauseRisk]
    risk_distribution: Dict[str, int]
    category_scores: Dict[str, float]
    priority_issues: List[str]
    recommendations: List[str]


class RiskAnalyzer:
    """
    Comprehensive risk analysis engine for legal contracts.
    Analyzes clauses for potential risks and generates risk scores.
    """
    
    def __init__(self):
        # Risk category definitions with patterns and weights
        self.risk_categories = {
            "penalty_clause": {
                "name": "Penalty Clauses",
                "patterns": [
                    r"penalty\s+of\s+(?:rs\.?|inr|₹)?\s*[\d,]+",
                    r"liquidated\s+damages",
                    r"forfeit",
                    r"fine\s+of",
                    r"punitive\s+damages"
                ],
                "keywords": ["penalty", "liquidated damages", "fine", "forfeit", "punitive"],
                "weight": 0.15,
                "base_risk": 0.6,
                "description": "Financial penalties for non-compliance"
            },
            "indemnity_clause": {
                "name": "Indemnity Clauses",
                "patterns": [
                    r"indemnify\s+and\s+hold\s+harmless",
                    r"shall\s+indemnify",
                    r"indemnification\s+obligation",
                    r"defend\s+and\s+indemnify"
                ],
                "keywords": ["indemnify", "indemnification", "hold harmless", "defend"],
                "weight": 0.15,
                "base_risk": 0.5,
                "description": "Obligation to compensate for losses"
            },
            "termination_clause": {
                "name": "Unilateral Termination",
                "patterns": [
                    r"terminate\s+(?:this\s+)?agreement\s+(?:at\s+)?(?:its?\s+)?(?:sole\s+)?discretion",
                    r"terminate\s+without\s+(?:any\s+)?(?:cause|reason)",
                    r"immediate\s+termination",
                    r"terminate\s+forthwith"
                ],
                "keywords": ["terminate", "termination", "cancel", "revoke"],
                "weight": 0.12,
                "base_risk": 0.7,
                "description": "One-sided termination rights"
            },
            "arbitration_clause": {
                "name": "Arbitration & Jurisdiction",
                "patterns": [
                    r"arbitration\s+(?:in|at)\s+\w+",
                    r"exclusive\s+jurisdiction",
                    r"courts?\s+(?:of|at|in)\s+\w+\s+shall\s+have",
                    r"governed\s+by\s+the\s+laws?\s+of"
                ],
                "keywords": ["arbitration", "jurisdiction", "dispute resolution", "governing law"],
                "weight": 0.10,
                "base_risk": 0.4,
                "description": "Dispute resolution mechanism"
            },
            "auto_renewal": {
                "name": "Auto-Renewal & Lock-in",
                "patterns": [
                    r"auto(?:matic(?:ally)?)?[\s-]?renew",
                    r"lock[\s-]?in\s+period",
                    r"minimum\s+(?:term|period|commitment)",
                    r"shall\s+(?:automatically\s+)?(?:be\s+)?renewed"
                ],
                "keywords": ["auto-renewal", "automatic renewal", "lock-in", "minimum term"],
                "weight": 0.10,
                "base_risk": 0.5,
                "description": "Automatic contract extension"
            },
            "non_compete": {
                "name": "Non-Compete Clauses",
                "patterns": [
                    r"non[\s-]?compete",
                    r"not\s+(?:directly\s+or\s+indirectly\s+)?(?:engage|compete)",
                    r"restrictive\s+covenant",
                    r"shall\s+not\s+(?:carry\s+on|engage\s+in)"
                ],
                "keywords": ["non-compete", "non-competition", "restrictive covenant", "compete"],
                "weight": 0.12,
                "base_risk": 0.6,
                "description": "Restrictions on competitive activities"
            },
            "ip_transfer": {
                "name": "IP Transfer Clauses",
                "patterns": [
                    r"(?:all\s+)?intellectual\s+property\s+(?:rights?\s+)?(?:shall\s+)?(?:belong|vest|transfer)",
                    r"assign(?:s|ment)?\s+(?:all\s+)?(?:right|title|interest)",
                    r"work[\s-]?(?:made[\s-]?)?for[\s-]?hire",
                    r"ownership\s+of\s+(?:all\s+)?(?:work|deliverables|ip)"
                ],
                "keywords": ["intellectual property", "ip rights", "patent", "copyright", "ownership"],
                "weight": 0.13,
                "base_risk": 0.6,
                "description": "Transfer of intellectual property rights"
            },
            "liability_limitation": {
                "name": "Liability Limitation",
                "patterns": [
                    r"(?:total|aggregate|maximum)\s+liability\s+(?:shall\s+)?(?:not\s+)?exceed",
                    r"cap\s+(?:on\s+)?liability",
                    r"exclude(?:s|d)?\s+(?:all\s+)?liability",
                    r"in\s+no\s+event\s+(?:shall|will)\s+(?:\w+\s+)?be\s+liable"
                ],
                "keywords": ["limitation of liability", "cap on liability", "exclude liability"],
                "weight": 0.08,
                "base_risk": 0.5,
                "description": "Limits on liability exposure"
            },
            "confidentiality": {
                "name": "Confidentiality & NDA",
                "patterns": [
                    r"confidential\s+information",
                    r"non[\s-]?disclosure",
                    r"proprietary\s+information",
                    r"trade\s+secret"
                ],
                "keywords": ["confidential", "confidentiality", "non-disclosure", "proprietary"],
                "weight": 0.05,
                "base_risk": 0.3,
                "description": "Protection of confidential information"
            },
            "unlimited_liability": {
                "name": "Unlimited Liability",
                "patterns": [
                    r"unlimited\s+liability",
                    r"fully\s+liable",
                    r"liable\s+(?:for\s+)?(?:all|any)\s+(?:losses?|damages?)",
                    r"without\s+(?:any\s+)?limitation"
                ],
                "keywords": ["unlimited liability", "fully liable", "all losses"],
                "weight": 0.15,
                "base_risk": 0.9,
                "description": "No cap on liability exposure"
            },
            "unilateral_amendment": {
                "name": "Unilateral Amendment",
                "patterns": [
                    r"(?:may|shall\s+have\s+the\s+right\s+to)\s+(?:amend|modify|change)\s+(?:this\s+agreement|these\s+terms)",
                    r"(?:sole|absolute)\s+discretion\s+(?:to\s+)?(?:amend|modify)",
                    r"reserves?\s+the\s+right\s+to\s+(?:amend|modify|change)"
                ],
                "keywords": ["amend", "modify", "change", "sole discretion"],
                "weight": 0.10,
                "base_risk": 0.7,
                "description": "One-sided right to change terms"
            },
            "waiver_of_rights": {
                "name": "Waiver of Rights",
                "patterns": [
                    r"waive(?:s|r)?\s+(?:any\s+)?(?:right|claim)",
                    r"release(?:s|d)?\s+(?:and\s+)?(?:discharge)?",
                    r"forever\s+(?:waive|release|discharge)"
                ],
                "keywords": ["waive", "waiver", "release", "discharge", "relinquish"],
                "weight": 0.08,
                "base_risk": 0.6,
                "description": "Giving up legal rights"
            }
        }
        
        # Red flag patterns (always high risk)
        self.red_flags = [
            (r"sole\s+and\s+absolute\s+discretion", "Absolute discretion given to one party"),
            (r"without\s+(?:any\s+)?(?:cause|reason|notice)", "Action without cause or notice"),
            (r"irrevocable", "Irrevocable commitment"),
            (r"perpetual(?:ly)?", "Perpetual obligation"),
            (r"unconditional(?:ly)?", "Unconditional obligation"),
            (r"(?:shall|will)\s+not\s+(?:be\s+)?(?:entitled|have\s+(?:any\s+)?right)", "Denial of rights"),
            (r"at\s+(?:its?|their)\s+(?:own\s+)?(?:sole\s+)?(?:cost|expense)", "Cost burden on one party"),
            (r"(?:any|all)\s+(?:claims?|disputes?)\s+(?:shall\s+)?(?:be\s+)?(?:waived|released)", "Waiver of claims"),
            (r"binding\s+(?:and\s+)?(?:final|conclusive)", "Binding without recourse"),
            (r"(?:no|without)\s+(?:right\s+(?:of|to)\s+)?appeal", "No right of appeal")
        ]
        
        # Ambiguity patterns
        self.ambiguity_patterns = [
            (r"\breasonable\b", "Subjective 'reasonable' standard"),
            (r"\bmaterial(?:ly)?\b", "Undefined 'material' threshold"),
            (r"\bsubstantial(?:ly)?\b", "Vague 'substantial' quantifier"),
            (r"\bpromptly\b", "Undefined 'promptly' timeframe"),
            (r"\btimely\b", "Undefined 'timely' timeframe"),
            (r"\bbest\s+efforts?\b", "Unclear 'best efforts' standard"),
            (r"\breasonable\s+efforts?\b", "Unclear 'reasonable efforts' standard"),
            (r"\bas\s+(?:needed|required|appropriate)\b", "Discretionary language"),
            (r"\band/or\b", "Ambiguous 'and/or' conjunction"),
            (r"\bincluding\s+(?:but\s+)?not\s+limited\s+to\b", "Open-ended list")
        ]
    
    def analyze_contract(self, text: str, 
                         clauses: Optional[List[Dict]] = None) -> ContractRisk:
        """
        Perform comprehensive risk analysis on a contract.
        
        Args:
            text: Full contract text
            clauses: Optional list of parsed clauses
            
        Returns:
            ContractRisk object with complete analysis
        """
        # If clauses not provided, analyze full text
        if clauses:
            clause_risks = [self.analyze_clause(c) for c in clauses]
        else:
            # Split text into sections and analyze
            sections = self._split_into_sections(text)
            clause_risks = [self.analyze_clause({
                'id': f'section_{i}',
                'type': 'unknown',
                'text': section
            }) for i, section in enumerate(sections)]
        
        # Calculate overall metrics
        overall_score = self._calculate_overall_score(clause_risks)
        overall_level = self._score_to_level(overall_score)
        
        # Get high risk clauses
        high_risk = [cr for cr in clause_risks if cr.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]]
        
        # Calculate distribution
        distribution = {
            'low': sum(1 for cr in clause_risks if cr.risk_level == RiskLevel.LOW),
            'medium': sum(1 for cr in clause_risks if cr.risk_level == RiskLevel.MEDIUM),
            'high': sum(1 for cr in clause_risks if cr.risk_level == RiskLevel.HIGH),
            'critical': sum(1 for cr in clause_risks if cr.risk_level == RiskLevel.CRITICAL)
        }
        
        # Calculate category scores
        category_scores = self._calculate_category_scores(clause_risks)
        
        # Generate priority issues
        priority_issues = self._identify_priority_issues(clause_risks)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(clause_risks, overall_score)
        
        return ContractRisk(
            overall_score=round(overall_score, 2),
            overall_level=overall_level,
            clause_risks=clause_risks,
            high_risk_clauses=high_risk,
            risk_distribution=distribution,
            category_scores=category_scores,
            priority_issues=priority_issues,
            recommendations=recommendations
        )
    
    def analyze_clause(self, clause: Dict) -> ClauseRisk:
        """
        Analyze risk for a single clause.
        
        Args:
            clause: Dictionary with clause info (id, type, text)
            
        Returns:
            ClauseRisk object
        """
        clause_id = clause.get('id', 'unknown')
        clause_type = clause.get('type', 'unknown')
        clause_text = clause.get('text', '')
        
        text_lower = clause_text.lower()
        
        risk_factors = []
        red_flags = []
        category_scores = {}
        
        # Check each risk category
        for category, config in self.risk_categories.items():
            category_score = 0.0
            
            # Check patterns
            for pattern in config['patterns']:
                matches = re.findall(pattern, text_lower)
                if matches:
                    category_score += len(matches) * 0.3
                    risk_factors.append(f"{config['name']}: Pattern match found")
            
            # Check keywords
            for keyword in config['keywords']:
                if keyword.lower() in text_lower:
                    category_score += 0.2
            
            if category_score > 0:
                category_scores[category] = min(category_score + config['base_risk'], 1.0)
        
        # Check red flags
        for pattern, description in self.red_flags:
            if re.search(pattern, text_lower):
                red_flags.append(description)
        
        # Check ambiguities
        ambiguities = []
        for pattern, description in self.ambiguity_patterns:
            if re.search(pattern, text_lower):
                ambiguities.append(description)
        
        if ambiguities:
            risk_factors.append(f"Ambiguous language: {len(ambiguities)} instances")
        
        # Calculate overall clause risk score
        if category_scores:
            weighted_score = sum(
                score * self.risk_categories[cat]['weight']
                for cat, score in category_scores.items()
            )
            base_score = max(category_scores.values())
            risk_score = (weighted_score * 0.4) + (base_score * 0.6)
        else:
            risk_score = 0.2  # Base risk for any clause
        
        # Adjust for red flags
        if red_flags:
            risk_score = min(risk_score + (len(red_flags) * 0.15), 1.0)
        
        # Determine risk level
        risk_level = self._score_to_level(risk_score)
        
        # Determine primary category
        if category_scores:
            primary_category = max(category_scores, key=category_scores.get)
        else:
            primary_category = "general"
        
        # Generate impact description
        impact = self._generate_impact_description(primary_category, risk_level)
        
        # Generate mitigation suggestions
        mitigations = self._generate_mitigations(primary_category, risk_factors, red_flags)
        
        return ClauseRisk(
            clause_id=clause_id,
            clause_type=clause_type,
            clause_text=clause_text[:500] + "..." if len(clause_text) > 500 else clause_text,
            risk_level=risk_level,
            risk_score=round(risk_score, 2),
            risk_factors=risk_factors,
            red_flags=red_flags,
            impact_description=impact,
            mitigation_suggestions=mitigations,
            category=primary_category
        )
    
    def _split_into_sections(self, text: str) -> List[str]:
        """Split text into analyzable sections."""
        # Split by common section markers
        patterns = [
            r'\n\d+\.\s+[A-Z]',
            r'\n[A-Z][A-Z\s]+\n',
            r'\n\n+'
        ]
        
        sections = [text]
        for pattern in patterns:
            new_sections = []
            for section in sections:
                parts = re.split(pattern, section)
                new_sections.extend([p.strip() for p in parts if p.strip()])
            sections = new_sections
        
        # Filter out very short sections
        sections = [s for s in sections if len(s) > 100]
        
        return sections if sections else [text]
    
    def _score_to_level(self, score: float) -> RiskLevel:
        """Convert numeric score to risk level."""
        if score >= 0.8:
            return RiskLevel.CRITICAL
        elif score >= 0.6:
            return RiskLevel.HIGH
        elif score >= 0.35:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _calculate_overall_score(self, clause_risks: List[ClauseRisk]) -> float:
        """Calculate overall contract risk score."""
        if not clause_risks:
            return 0.5
        
        # Weighted average with emphasis on high-risk clauses
        scores = [cr.risk_score for cr in clause_risks]
        
        # Simple average
        avg_score = sum(scores) / len(scores)
        
        # Max score influence
        max_score = max(scores)
        
        # Count of high-risk clauses influence
        high_risk_count = sum(1 for cr in clause_risks 
                            if cr.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL])
        high_risk_factor = min(high_risk_count * 0.1, 0.3)
        
        # Combined score
        overall = (avg_score * 0.4) + (max_score * 0.4) + high_risk_factor
        
        return min(overall, 1.0)
    
    def _calculate_category_scores(self, clause_risks: List[ClauseRisk]) -> Dict[str, float]:
        """Calculate risk scores by category."""
        category_scores = {}
        category_counts = {}
        
        for cr in clause_risks:
            cat = cr.category
            if cat not in category_scores:
                category_scores[cat] = 0.0
                category_counts[cat] = 0
            category_scores[cat] += cr.risk_score
            category_counts[cat] += 1
        
        # Average by category
        for cat in category_scores:
            if category_counts[cat] > 0:
                category_scores[cat] = round(category_scores[cat] / category_counts[cat], 2)
        
        return category_scores
    
    def _identify_priority_issues(self, clause_risks: List[ClauseRisk]) -> List[str]:
        """Identify priority issues from clause risks."""
        issues = []
        
        # Collect all red flags
        for cr in clause_risks:
            for flag in cr.red_flags:
                if flag not in issues:
                    issues.append(flag)
        
        # Add high-risk categories
        high_risk = [cr for cr in clause_risks if cr.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]]
        for cr in high_risk:
            cat_name = self.risk_categories.get(cr.category, {}).get('name', cr.category)
            issue = f"High-risk {cat_name} detected"
            if issue not in issues:
                issues.append(issue)
        
        return issues[:10]  # Top 10 issues
    
    def _generate_recommendations(self, clause_risks: List[ClauseRisk], 
                                   overall_score: float) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []
        
        if overall_score >= 0.7:
            recommendations.append("[!] HIGH RISK: Strongly recommend legal review before signing")
            recommendations.append("Consider renegotiating major terms")
        elif overall_score >= 0.5:
            recommendations.append("[!] MODERATE RISK: Legal review recommended")
            recommendations.append("Review highlighted clauses carefully")
        else:
            recommendations.append("[OK] LOW RISK: Contract appears reasonable")
            recommendations.append("Standard review recommended")
        
        # Category-specific recommendations
        categories_found = set(cr.category for cr in clause_risks if cr.risk_score > 0.5)
        
        if 'penalty_clause' in categories_found:
            recommendations.append("Negotiate penalty caps or removal")
        if 'indemnity_clause' in categories_found:
            recommendations.append("Request mutual indemnification or caps")
        if 'termination_clause' in categories_found:
            recommendations.append("Ensure termination rights are balanced")
        if 'non_compete' in categories_found:
            recommendations.append("Review non-compete scope and duration")
        if 'ip_transfer' in categories_found:
            recommendations.append("Clarify IP ownership and licensing terms")
        if 'unlimited_liability' in categories_found:
            recommendations.append("CRITICAL: Negotiate liability caps")
        
        return recommendations
    
    def _generate_impact_description(self, category: str, risk_level: RiskLevel) -> str:
        """Generate impact description for a risk category."""
        impacts = {
            "penalty_clause": "May result in significant financial penalties if obligations are not met",
            "indemnity_clause": "Could require compensation for third-party claims or losses",
            "termination_clause": "Contract may be terminated unexpectedly, disrupting business",
            "arbitration_clause": "Disputes may need to be resolved in specific jurisdiction",
            "auto_renewal": "Contract may automatically extend, creating ongoing obligations",
            "non_compete": "May restrict future business activities and opportunities",
            "ip_transfer": "May lose ownership of created intellectual property",
            "liability_limitation": "May limit ability to recover damages",
            "confidentiality": "Imposes obligations to protect information",
            "unlimited_liability": "Full exposure to all potential losses without cap",
            "unilateral_amendment": "Terms may change without consent",
            "waiver_of_rights": "May lose important legal protections"
        }
        
        base_impact = impacts.get(category, "May have legal or financial implications")
        
        if risk_level == RiskLevel.CRITICAL:
            return f"CRITICAL: {base_impact}. Immediate attention required."
        elif risk_level == RiskLevel.HIGH:
            return f"HIGH RISK: {base_impact}. Careful review needed."
        elif risk_level == RiskLevel.MEDIUM:
            return f"MODERATE: {base_impact}. Consider negotiating."
        else:
            return f"LOW RISK: {base_impact}. Standard terms."
    
    def _generate_mitigations(self, category: str, 
                              risk_factors: List[str],
                              red_flags: List[str]) -> List[str]:
        """Generate mitigation suggestions."""
        mitigations = {
            "penalty_clause": [
                "Negotiate a cap on total penalties",
                "Request cure period before penalties apply",
                "Add force majeure exceptions"
            ],
            "indemnity_clause": [
                "Request mutual indemnification",
                "Add cap on indemnity obligations",
                "Limit to direct damages only"
            ],
            "termination_clause": [
                "Add termination for convenience for both parties",
                "Require reasonable notice period",
                "Include cure period for breaches"
            ],
            "non_compete": [
                "Limit geographic scope",
                "Reduce duration to reasonable period",
                "Narrow scope of restricted activities"
            ],
            "ip_transfer": [
                "Retain license to use created IP",
                "Limit transfer to project-specific IP",
                "Add fair compensation for IP transfer"
            ],
            "unlimited_liability": [
                "Add liability cap (e.g., contract value)",
                "Exclude consequential damages",
                "Add insurance requirements"
            ]
        }
        
        suggestions = mitigations.get(category, [
            "Review clause with legal counsel",
            "Consider negotiating more balanced terms",
            "Document any concerns before signing"
        ])
        
        if red_flags:
            suggestions.insert(0, "Address red flags before proceeding")
        
        return suggestions
    
    def get_risk_summary(self, contract_risk: ContractRisk) -> Dict:
        """Generate a summary of the risk analysis."""
        return {
            'overall_risk_score': contract_risk.overall_score,
            'overall_risk_level': contract_risk.overall_level.value,
            'total_clauses_analyzed': len(contract_risk.clause_risks),
            'high_risk_clause_count': len(contract_risk.high_risk_clauses),
            'risk_distribution': contract_risk.risk_distribution,
            'top_risk_categories': sorted(
                contract_risk.category_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5],
            'priority_issues': contract_risk.priority_issues[:5],
            'key_recommendations': contract_risk.recommendations[:5]
        }

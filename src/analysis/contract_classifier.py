"""
Contract Classification Module
Classifies contracts into predefined categories
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from collections import Counter


@dataclass
class ClassificationResult:
    """Result of contract classification."""
    contract_type: str
    confidence: float
    secondary_types: List[Tuple[str, float]]
    indicators_found: Dict[str, List[str]]
    reasoning: str


class ContractClassifier:
    """
    Classifies contracts into predefined categories using
    keyword matching, pattern recognition, and structural analysis.
    """
    
    def __init__(self):
        # Contract type indicators
        self.contract_indicators = {
            "Employment Agreement": {
                "keywords": [
                    "employment", "employee", "employer", "salary", "wages",
                    "probation", "working hours", "leave", "resignation",
                    "termination of employment", "job title", "designation",
                    "reporting", "workplace", "benefits", "provident fund",
                    "gratuity", "bonus", "appraisal", "notice period"
                ],
                "patterns": [
                    r"employment\s+agreement",
                    r"letter\s+of\s+appointment",
                    r"offer\s+letter",
                    r"service\s+agreement",
                    r"terms\s+of\s+employment"
                ],
                "weight": 1.0
            },
            "Vendor Contract": {
                "keywords": [
                    "vendor", "supplier", "supply", "purchase order",
                    "procurement", "goods", "materials", "delivery",
                    "quality", "inspection", "rejection", "warranty",
                    "price", "payment terms", "invoice"
                ],
                "patterns": [
                    r"vendor\s+agreement",
                    r"supply\s+agreement",
                    r"purchase\s+agreement",
                    r"procurement\s+contract"
                ],
                "weight": 1.0
            },
            "Lease Agreement": {
                "keywords": [
                    "lease", "lessor", "lessee", "rent", "premises",
                    "tenant", "landlord", "property", "occupation",
                    "security deposit", "maintenance", "utilities",
                    "sub-lease", "eviction", "renewal", "lock-in"
                ],
                "patterns": [
                    r"lease\s+agreement",
                    r"rental\s+agreement",
                    r"tenancy\s+agreement",
                    r"leave\s+and\s+license"
                ],
                "weight": 1.0
            },
            "Partnership Deed": {
                "keywords": [
                    "partnership", "partner", "partners", "firm",
                    "profit sharing", "loss sharing", "capital contribution",
                    "partnership firm", "managing partner", "sleeping partner",
                    "dissolution", "goodwill", "partnership act"
                ],
                "patterns": [
                    r"partnership\s+deed",
                    r"partnership\s+agreement",
                    r"deed\s+of\s+partnership"
                ],
                "weight": 1.0
            },
            "Service Contract": {
                "keywords": [
                    "service", "services", "service provider", "client",
                    "scope of work", "deliverables", "milestones",
                    "service level", "sla", "performance", "acceptance",
                    "professional services", "consulting"
                ],
                "patterns": [
                    r"service\s+agreement",
                    r"master\s+service\s+agreement",
                    r"professional\s+services\s+agreement",
                    r"msa"
                ],
                "weight": 1.0
            },
            "Non-Disclosure Agreement": {
                "keywords": [
                    "confidential", "confidentiality", "non-disclosure",
                    "nda", "proprietary", "trade secret", "disclosure",
                    "receiving party", "disclosing party", "confidential information"
                ],
                "patterns": [
                    r"non-disclosure\s+agreement",
                    r"confidentiality\s+agreement",
                    r"nda",
                    r"mutual\s+nda"
                ],
                "weight": 1.2  # Higher weight as NDA is very specific
            },
            "Consultancy Agreement": {
                "keywords": [
                    "consultant", "consultancy", "advisory", "advisor",
                    "engagement", "professional fees", "retainer",
                    "independent contractor", "expertise", "recommendations"
                ],
                "patterns": [
                    r"consultancy\s+agreement",
                    r"consulting\s+agreement",
                    r"advisory\s+agreement",
                    r"engagement\s+letter"
                ],
                "weight": 1.0
            },
            "Supply Agreement": {
                "keywords": [
                    "supply", "supplier", "buyer", "goods", "products",
                    "quantity", "specifications", "delivery schedule",
                    "purchase price", "minimum order", "exclusivity"
                ],
                "patterns": [
                    r"supply\s+agreement",
                    r"distribution\s+agreement",
                    r"product\s+supply"
                ],
                "weight": 1.0
            },
            "Franchise Agreement": {
                "keywords": [
                    "franchise", "franchisor", "franchisee", "royalty",
                    "brand", "trademark license", "territory", "exclusivity",
                    "franchise fee", "training", "operations manual"
                ],
                "patterns": [
                    r"franchise\s+agreement",
                    r"franchising\s+agreement",
                    r"master\s+franchise"
                ],
                "weight": 1.0
            },
            "Joint Venture Agreement": {
                "keywords": [
                    "joint venture", "jv", "venture", "collaboration",
                    "joint enterprise", "co-venture", "profit sharing",
                    "management committee", "steering committee"
                ],
                "patterns": [
                    r"joint\s+venture\s+agreement",
                    r"jv\s+agreement",
                    r"collaboration\s+agreement"
                ],
                "weight": 1.0
            },
            "Loan Agreement": {
                "keywords": [
                    "loan", "lender", "borrower", "principal", "interest",
                    "repayment", "emi", "collateral", "security", "mortgage",
                    "default", "prepayment", "disbursement"
                ],
                "patterns": [
                    r"loan\s+agreement",
                    r"credit\s+agreement",
                    r"facility\s+agreement"
                ],
                "weight": 1.0
            },
            "Shareholders Agreement": {
                "keywords": [
                    "shareholder", "shareholders", "equity", "shares",
                    "voting rights", "board", "directors", "dividend",
                    "drag along", "tag along", "pre-emptive", "rofr"
                ],
                "patterns": [
                    r"shareholders?\s+agreement",
                    r"sha",
                    r"subscription\s+agreement"
                ],
                "weight": 1.0
            }
        }
        
        # Structural indicators
        self.structural_patterns = {
            "has_recitals": r"(WHEREAS|RECITALS|BACKGROUND)",
            "has_definitions": r"(DEFINITIONS|INTERPRETATION)",
            "has_schedules": r"(SCHEDULE|ANNEXURE|EXHIBIT)\s+[A-Z\d]",
            "has_signatures": r"(SIGNED|EXECUTED|WITNESS)",
            "has_parties": r"(BETWEEN|PARTY\s+OF\s+THE\s+FIRST\s+PART)"
        }
    
    def classify(self, text: str) -> ClassificationResult:
        """
        Classify a contract based on its content.
        
        Args:
            text: Contract text to classify
            
        Returns:
            ClassificationResult with classification details
        """
        text_lower = text.lower()
        scores = {}
        indicators_found = {}
        
        # Score each contract type
        for contract_type, config in self.contract_indicators.items():
            score = 0.0
            found_keywords = []
            found_patterns = []
            
            # Check keywords
            for keyword in config["keywords"]:
                count = len(re.findall(rf'\b{keyword}\b', text_lower))
                if count > 0:
                    score += count * 0.1
                    found_keywords.append(f"{keyword} ({count})")
            
            # Check patterns (higher weight)
            for pattern in config["patterns"]:
                matches = re.findall(pattern, text_lower)
                if matches:
                    score += len(matches) * 0.5
                    found_patterns.append(pattern)
            
            # Apply type weight
            score *= config["weight"]
            
            scores[contract_type] = score
            if found_keywords or found_patterns:
                indicators_found[contract_type] = {
                    "keywords": found_keywords[:10],
                    "patterns": found_patterns
                }
        
        # Normalize scores
        max_score = max(scores.values()) if scores else 1
        if max_score > 0:
            normalized_scores = {k: v / max_score for k, v in scores.items()}
        else:
            normalized_scores = scores
        
        # Get top classification
        sorted_types = sorted(normalized_scores.items(), key=lambda x: x[1], reverse=True)
        
        if sorted_types and sorted_types[0][1] > 0:
            primary_type = sorted_types[0][0]
            confidence = min(sorted_types[0][1], 1.0)
            
            # Adjust confidence based on structural analysis
            structure_score = self._analyze_structure(text)
            confidence = (confidence * 0.8) + (structure_score * 0.2)
        else:
            primary_type = "Unknown"
            confidence = 0.0
        
        # Get secondary types
        secondary_types = [
            (t, min(s, 1.0)) for t, s in sorted_types[1:4] if s > 0.3
        ]
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            primary_type, confidence, indicators_found.get(primary_type, {})
        )
        
        return ClassificationResult(
            contract_type=primary_type,
            confidence=round(confidence, 2),
            secondary_types=secondary_types,
            indicators_found=indicators_found,
            reasoning=reasoning
        )
    
    def _analyze_structure(self, text: str) -> float:
        """
        Analyze document structure to validate it's a contract.
        
        Returns:
            Score from 0 to 1 indicating how contract-like the structure is
        """
        score = 0.0
        checks = 0
        
        for pattern_name, pattern in self.structural_patterns.items():
            checks += 1
            if re.search(pattern, text, re.IGNORECASE):
                score += 1
        
        return score / checks if checks > 0 else 0
    
    def _generate_reasoning(self, contract_type: str, 
                           confidence: float,
                           indicators: Dict) -> str:
        """
        Generate human-readable reasoning for classification.
        """
        if contract_type == "Unknown":
            return "Unable to determine contract type. The document may not be a standard contract or may be missing key indicators."
        
        keywords = indicators.get("keywords", [])
        patterns = indicators.get("patterns", [])
        
        reasoning = f"Classified as {contract_type} with {confidence:.0%} confidence. "
        
        if patterns:
            reasoning += f"Found explicit mentions matching {contract_type} patterns. "
        
        if keywords:
            top_keywords = keywords[:5]
            reasoning += f"Key indicators found: {', '.join(top_keywords)}. "
        
        if confidence < 0.5:
            reasoning += "Low confidence - consider manual review."
        elif confidence < 0.75:
            reasoning += "Moderate confidence - verify classification."
        else:
            reasoning += "High confidence classification."
        
        return reasoning
    
    def get_contract_type_info(self, contract_type: str) -> Dict:
        """
        Get information about a contract type.
        
        Args:
            contract_type: The contract type to get info for
            
        Returns:
            Dictionary with contract type information
        """
        type_info = {
            "Employment Agreement": {
                "description": "Agreement between employer and employee defining terms of employment",
                "key_clauses": ["Job Description", "Compensation", "Benefits", "Termination", "Non-Compete", "Confidentiality"],
                "applicable_laws": ["Indian Contract Act", "Labour Laws", "Shops and Establishments Act"],
                "common_risks": ["Unfair termination terms", "Restrictive non-compete", "Unclear compensation structure"]
            },
            "Vendor Contract": {
                "description": "Agreement for supply of goods or materials from a vendor",
                "key_clauses": ["Specifications", "Pricing", "Delivery", "Quality", "Warranty", "Payment Terms"],
                "applicable_laws": ["Indian Contract Act", "Sale of Goods Act"],
                "common_risks": ["Quality issues", "Delivery delays", "Payment disputes"]
            },
            "Lease Agreement": {
                "description": "Agreement for rental of property or premises",
                "key_clauses": ["Rent", "Security Deposit", "Term", "Maintenance", "Termination", "Renewal"],
                "applicable_laws": ["Transfer of Property Act", "Rent Control Acts", "Stamp Act"],
                "common_risks": ["Lock-in periods", "Unfair termination", "Maintenance disputes"]
            },
            "Service Contract": {
                "description": "Agreement for provision of professional services",
                "key_clauses": ["Scope of Work", "Deliverables", "Payment", "Timeline", "Acceptance", "Liability"],
                "applicable_laws": ["Indian Contract Act", "IT Act (for digital services)"],
                "common_risks": ["Scope creep", "Unclear deliverables", "Payment delays"]
            },
            "Non-Disclosure Agreement": {
                "description": "Agreement to protect confidential information",
                "key_clauses": ["Definition of Confidential Information", "Obligations", "Exclusions", "Term", "Return of Information"],
                "applicable_laws": ["Indian Contract Act", "IT Act"],
                "common_risks": ["Overly broad definitions", "Perpetual obligations", "Unclear exceptions"]
            }
        }
        
        return type_info.get(contract_type, {
            "description": "Standard commercial agreement",
            "key_clauses": ["Terms", "Obligations", "Payment", "Termination", "Dispute Resolution"],
            "applicable_laws": ["Indian Contract Act"],
            "common_risks": ["Unfavorable terms", "Unclear obligations", "Dispute resolution issues"]
        })
    
    def suggest_required_clauses(self, contract_type: str) -> List[str]:
        """
        Suggest required clauses for a contract type.
        
        Args:
            contract_type: The contract type
            
        Returns:
            List of recommended clauses
        """
        required_clauses = {
            "Employment Agreement": [
                "Definitions",
                "Position and Duties",
                "Compensation and Benefits",
                "Working Hours",
                "Leave Policy",
                "Probation Period",
                "Termination",
                "Notice Period",
                "Confidentiality",
                "Non-Compete",
                "Intellectual Property",
                "Dispute Resolution",
                "Governing Law"
            ],
            "Vendor Contract": [
                "Definitions",
                "Scope of Supply",
                "Specifications",
                "Pricing",
                "Payment Terms",
                "Delivery",
                "Inspection and Acceptance",
                "Warranty",
                "Indemnification",
                "Limitation of Liability",
                "Termination",
                "Dispute Resolution"
            ],
            "Lease Agreement": [
                "Definitions",
                "Premises Description",
                "Term",
                "Rent and Payment",
                "Security Deposit",
                "Maintenance",
                "Permitted Use",
                "Alterations",
                "Insurance",
                "Termination",
                "Renewal",
                "Dispute Resolution"
            ],
            "Service Contract": [
                "Definitions",
                "Scope of Services",
                "Deliverables",
                "Timeline",
                "Payment Terms",
                "Acceptance Criteria",
                "Warranties",
                "Confidentiality",
                "Intellectual Property",
                "Indemnification",
                "Limitation of Liability",
                "Termination",
                "Dispute Resolution"
            ],
            "Non-Disclosure Agreement": [
                "Definitions",
                "Confidential Information",
                "Obligations of Receiving Party",
                "Exclusions",
                "Term",
                "Return of Information",
                "Remedies",
                "No License",
                "Governing Law"
            ]
        }
        
        return required_clauses.get(contract_type, [
            "Definitions",
            "Scope",
            "Obligations",
            "Payment",
            "Term",
            "Termination",
            "Confidentiality",
            "Dispute Resolution",
            "Governing Law"
        ])

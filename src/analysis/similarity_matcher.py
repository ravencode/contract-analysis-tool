"""
Similarity Matcher Module
Compares contract clauses against standard templates
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from difflib import SequenceMatcher
from collections import defaultdict


@dataclass
class SimilarityResult:
    """Result of similarity matching."""
    clause_text: str
    template_clause: str
    similarity_score: float
    match_type: str  # exact, high, medium, low, no_match
    differences: List[str]
    suggestions: List[str]


@dataclass
class TemplateComparisonReport:
    """Complete template comparison report."""
    contract_type: str
    overall_similarity: float
    matched_clauses: List[SimilarityResult]
    missing_clauses: List[str]
    extra_clauses: List[str]
    quality_score: float
    recommendations: List[str]


class SimilarityMatcher:
    """
    Compares contract clauses against standard templates.
    Uses text similarity algorithms and pattern matching.
    """
    
    def __init__(self):
        # Standard clause templates for different contract types
        self.standard_templates = {
            "Employment Agreement": {
                "definitions": {
                    "template": "In this Agreement, unless the context otherwise requires, the following terms shall have the meanings assigned to them: 'Company' means [Company Name]; 'Employee' means [Employee Name]; 'Effective Date' means the date of commencement of employment.",
                    "required": True,
                    "keywords": ["definitions", "means", "shall have the meaning"]
                },
                "position_duties": {
                    "template": "The Employee shall be employed in the position of [Designation] and shall perform such duties as may be assigned by the Company from time to time. The Employee shall report to [Reporting Manager].",
                    "required": True,
                    "keywords": ["position", "duties", "designation", "report to"]
                },
                "compensation": {
                    "template": "The Company shall pay the Employee a gross salary of INR [Amount] per annum, payable in monthly installments. The salary shall be subject to applicable tax deductions.",
                    "required": True,
                    "keywords": ["salary", "compensation", "payment", "per annum", "monthly"]
                },
                "working_hours": {
                    "template": "The normal working hours shall be [X] hours per day, [Y] days per week. The Employee may be required to work additional hours as necessary for the proper performance of duties.",
                    "required": True,
                    "keywords": ["working hours", "hours per day", "days per week"]
                },
                "leave": {
                    "template": "The Employee shall be entitled to [X] days of paid leave per annum, in addition to public holidays as declared by the Company.",
                    "required": True,
                    "keywords": ["leave", "paid leave", "holidays", "vacation"]
                },
                "confidentiality": {
                    "template": "The Employee shall maintain strict confidentiality of all proprietary information, trade secrets, and confidential business information of the Company, both during and after employment.",
                    "required": True,
                    "keywords": ["confidential", "proprietary", "trade secret"]
                },
                "termination": {
                    "template": "Either party may terminate this Agreement by giving [X] days written notice. The Company may terminate immediately for cause including misconduct, breach of duties, or violation of company policies.",
                    "required": True,
                    "keywords": ["terminate", "termination", "notice period"]
                },
                "non_compete": {
                    "template": "For a period of [X] months after termination, the Employee shall not engage in any business that directly competes with the Company within [geographic area].",
                    "required": False,
                    "keywords": ["non-compete", "compete", "restriction"]
                }
            },
            "Service Contract": {
                "definitions": {
                    "template": "In this Agreement: 'Client' means [Client Name]; 'Service Provider' means [Provider Name]; 'Services' means the services described in Schedule A; 'Deliverables' means the work products to be delivered.",
                    "required": True,
                    "keywords": ["definitions", "client", "service provider", "services"]
                },
                "scope_of_services": {
                    "template": "The Service Provider shall provide the Services as described in Schedule A attached hereto. Any changes to the scope shall be agreed in writing by both parties.",
                    "required": True,
                    "keywords": ["scope", "services", "schedule", "deliverables"]
                },
                "payment_terms": {
                    "template": "The Client shall pay the Service Provider [Amount] for the Services. Payment shall be made within [X] days of receipt of invoice. Late payments shall attract interest at [Y]% per annum.",
                    "required": True,
                    "keywords": ["payment", "invoice", "fees", "compensation"]
                },
                "timeline": {
                    "template": "The Services shall be completed within [X] days/months from the Effective Date. Milestones and deadlines are set forth in Schedule B.",
                    "required": True,
                    "keywords": ["timeline", "deadline", "milestone", "completion"]
                },
                "warranties": {
                    "template": "The Service Provider warrants that the Services shall be performed in a professional and workmanlike manner in accordance with industry standards.",
                    "required": True,
                    "keywords": ["warranty", "warrants", "professional", "standards"]
                },
                "intellectual_property": {
                    "template": "All intellectual property created in the course of providing Services shall belong to [Party]. The other party is granted a [license type] license to use such IP.",
                    "required": True,
                    "keywords": ["intellectual property", "ip", "ownership", "license"]
                },
                "limitation_of_liability": {
                    "template": "The total liability of the Service Provider under this Agreement shall not exceed the total fees paid by the Client. Neither party shall be liable for indirect, consequential, or punitive damages.",
                    "required": True,
                    "keywords": ["liability", "limitation", "damages", "cap"]
                },
                "termination": {
                    "template": "Either party may terminate this Agreement with [X] days written notice. Upon termination, the Client shall pay for all Services rendered up to the termination date.",
                    "required": True,
                    "keywords": ["terminate", "termination", "notice"]
                }
            },
            "Non-Disclosure Agreement": {
                "definitions": {
                    "template": "'Confidential Information' means any information disclosed by the Disclosing Party to the Receiving Party, whether orally, in writing, or by inspection, that is designated as confidential or would reasonably be understood to be confidential.",
                    "required": True,
                    "keywords": ["confidential information", "disclosing party", "receiving party"]
                },
                "obligations": {
                    "template": "The Receiving Party shall: (a) maintain the confidentiality of the Confidential Information; (b) not disclose it to any third party without prior written consent; (c) use it only for the Purpose.",
                    "required": True,
                    "keywords": ["maintain", "not disclose", "third party", "purpose"]
                },
                "exclusions": {
                    "template": "Confidential Information does not include information that: (a) is publicly available; (b) was known to the Receiving Party prior to disclosure; (c) is independently developed; (d) is disclosed by a third party without breach.",
                    "required": True,
                    "keywords": ["exclude", "publicly available", "independently developed"]
                },
                "term": {
                    "template": "This Agreement shall remain in effect for [X] years from the Effective Date. The confidentiality obligations shall survive termination for [Y] years.",
                    "required": True,
                    "keywords": ["term", "years", "survive", "termination"]
                },
                "return_of_information": {
                    "template": "Upon termination or request, the Receiving Party shall promptly return or destroy all Confidential Information and certify such destruction in writing.",
                    "required": True,
                    "keywords": ["return", "destroy", "certify"]
                }
            },
            "Lease Agreement": {
                "premises": {
                    "template": "The Lessor hereby leases to the Lessee the premises located at [Address], comprising [description of premises] for the purpose of [permitted use].",
                    "required": True,
                    "keywords": ["premises", "located at", "address", "property"]
                },
                "term": {
                    "template": "The lease shall commence on [Start Date] and continue for a period of [X] months/years, unless terminated earlier in accordance with this Agreement.",
                    "required": True,
                    "keywords": ["term", "commence", "period", "months", "years"]
                },
                "rent": {
                    "template": "The Lessee shall pay a monthly rent of INR [Amount], payable on or before the [X]th day of each month. Rent shall be paid by [payment method].",
                    "required": True,
                    "keywords": ["rent", "monthly", "payable", "payment"]
                },
                "security_deposit": {
                    "template": "The Lessee shall pay a security deposit of INR [Amount] upon execution of this Agreement. The deposit shall be refunded within [X] days of termination, less any deductions for damages.",
                    "required": True,
                    "keywords": ["security deposit", "deposit", "refund"]
                },
                "maintenance": {
                    "template": "The Lessee shall maintain the premises in good condition. The Lessor shall be responsible for structural repairs and major maintenance.",
                    "required": True,
                    "keywords": ["maintenance", "repair", "condition"]
                },
                "termination": {
                    "template": "Either party may terminate this lease by giving [X] months written notice. Early termination by the Lessee may result in forfeiture of the security deposit.",
                    "required": True,
                    "keywords": ["terminate", "termination", "notice", "early termination"]
                }
            }
        }
        
        # Standard clauses that should be in most contracts
        self.universal_clauses = {
            "governing_law": {
                "template": "This Agreement shall be governed by and construed in accordance with the laws of India. The courts of [City] shall have exclusive jurisdiction.",
                "required": True,
                "keywords": ["governing law", "jurisdiction", "courts", "laws of india"]
            },
            "dispute_resolution": {
                "template": "Any dispute arising out of this Agreement shall first be attempted to be resolved through mutual negotiation. If unresolved, the dispute shall be referred to arbitration/mediation.",
                "required": True,
                "keywords": ["dispute", "resolution", "arbitration", "mediation", "negotiation"]
            },
            "entire_agreement": {
                "template": "This Agreement constitutes the entire agreement between the parties and supersedes all prior negotiations, representations, and agreements.",
                "required": True,
                "keywords": ["entire agreement", "supersedes", "prior"]
            },
            "amendment": {
                "template": "This Agreement may only be amended by a written instrument signed by both parties.",
                "required": True,
                "keywords": ["amendment", "modify", "written", "signed"]
            },
            "severability": {
                "template": "If any provision of this Agreement is held invalid or unenforceable, the remaining provisions shall continue in full force and effect.",
                "required": False,
                "keywords": ["severability", "invalid", "unenforceable", "remaining"]
            },
            "notices": {
                "template": "All notices under this Agreement shall be in writing and delivered to the addresses specified herein or such other address as may be notified.",
                "required": True,
                "keywords": ["notice", "notices", "writing", "address"]
            }
        }
    
    def compare_to_template(self, contract_text: str,
                            contract_type: str,
                            clauses: Optional[List[Dict]] = None) -> TemplateComparisonReport:
        """
        Compare contract against standard template.
        
        Args:
            contract_text: Full contract text
            contract_type: Type of contract
            clauses: Optional parsed clauses
            
        Returns:
            TemplateComparisonReport with comparison results
        """
        # Get applicable templates
        type_templates = self.standard_templates.get(contract_type, {})
        all_templates = {**type_templates, **self.universal_clauses}
        
        matched_clauses = []
        missing_clauses = []
        extra_clauses = []
        
        text_lower = contract_text.lower()
        
        # Check each template clause
        for clause_name, template_info in all_templates.items():
            # Find matching section in contract
            match_result = self._find_matching_clause(
                text_lower, 
                template_info['template'],
                template_info['keywords']
            )
            
            if match_result['found']:
                similarity = SimilarityResult(
                    clause_text=match_result['matched_text'],
                    template_clause=template_info['template'],
                    similarity_score=match_result['score'],
                    match_type=self._score_to_match_type(match_result['score']),
                    differences=match_result['differences'],
                    suggestions=self._generate_suggestions(
                        clause_name, 
                        match_result['score'],
                        match_result['differences']
                    )
                )
                matched_clauses.append(similarity)
            else:
                if template_info['required']:
                    missing_clauses.append(clause_name.replace('_', ' ').title())
        
        # Calculate overall similarity
        if matched_clauses:
            overall_similarity = sum(m.similarity_score for m in matched_clauses) / len(matched_clauses)
        else:
            overall_similarity = 0.0
        
        # Calculate quality score
        required_count = sum(1 for t in all_templates.values() if t['required'])
        matched_required = sum(1 for m in matched_clauses 
                              if m.similarity_score > 0.3)
        quality_score = matched_required / required_count if required_count > 0 else 0
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            matched_clauses, missing_clauses, quality_score
        )
        
        return TemplateComparisonReport(
            contract_type=contract_type,
            overall_similarity=round(overall_similarity, 2),
            matched_clauses=matched_clauses,
            missing_clauses=missing_clauses,
            extra_clauses=extra_clauses,
            quality_score=round(quality_score, 2),
            recommendations=recommendations
        )
    
    def _find_matching_clause(self, text: str, 
                               template: str,
                               keywords: List[str]) -> Dict:
        """
        Find a matching clause in the contract text.
        
        Args:
            text: Contract text (lowercase)
            template: Template clause text
            keywords: Keywords to search for
            
        Returns:
            Dictionary with match results
        """
        # First, check if keywords are present
        keyword_matches = sum(1 for kw in keywords if kw.lower() in text)
        keyword_ratio = keyword_matches / len(keywords) if keywords else 0
        
        if keyword_ratio < 0.3:
            return {'found': False, 'score': 0, 'matched_text': '', 'differences': []}
        
        # Find the section containing most keywords
        sentences = re.split(r'[.;]', text)
        best_match = ''
        best_score = 0
        
        # Look for consecutive sentences that match
        for i in range(len(sentences)):
            # Take up to 5 consecutive sentences
            for j in range(i + 1, min(i + 6, len(sentences) + 1)):
                section = '. '.join(sentences[i:j])
                
                # Check keyword presence in this section
                section_keywords = sum(1 for kw in keywords if kw.lower() in section)
                if section_keywords < len(keywords) * 0.3:
                    continue
                
                # Calculate similarity
                score = self._calculate_similarity(section, template.lower())
                
                if score > best_score:
                    best_score = score
                    best_match = section
        
        if best_score > 0.2:
            differences = self._identify_differences(best_match, template.lower())
            return {
                'found': True,
                'score': best_score,
                'matched_text': best_match[:500],
                'differences': differences
            }
        
        return {'found': False, 'score': 0, 'matched_text': '', 'differences': []}
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two texts.
        Uses SequenceMatcher for similarity scoring.
        """
        # Normalize texts
        text1 = re.sub(r'\s+', ' ', text1.strip())
        text2 = re.sub(r'\s+', ' ', text2.strip())
        
        # Use SequenceMatcher
        matcher = SequenceMatcher(None, text1, text2)
        return matcher.ratio()
    
    def _identify_differences(self, actual: str, template: str) -> List[str]:
        """
        Identify key differences between actual and template.
        """
        differences = []
        
        # Check for missing key elements
        template_words = set(template.split())
        actual_words = set(actual.split())
        
        # Important legal terms that might be missing
        important_terms = ['shall', 'must', 'may', 'written', 'notice', 'days', 
                          'liability', 'indemnify', 'terminate', 'confidential']
        
        for term in important_terms:
            if term in template_words and term not in actual_words:
                differences.append(f"Missing term: '{term}'")
        
        # Check for concerning additions
        concerning_terms = ['unlimited', 'perpetual', 'irrevocable', 'sole discretion']
        for term in concerning_terms:
            if term in actual and term not in template:
                differences.append(f"Added concerning term: '{term}'")
        
        return differences[:5]
    
    def _score_to_match_type(self, score: float) -> str:
        """Convert similarity score to match type."""
        if score >= 0.8:
            return "exact"
        elif score >= 0.6:
            return "high"
        elif score >= 0.4:
            return "medium"
        elif score >= 0.2:
            return "low"
        else:
            return "no_match"
    
    def _generate_suggestions(self, clause_name: str,
                               score: float,
                               differences: List[str]) -> List[str]:
        """Generate suggestions for improving clause."""
        suggestions = []
        
        if score < 0.4:
            suggestions.append(f"Consider revising {clause_name} to align with standard practices")
        
        if score < 0.6:
            suggestions.append("Review clause for completeness")
        
        for diff in differences:
            if "Missing term" in diff:
                term = diff.split("'")[1]
                suggestions.append(f"Consider adding '{term}' for clarity")
            elif "concerning term" in diff:
                term = diff.split("'")[1]
                suggestions.append(f"Review use of '{term}' - may be unfavorable")
        
        return suggestions
    
    def _generate_recommendations(self, matched: List[SimilarityResult],
                                    missing: List[str],
                                    quality_score: float) -> List[str]:
        """Generate overall recommendations."""
        recommendations = []
        
        if quality_score >= 0.8:
            recommendations.append("✅ Contract structure aligns well with standard templates")
        elif quality_score >= 0.6:
            recommendations.append("⚡ Contract has most standard clauses but needs some additions")
        else:
            recommendations.append("⚠️ Contract is missing several standard clauses")
        
        if missing:
            recommendations.append(f"Add missing clauses: {', '.join(missing[:5])}")
        
        # Check for low-similarity matches
        low_matches = [m for m in matched if m.similarity_score < 0.4]
        if low_matches:
            recommendations.append(f"Review and strengthen {len(low_matches)} clauses that deviate from standards")
        
        return recommendations
    
    def get_template_for_type(self, contract_type: str) -> Dict:
        """
        Get the standard template for a contract type.
        
        Args:
            contract_type: Type of contract
            
        Returns:
            Dictionary with template clauses
        """
        type_templates = self.standard_templates.get(contract_type, {})
        return {**type_templates, **self.universal_clauses}
    
    def get_clause_template(self, contract_type: str, clause_name: str) -> Optional[str]:
        """
        Get template for a specific clause.
        
        Args:
            contract_type: Type of contract
            clause_name: Name of clause
            
        Returns:
            Template text or None
        """
        templates = self.get_template_for_type(contract_type)
        clause_info = templates.get(clause_name.lower().replace(' ', '_'))
        return clause_info['template'] if clause_info else None

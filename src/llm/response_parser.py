"""
Response Parser Module
Parses and structures GPT responses for contract analysis
"""

import json
import re
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field


@dataclass
class ParsedRiskAssessment:
    """Structured risk assessment data."""
    risk_level: str
    risk_score: float
    risk_factors: List[str]
    potential_impact: str
    red_flags: List[str]
    mitigation_suggestions: List[str]
    negotiation_points: List[str]
    explanation: str


@dataclass
class ParsedClauseAnalysis:
    """Structured clause analysis data."""
    clause_id: str
    clause_type: str
    risk_assessment: Optional[ParsedRiskAssessment]
    explanation: str
    key_points: List[str]
    concerns: List[str]


@dataclass
class ParsedContractClassification:
    """Structured contract classification data."""
    contract_type: str
    confidence: float
    purpose: str
    parties: List[str]
    jurisdiction: str
    subject_matter: str
    reasoning: str


@dataclass
class ParsedUnfavorableTerm:
    """Structured unfavorable term data."""
    clause_text: str
    issue: str
    severity: str
    suggested_alternative: str
    explanation: str


@dataclass
class ParsedComplianceIssue:
    """Structured compliance issue data."""
    clause: str
    law: str
    issue: str
    severity: str
    recommendation: str
    risk: str


@dataclass
class ParsedAmbiguity:
    """Structured ambiguity data."""
    text: str
    ambiguity_type: str
    issue: str
    suggestion: str
    risk_level: str


class ResponseParser:
    """
    Parser for GPT responses in contract analysis.
    Handles JSON parsing, validation, and structuring of responses.
    """
    
    def __init__(self):
        self.default_risk_score = 0.5
        self.default_confidence = 0.7
    
    def parse_json_response(self, response_text: str) -> Optional[Dict]:
        """
        Parse JSON from GPT response text.
        
        Args:
            response_text: Raw response text from GPT
            
        Returns:
            Parsed JSON dictionary or None
        """
        if not response_text:
            return None
        
        # Try direct parsing first
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            pass
        
        # Try to extract JSON from markdown code blocks
        patterns = [
            r'```json\s*([\s\S]*?)\s*```',
            r'```\s*([\s\S]*?)\s*```',
            r'\{[\s\S]*\}'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response_text)
            if match:
                try:
                    json_str = match.group(1) if '```' in pattern else match.group(0)
                    return json.loads(json_str.strip())
                except json.JSONDecodeError:
                    continue
        
        return None
    
    def parse_classification(self, response: Union[str, Dict]) -> ParsedContractClassification:
        """
        Parse contract classification response.
        
        Args:
            response: GPT response (string or dict)
            
        Returns:
            ParsedContractClassification object
        """
        if isinstance(response, str):
            data = self.parse_json_response(response) or {}
        else:
            data = response or {}
        
        return ParsedContractClassification(
            contract_type=data.get('contract_type', 'Unknown'),
            confidence=float(data.get('confidence', self.default_confidence)),
            purpose=data.get('purpose', ''),
            parties=data.get('parties', []),
            jurisdiction=data.get('jurisdiction', ''),
            subject_matter=data.get('subject_matter', ''),
            reasoning=data.get('reasoning', '')
        )
    
    def parse_risk_assessment(self, response: Union[str, Dict]) -> ParsedRiskAssessment:
        """
        Parse risk assessment response.
        
        Args:
            response: GPT response (string or dict)
            
        Returns:
            ParsedRiskAssessment object
        """
        if isinstance(response, str):
            data = self.parse_json_response(response) or {}
        else:
            data = response or {}
        
        # Normalize risk level
        risk_level = data.get('risk_level', 'MEDIUM').upper()
        if risk_level not in ['LOW', 'MEDIUM', 'HIGH']:
            risk_level = 'MEDIUM'
        
        # Normalize risk score
        risk_score = float(data.get('risk_score', self.default_risk_score))
        risk_score = max(0.0, min(1.0, risk_score))
        
        return ParsedRiskAssessment(
            risk_level=risk_level,
            risk_score=risk_score,
            risk_factors=data.get('risk_factors', []),
            potential_impact=data.get('potential_impact', ''),
            red_flags=data.get('red_flags', []),
            mitigation_suggestions=data.get('mitigation_suggestions', []),
            negotiation_points=data.get('negotiation_points', []),
            explanation=data.get('explanation', '')
        )
    
    def parse_unfavorable_terms(self, response: Union[str, Dict]) -> Dict:
        """
        Parse unfavorable terms detection response.
        
        Args:
            response: GPT response (string or dict)
            
        Returns:
            Dictionary with parsed unfavorable terms
        """
        if isinstance(response, str):
            data = self.parse_json_response(response) or {}
        else:
            data = response or {}
        
        unfavorable_terms = []
        for term in data.get('unfavorable_terms', []):
            unfavorable_terms.append(ParsedUnfavorableTerm(
                clause_text=term.get('clause_text', ''),
                issue=term.get('issue', ''),
                severity=term.get('severity', 'Moderate'),
                suggested_alternative=term.get('suggested_alternative', ''),
                explanation=term.get('explanation', '')
            ))
        
        return {
            'unfavorable_terms': unfavorable_terms,
            'one_sided_provisions': data.get('one_sided_provisions', []),
            'hidden_risks': data.get('hidden_risks', []),
            'missing_protections': data.get('missing_protections', []),
            'unusual_clauses': data.get('unusual_clauses', []),
            'compliance_concerns': data.get('compliance_concerns', []),
            'overall_assessment': data.get('overall_assessment', ''),
            'priority_issues': data.get('priority_issues', [])
        }
    
    def parse_compliance_check(self, response: Union[str, Dict]) -> Dict:
        """
        Parse compliance check response.
        
        Args:
            response: GPT response (string or dict)
            
        Returns:
            Dictionary with parsed compliance results
        """
        if isinstance(response, str):
            data = self.parse_json_response(response) or {}
        else:
            data = response or {}
        
        issues = []
        for issue in data.get('issues', []):
            issues.append(ParsedComplianceIssue(
                clause=issue.get('clause', ''),
                law=issue.get('law', ''),
                issue=issue.get('issue', ''),
                severity=issue.get('severity', 'Medium'),
                recommendation=issue.get('recommendation', ''),
                risk=issue.get('risk', '')
            ))
        
        return {
            'compliance_status': data.get('compliance_status', 'Unknown'),
            'issues': issues,
            'missing_requirements': data.get('missing_requirements', []),
            'recommendations': data.get('recommendations', []),
            'overall_assessment': data.get('overall_assessment', '')
        }
    
    def parse_ambiguities(self, response: Union[str, Dict]) -> Dict:
        """
        Parse ambiguity detection response.
        
        Args:
            response: GPT response (string or dict)
            
        Returns:
            Dictionary with parsed ambiguities
        """
        if isinstance(response, str):
            data = self.parse_json_response(response) or {}
        else:
            data = response or {}
        
        ambiguities = []
        for amb in data.get('ambiguities', []):
            ambiguities.append(ParsedAmbiguity(
                text=amb.get('text', ''),
                ambiguity_type=amb.get('type', 'unknown'),
                issue=amb.get('issue', ''),
                suggestion=amb.get('suggestion', ''),
                risk_level=amb.get('risk_level', 'Medium')
            ))
        
        return {
            'ambiguities': ambiguities,
            'total_issues': data.get('total_issues', len(ambiguities)),
            'high_priority_issues': data.get('high_priority_issues', []),
            'recommendations': data.get('recommendations', [])
        }
    
    def parse_obligations(self, response: Union[str, Dict]) -> Dict:
        """
        Parse obligations extraction response.
        
        Args:
            response: GPT response (string or dict)
            
        Returns:
            Dictionary with parsed obligations
        """
        if isinstance(response, str):
            data = self.parse_json_response(response) or {}
        else:
            data = response or {}
        
        return {
            'party_1': data.get('party_1', {}),
            'party_2': data.get('party_2', {}),
            'mutual_obligations': data.get('mutual_obligations', []),
            'mutual_rights': data.get('mutual_rights', []),
            'mutual_prohibitions': data.get('mutual_prohibitions', [])
        }
    
    def parse_template_comparison(self, response: Union[str, Dict]) -> Dict:
        """
        Parse template comparison response.
        
        Args:
            response: GPT response (string or dict)
            
        Returns:
            Dictionary with parsed comparison results
        """
        if isinstance(response, str):
            data = self.parse_json_response(response) or {}
        else:
            data = response or {}
        
        return {
            'present_clauses': data.get('present_clauses', []),
            'missing_clauses': data.get('missing_clauses', []),
            'non_standard_clauses': data.get('non_standard_clauses', []),
            'deviations': data.get('deviations', []),
            'quality_score': float(data.get('quality_score', 0.5)),
            'overall_assessment': data.get('overall_assessment', '')
        }
    
    def extract_key_points(self, text: str) -> List[str]:
        """
        Extract key points from unstructured text.
        
        Args:
            text: Text to extract points from
            
        Returns:
            List of key points
        """
        points = []
        
        # Look for bullet points
        bullet_patterns = [
            r'[-•*]\s*(.+?)(?=\n[-•*]|\n\n|$)',
            r'\d+\.\s*(.+?)(?=\n\d+\.|\n\n|$)',
            r'[a-z]\)\s*(.+?)(?=\n[a-z]\)|\n\n|$)'
        ]
        
        for pattern in bullet_patterns:
            matches = re.findall(pattern, text, re.MULTILINE)
            points.extend([m.strip() for m in matches if m.strip()])
        
        # If no bullets found, split by sentences
        if not points:
            sentences = re.split(r'[.!?]+', text)
            points = [s.strip() for s in sentences if len(s.strip()) > 20][:10]
        
        return points
    
    def extract_sections(self, text: str) -> Dict[str, str]:
        """
        Extract sections from markdown-formatted text.
        
        Args:
            text: Markdown text
            
        Returns:
            Dictionary of section headers to content
        """
        sections = {}
        current_section = 'introduction'
        current_content = []
        
        for line in text.split('\n'):
            # Check for headers
            header_match = re.match(r'^#{1,3}\s+(.+)$', line)
            if header_match:
                # Save previous section
                if current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                
                current_section = header_match.group(1).strip().lower()
                current_section = re.sub(r'[^\w\s]', '', current_section)
                current_section = current_section.replace(' ', '_')
                current_content = []
            else:
                current_content.append(line)
        
        # Save last section
        if current_content:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections
    
    def calculate_overall_risk(self, clause_risks: List[ParsedRiskAssessment]) -> Dict:
        """
        Calculate overall contract risk from clause-level risks.
        
        Args:
            clause_risks: List of clause risk assessments
            
        Returns:
            Dictionary with overall risk metrics
        """
        if not clause_risks:
            return {
                'overall_score': 0.5,
                'overall_level': 'MEDIUM',
                'high_risk_count': 0,
                'medium_risk_count': 0,
                'low_risk_count': 0
            }
        
        # Count by level
        high_count = sum(1 for r in clause_risks if r.risk_level == 'HIGH')
        medium_count = sum(1 for r in clause_risks if r.risk_level == 'MEDIUM')
        low_count = sum(1 for r in clause_risks if r.risk_level == 'LOW')
        
        # Calculate weighted average
        total = len(clause_risks)
        weighted_score = (high_count * 0.9 + medium_count * 0.5 + low_count * 0.2) / total
        
        # Determine overall level
        if weighted_score >= 0.66 or high_count >= 3:
            overall_level = 'HIGH'
        elif weighted_score >= 0.33 or high_count >= 1:
            overall_level = 'MEDIUM'
        else:
            overall_level = 'LOW'
        
        return {
            'overall_score': round(weighted_score, 2),
            'overall_level': overall_level,
            'high_risk_count': high_count,
            'medium_risk_count': medium_count,
            'low_risk_count': low_count,
            'total_clauses_analyzed': total
        }
    
    def format_for_display(self, data: Any, format_type: str = 'markdown') -> str:
        """
        Format parsed data for display.
        
        Args:
            data: Data to format
            format_type: Output format ('markdown', 'plain', 'html')
            
        Returns:
            Formatted string
        """
        if format_type == 'markdown':
            return self._format_markdown(data)
        elif format_type == 'plain':
            return self._format_plain(data)
        elif format_type == 'html':
            return self._format_html(data)
        else:
            return str(data)
    
    def _format_markdown(self, data: Any) -> str:
        """Format data as markdown."""
        if isinstance(data, ParsedRiskAssessment):
            return f"""### Risk Assessment

**Risk Level:** {data.risk_level}
**Risk Score:** {data.risk_score:.2f}

#### Risk Factors
{self._list_to_md(data.risk_factors)}

#### Potential Impact
{data.potential_impact}

#### Red Flags
{self._list_to_md(data.red_flags)}

#### Mitigation Suggestions
{self._list_to_md(data.mitigation_suggestions)}

#### Negotiation Points
{self._list_to_md(data.negotiation_points)}
"""
        elif isinstance(data, ParsedContractClassification):
            return f"""### Contract Classification

**Type:** {data.contract_type}
**Confidence:** {data.confidence:.0%}

**Purpose:** {data.purpose}

**Parties:**
{self._list_to_md(data.parties)}

**Jurisdiction:** {data.jurisdiction}

**Subject Matter:** {data.subject_matter}

**Reasoning:** {data.reasoning}
"""
        elif isinstance(data, dict):
            return json.dumps(data, indent=2)
        else:
            return str(data)
    
    def _format_plain(self, data: Any) -> str:
        """Format data as plain text."""
        if isinstance(data, (ParsedRiskAssessment, ParsedContractClassification)):
            return str(data)
        elif isinstance(data, dict):
            return json.dumps(data, indent=2)
        else:
            return str(data)
    
    def _format_html(self, data: Any) -> str:
        """Format data as HTML."""
        md = self._format_markdown(data)
        # Basic markdown to HTML conversion
        html = md.replace('### ', '<h3>').replace('\n\n', '</p><p>')
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'- (.+)', r'<li>\1</li>', html)
        return f'<div class="analysis-result">{html}</div>'
    
    def _list_to_md(self, items: List[str]) -> str:
        """Convert list to markdown bullet points."""
        if not items:
            return "_None identified_"
        return '\n'.join(f'- {item}' for item in items)

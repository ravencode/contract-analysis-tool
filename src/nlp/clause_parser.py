"""
Clause Parser Module
Extracts and categorizes clauses from legal contracts
"""

import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum


class ClauseType(Enum):
    """Enumeration of clause types in legal contracts."""
    DEFINITIONS = "definitions"
    SCOPE = "scope_of_work"
    PAYMENT = "payment_terms"
    DELIVERY = "delivery_performance"
    WARRANTY = "warranties_representations"
    INDEMNITY = "indemnification"
    LIABILITY = "limitation_of_liability"
    CONFIDENTIALITY = "confidentiality"
    IP_RIGHTS = "intellectual_property"
    TERM = "term_duration"
    TERMINATION = "termination"
    DISPUTE = "dispute_resolution"
    FORCE_MAJEURE = "force_majeure"
    ASSIGNMENT = "assignment"
    NOTICES = "notices"
    GOVERNING_LAW = "governing_law"
    ENTIRE_AGREEMENT = "entire_agreement"
    AMENDMENT = "amendment"
    SEVERABILITY = "severability"
    WAIVER = "waiver"
    NON_COMPETE = "non_compete"
    NON_SOLICITATION = "non_solicitation"
    PENALTY = "penalty"
    INSURANCE = "insurance"
    COMPLIANCE = "compliance"
    AUDIT = "audit_rights"
    DATA_PROTECTION = "data_protection"
    MISCELLANEOUS = "miscellaneous"
    UNKNOWN = "unknown"


@dataclass
class Clause:
    """Data class representing a contract clause."""
    clause_id: str
    clause_type: ClauseType
    title: str
    content: str
    level: int  # Hierarchy level (1 = main clause, 2 = sub-clause, etc.)
    parent_id: Optional[str] = None
    start_position: int = 0
    end_position: int = 0
    sub_clauses: List['Clause'] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)


class ClauseParser:
    """
    Advanced clause extraction and parsing for legal contracts.
    Identifies clause boundaries, types, and hierarchical structure.
    """
    
    def __init__(self):
        # Clause type detection patterns
        self.clause_patterns = {
            ClauseType.DEFINITIONS: [
                r'definition', r'interpret', r'meaning', r'glossary'
            ],
            ClauseType.SCOPE: [
                r'scope\s+of\s+work', r'scope\s+of\s+services', r'services',
                r'deliverables', r'work\s+order', r'statement\s+of\s+work'
            ],
            ClauseType.PAYMENT: [
                r'payment', r'compensation', r'fee', r'price', r'consideration',
                r'invoice', r'billing', r'remuneration'
            ],
            ClauseType.DELIVERY: [
                r'delivery', r'performance', r'milestone', r'timeline',
                r'schedule', r'completion'
            ],
            ClauseType.WARRANTY: [
                r'warrant', r'representation', r'guarantee', r'assurance'
            ],
            ClauseType.INDEMNITY: [
                r'indemnif', r'hold\s+harmless', r'defend'
            ],
            ClauseType.LIABILITY: [
                r'limitation\s+of\s+liability', r'liability\s+cap', r'liability\s+limit',
                r'exclusion\s+of\s+liability', r'cap\s+on\s+liability'
            ],
            ClauseType.CONFIDENTIALITY: [
                r'confidential', r'non-disclosure', r'nda', r'proprietary',
                r'trade\s+secret', r'sensitive\s+information'
            ],
            ClauseType.IP_RIGHTS: [
                r'intellectual\s+property', r'ip\s+rights', r'copyright',
                r'patent', r'trademark', r'ownership\s+of\s+work'
            ],
            ClauseType.TERM: [
                r'^term$', r'duration', r'period\s+of\s+agreement', r'validity'
            ],
            ClauseType.TERMINATION: [
                r'terminat', r'cancel', r'end\s+of\s+agreement', r'expir'
            ],
            ClauseType.DISPUTE: [
                r'dispute', r'arbitrat', r'mediat', r'resolution', r'settlement'
            ],
            ClauseType.FORCE_MAJEURE: [
                r'force\s+majeure', r'act\s+of\s+god', r'unforeseeable', r'beyond\s+control'
            ],
            ClauseType.ASSIGNMENT: [
                r'assignment', r'transfer\s+of\s+rights', r'subcontract'
            ],
            ClauseType.NOTICES: [
                r'notice', r'communication', r'notification'
            ],
            ClauseType.GOVERNING_LAW: [
                r'governing\s+law', r'applicable\s+law', r'jurisdiction',
                r'choice\s+of\s+law', r'legal\s+framework'
            ],
            ClauseType.ENTIRE_AGREEMENT: [
                r'entire\s+agreement', r'whole\s+agreement', r'complete\s+agreement',
                r'integration', r'merger'
            ],
            ClauseType.AMENDMENT: [
                r'amendment', r'modification', r'variation', r'change'
            ],
            ClauseType.SEVERABILITY: [
                r'severab', r'invalid', r'unenforceable'
            ],
            ClauseType.WAIVER: [
                r'waiver', r'forbearance', r'no\s+waiver'
            ],
            ClauseType.NON_COMPETE: [
                r'non-compete', r'non\s+compete', r'competition', r'restrictive\s+covenant'
            ],
            ClauseType.NON_SOLICITATION: [
                r'non-solicitation', r'non\s+solicitation', r'no\s+poaching'
            ],
            ClauseType.PENALTY: [
                r'penalty', r'liquidated\s+damages', r'fine', r'forfeit'
            ],
            ClauseType.INSURANCE: [
                r'insurance', r'coverage', r'policy'
            ],
            ClauseType.COMPLIANCE: [
                r'compliance', r'regulatory', r'legal\s+requirement'
            ],
            ClauseType.AUDIT: [
                r'audit', r'inspection', r'review\s+rights', r'access\s+to\s+records'
            ],
            ClauseType.DATA_PROTECTION: [
                r'data\s+protection', r'privacy', r'personal\s+data', r'gdpr', r'dpdp'
            ]
        }
        
        # Section header patterns
        self.header_patterns = [
            # Numbered patterns
            (r'^(\d+)\.\s+([A-Z][A-Z\s]+)$', 1),                    # 1. DEFINITIONS
            (r'^(\d+)\.\s+([A-Z][a-zA-Z\s]+)$', 1),                 # 1. Definitions
            (r'^(\d+\.\d+)\s+(.+)$', 2),                            # 1.1 Sub-clause
            (r'^(\d+\.\d+\.\d+)\s+(.+)$', 3),                       # 1.1.1 Sub-sub-clause
            (r'^ARTICLE\s+(\d+)[:\s]+(.+)$', 1),                    # ARTICLE 1: Title
            (r'^SECTION\s+(\d+)[:\s]+(.+)$', 1),                    # SECTION 1: Title
            (r'^CLAUSE\s+(\d+)[:\s]+(.+)$', 1),                     # CLAUSE 1: Title
            # Lettered patterns
            (r'^\(([a-z])\)\s+(.+)$', 2),                           # (a) Sub-clause
            (r'^([a-z])\)\s+(.+)$', 2),                             # a) Sub-clause
            (r'^\(([ivxlcdm]+)\)\s+(.+)$', 3),                      # (i) Sub-sub-clause
            # All caps headers
            (r'^([A-Z][A-Z\s]{3,})$', 1),                           # ALL CAPS HEADER
            # Schedule/Annexure patterns
            (r'^SCHEDULE\s+([A-Z\d]+)[:\s]*(.*)$', 1),              # SCHEDULE A
            (r'^ANNEXURE\s+([A-Z\d]+)[:\s]*(.*)$', 1),              # ANNEXURE 1
            (r'^EXHIBIT\s+([A-Z\d]+)[:\s]*(.*)$', 1),               # EXHIBIT A
        ]
    
    def parse_clauses(self, text: str) -> List[Clause]:
        """
        Parse contract text into structured clauses.
        
        Args:
            text: Contract text to parse
            
        Returns:
            List of Clause objects with hierarchical structure
        """
        lines = text.split('\n')
        clauses = []
        current_clause = None
        current_content = []
        clause_counter = 0
        
        for line_num, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Check if this line is a header
            header_match = self._match_header(line)
            
            if header_match:
                # Save previous clause
                if current_clause:
                    current_clause.content = ' '.join(current_content).strip()
                    current_clause.end_position = line_num - 1
                    clauses.append(current_clause)
                
                # Start new clause
                clause_counter += 1
                clause_id, title, level = header_match
                clause_type = self._detect_clause_type(title + ' ' + line)
                
                current_clause = Clause(
                    clause_id=f"clause_{clause_counter}",
                    clause_type=clause_type,
                    title=title,
                    content='',
                    level=level,
                    start_position=line_num
                )
                current_content = []
            else:
                current_content.append(line)
        
        # Save last clause
        if current_clause:
            current_clause.content = ' '.join(current_content).strip()
            current_clause.end_position = len(lines) - 1
            clauses.append(current_clause)
        
        # Build hierarchy
        clauses = self._build_hierarchy(clauses)
        
        return clauses
    
    def _match_header(self, line: str) -> Optional[Tuple[str, str, int]]:
        """
        Check if a line matches a header pattern.
        
        Returns:
            Tuple of (clause_id, title, level) or None
        """
        for pattern, level in self.header_patterns:
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                groups = match.groups()
                if len(groups) >= 2:
                    return (groups[0], groups[1].strip(), level)
                elif len(groups) == 1:
                    return (groups[0], groups[0].strip(), level)
        
        return None
    
    def _detect_clause_type(self, text: str) -> ClauseType:
        """
        Detect the type of clause based on its content.
        """
        text_lower = text.lower()
        
        for clause_type, patterns in self.clause_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return clause_type
        
        return ClauseType.UNKNOWN
    
    def _build_hierarchy(self, clauses: List[Clause]) -> List[Clause]:
        """
        Build parent-child relationships between clauses.
        """
        if not clauses:
            return clauses
        
        # Stack to track parent clauses at each level
        parent_stack = {}
        
        for clause in clauses:
            level = clause.level
            
            # Find parent
            for parent_level in range(level - 1, 0, -1):
                if parent_level in parent_stack:
                    clause.parent_id = parent_stack[parent_level].clause_id
                    parent_stack[parent_level].sub_clauses.append(clause)
                    break
            
            # Update stack
            parent_stack[level] = clause
            
            # Clear lower levels
            for l in list(parent_stack.keys()):
                if l > level:
                    del parent_stack[l]
        
        # Return only top-level clauses
        return [c for c in clauses if c.parent_id is None]
    
    def extract_clause_by_type(self, clauses: List[Clause], 
                                clause_type: ClauseType) -> List[Clause]:
        """
        Extract all clauses of a specific type.
        """
        result = []
        
        def search_recursive(clause_list):
            for clause in clause_list:
                if clause.clause_type == clause_type:
                    result.append(clause)
                search_recursive(clause.sub_clauses)
        
        search_recursive(clauses)
        return result
    
    def get_clause_text(self, clause: Clause, include_subclauses: bool = True) -> str:
        """
        Get the full text of a clause including sub-clauses.
        """
        text = f"{clause.title}\n{clause.content}"
        
        if include_subclauses:
            for sub in clause.sub_clauses:
                text += f"\n{self.get_clause_text(sub, True)}"
        
        return text
    
    def analyze_clause_structure(self, clauses: List[Clause]) -> Dict:
        """
        Analyze the structure of parsed clauses.
        """
        def count_recursive(clause_list, depth=1):
            counts = {'total': 0, 'by_type': {}, 'by_level': {}, 'max_depth': depth}
            
            for clause in clause_list:
                counts['total'] += 1
                
                # Count by type
                type_name = clause.clause_type.value
                counts['by_type'][type_name] = counts['by_type'].get(type_name, 0) + 1
                
                # Count by level
                counts['by_level'][clause.level] = counts['by_level'].get(clause.level, 0) + 1
                
                # Recurse into sub-clauses
                if clause.sub_clauses:
                    sub_counts = count_recursive(clause.sub_clauses, depth + 1)
                    counts['total'] += sub_counts['total']
                    counts['max_depth'] = max(counts['max_depth'], sub_counts['max_depth'])
                    
                    for t, c in sub_counts['by_type'].items():
                        counts['by_type'][t] = counts['by_type'].get(t, 0) + c
                    for l, c in sub_counts['by_level'].items():
                        counts['by_level'][l] = counts['by_level'].get(l, 0) + c
            
            return counts
        
        analysis = count_recursive(clauses)
        analysis['top_level_clauses'] = len(clauses)
        
        # Identify missing standard clauses
        standard_clauses = [
            ClauseType.DEFINITIONS, ClauseType.SCOPE, ClauseType.PAYMENT,
            ClauseType.TERM, ClauseType.TERMINATION, ClauseType.CONFIDENTIALITY,
            ClauseType.LIABILITY, ClauseType.DISPUTE, ClauseType.GOVERNING_LAW
        ]
        
        analysis['missing_standard_clauses'] = [
            ct.value for ct in standard_clauses 
            if ct.value not in analysis['by_type']
        ]
        
        return analysis
    
    def find_related_clauses(self, clauses: List[Clause], 
                             keywords: List[str]) -> List[Clause]:
        """
        Find clauses related to specific keywords.
        """
        related = []
        
        def search_recursive(clause_list):
            for clause in clause_list:
                text = (clause.title + ' ' + clause.content).lower()
                if any(kw.lower() in text for kw in keywords):
                    related.append(clause)
                search_recursive(clause.sub_clauses)
        
        search_recursive(clauses)
        return related
    
    def extract_definitions_section(self, text: str) -> Dict[str, str]:
        """
        Extract defined terms from the definitions section.
        """
        definitions = {}
        
        # Pattern 1: "Term" means/shall mean...
        pattern1 = r'"([^"]+)"\s+(?:means|shall\s+mean|refers\s+to)\s+([^.]+\.)'
        matches1 = re.findall(pattern1, text, re.IGNORECASE)
        for term, definition in matches1:
            definitions[term.strip()] = definition.strip()
        
        # Pattern 2: (a) "Term" means...
        pattern2 = r'\([a-z]\)\s+"([^"]+)"\s+(?:means|shall\s+mean)\s+([^.]+\.)'
        matches2 = re.findall(pattern2, text, re.IGNORECASE)
        for term, definition in matches2:
            definitions[term.strip()] = definition.strip()
        
        # Pattern 3: Term: definition
        pattern3 = r'([A-Z][a-zA-Z\s]+):\s+(?:means\s+)?([^.;]+[.;])'
        matches3 = re.findall(pattern3, text)
        for term, definition in matches3:
            if len(term.strip()) < 50:  # Avoid false positives
                definitions[term.strip()] = definition.strip()
        
        return definitions
    
    def get_clause_summary(self, clauses: List[Clause]) -> List[Dict]:
        """
        Generate a summary of all clauses.
        """
        summary = []
        
        def summarize_recursive(clause_list, indent=0):
            for clause in clause_list:
                summary.append({
                    'id': clause.clause_id,
                    'title': clause.title,
                    'type': clause.clause_type.value,
                    'level': clause.level,
                    'indent': indent,
                    'content_preview': clause.content[:200] + '...' if len(clause.content) > 200 else clause.content,
                    'has_subclauses': len(clause.sub_clauses) > 0,
                    'subclause_count': len(clause.sub_clauses)
                })
                summarize_recursive(clause.sub_clauses, indent + 1)
        
        summarize_recursive(clauses)
        return summary
    
    def detect_ambiguous_clauses(self, clauses: List[Clause]) -> List[Dict]:
        """
        Detect potentially ambiguous clauses.
        """
        ambiguous = []
        
        # Ambiguity indicators
        ambiguity_patterns = [
            (r'\b(reasonable|reasonably)\b', 'Subjective standard: "reasonable"'),
            (r'\b(material|materially)\b', 'Undefined materiality threshold'),
            (r'\b(substantial|substantially)\b', 'Vague quantifier'),
            (r'\b(promptly|timely)\b', 'Undefined time frame'),
            (r'\b(best\s+efforts?|reasonable\s+efforts?)\b', 'Effort standard unclear'),
            (r'\b(as\s+needed|as\s+required|as\s+appropriate)\b', 'Discretionary language'),
            (r'\b(including\s+but\s+not\s+limited\s+to)\b', 'Open-ended list'),
            (r'\b(may\s+be\s+amended|subject\s+to\s+change)\b', 'Unilateral modification'),
            (r'\b(sole\s+discretion|absolute\s+discretion)\b', 'Discretionary power'),
            (r'\b(and/or)\b', 'Ambiguous conjunction'),
        ]
        
        def check_recursive(clause_list):
            for clause in clause_list:
                text = clause.content.lower()
                issues = []
                
                for pattern, description in ambiguity_patterns:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    if matches:
                        issues.append({
                            'pattern': pattern,
                            'description': description,
                            'occurrences': len(matches)
                        })
                
                if issues:
                    ambiguous.append({
                        'clause_id': clause.clause_id,
                        'title': clause.title,
                        'type': clause.clause_type.value,
                        'issues': issues,
                        'total_issues': sum(i['occurrences'] for i in issues)
                    })
                
                check_recursive(clause.sub_clauses)
        
        check_recursive(clauses)
        return sorted(ambiguous, key=lambda x: x['total_issues'], reverse=True)

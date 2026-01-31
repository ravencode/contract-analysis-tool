"""
Legal Entity Extraction Module
Named Entity Recognition for Contract Documents
"""

import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import spacy
from dateutil import parser as date_parser


@dataclass
class LegalEntity:
    """Data class representing an extracted legal entity."""
    entity_type: str
    value: str
    start_pos: int
    end_pos: int
    confidence: float
    context: str = ""
    normalized_value: Optional[str] = None


class LegalEntityExtractor:
    """
    Advanced Named Entity Recognition for legal contracts.
    Extracts parties, dates, amounts, jurisdictions, and other legal entities.
    """
    
    def __init__(self):
        # Load spaCy model
        try:
            self.nlp = spacy.load("en_core_web_lg")
        except OSError:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                # Fallback - will use regex-based extraction
                self.nlp = None
        
        # Indian states and union territories for jurisdiction detection
        self.indian_jurisdictions = {
            'andhra pradesh', 'arunachal pradesh', 'assam', 'bihar', 'chhattisgarh',
            'goa', 'gujarat', 'haryana', 'himachal pradesh', 'jharkhand', 'karnataka',
            'kerala', 'madhya pradesh', 'maharashtra', 'manipur', 'meghalaya', 'mizoram',
            'nagaland', 'odisha', 'punjab', 'rajasthan', 'sikkim', 'tamil nadu',
            'telangana', 'tripura', 'uttar pradesh', 'uttarakhand', 'west bengal',
            'delhi', 'new delhi', 'mumbai', 'bangalore', 'bengaluru', 'chennai',
            'hyderabad', 'kolkata', 'pune', 'ahmedabad', 'jaipur', 'lucknow'
        }
        
        # Common party type indicators
        self.party_indicators = [
            r'private\s+limited', r'pvt\.?\s*ltd\.?', r'limited', r'ltd\.?',
            r'llp', r'llc', r'inc\.?', r'incorporated', r'corporation', r'corp\.?',
            r'partnership', r'proprietorship', r'sole\s+proprietor',
            r'company', r'co\.?', r'enterprises?', r'industries', r'solutions',
            r'technologies', r'services', r'consultants?', r'associates?'
        ]
        
        # Currency patterns
        self.currency_patterns = [
            (r'(?:INR|Rs\.?|₹)\s*([\d,]+(?:\.\d{2})?)', 'INR'),
            (r'(?:USD|\$)\s*([\d,]+(?:\.\d{2})?)', 'USD'),
            (r'(?:EUR|€)\s*([\d,]+(?:\.\d{2})?)', 'EUR'),
            (r'(?:GBP|£)\s*([\d,]+(?:\.\d{2})?)', 'GBP'),
            (r'([\d,]+(?:\.\d{2})?)\s*(?:lakhs?|lacs?)', 'INR_LAKH'),
            (r'([\d,]+(?:\.\d{2})?)\s*(?:crores?)', 'INR_CRORE')
        ]
        
        # Duration patterns
        self.duration_patterns = [
            r'(\d+)\s*(?:years?|yrs?)',
            r'(\d+)\s*(?:months?|mos?)',
            r'(\d+)\s*(?:weeks?|wks?)',
            r'(\d+)\s*(?:days?)',
            r'(\d+)\s*(?:hours?|hrs?)'
        ]
        
        # Obligation keywords
        self.obligation_keywords = ['shall', 'must', 'will', 'agrees to', 'undertakes to', 
                                    'is required to', 'is obligated to', 'commits to']
        
        # Right keywords
        self.right_keywords = ['may', 'is entitled to', 'has the right to', 'can', 
                               'is authorized to', 'is permitted to', 'reserves the right']
        
        # Prohibition keywords
        self.prohibition_keywords = ['shall not', 'must not', 'will not', 'cannot', 
                                     'is prohibited from', 'is not permitted to', 
                                     'is not allowed to', 'may not']
    
    def extract_all_entities(self, text: str) -> Dict[str, List[LegalEntity]]:
        """
        Extract all legal entities from contract text.
        
        Args:
            text: Contract text to analyze
            
        Returns:
            Dictionary of entity types to lists of extracted entities
        """
        entities = {
            'parties': self.extract_parties(text),
            'dates': self.extract_dates(text),
            'amounts': self.extract_amounts(text),
            'durations': self.extract_durations(text),
            'jurisdictions': self.extract_jurisdictions(text),
            'obligations': self.extract_obligations(text),
            'rights': self.extract_rights(text),
            'prohibitions': self.extract_prohibitions(text),
            'deliverables': self.extract_deliverables(text),
            'notice_periods': self.extract_notice_periods(text)
        }
        
        return entities
    
    def extract_parties(self, text: str) -> List[LegalEntity]:
        """
        Extract contract parties (companies, individuals).
        """
        parties = []
        
        # Pattern 1: "BETWEEN [Party Name] (hereinafter...)"
        pattern1 = r'(?:BETWEEN|between)\s+([A-Z][A-Za-z\s\.,]+?)(?:\s*\(|,\s*(?:a|an)\s+)'
        matches1 = re.finditer(pattern1, text)
        for match in matches1:
            party_name = match.group(1).strip()
            if len(party_name) > 3:
                parties.append(LegalEntity(
                    entity_type='PARTY',
                    value=party_name,
                    start_pos=match.start(1),
                    end_pos=match.end(1),
                    confidence=0.9,
                    context=text[max(0, match.start()-50):match.end()+50]
                ))
        
        # Pattern 2: Company names with indicators
        for indicator in self.party_indicators:
            pattern = rf'([A-Z][A-Za-z\s&\-\.]+\s+{indicator})'
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                party_name = match.group(1).strip()
                if len(party_name) > 5 and party_name not in [p.value for p in parties]:
                    parties.append(LegalEntity(
                        entity_type='PARTY',
                        value=party_name,
                        start_pos=match.start(1),
                        end_pos=match.end(1),
                        confidence=0.85,
                        context=text[max(0, match.start()-30):match.end()+30]
                    ))
        
        # Pattern 3: "hereinafter referred to as" pattern
        pattern3 = r'([A-Z][A-Za-z\s\.,]+?)\s*\(?\s*hereinafter\s+(?:referred\s+to\s+as|called)\s*["\']?([A-Za-z\s]+)["\']?\)?'
        matches3 = re.finditer(pattern3, text, re.IGNORECASE)
        for match in matches3:
            party_name = match.group(1).strip()
            alias = match.group(2).strip()
            if len(party_name) > 3:
                parties.append(LegalEntity(
                    entity_type='PARTY',
                    value=party_name,
                    start_pos=match.start(1),
                    end_pos=match.end(1),
                    confidence=0.95,
                    context=text[max(0, match.start()-20):match.end()+20],
                    normalized_value=alias
                ))
        
        # Use spaCy NER if available
        if self.nlp:
            doc = self.nlp(text[:50000])  # Limit for performance
            for ent in doc.ents:
                if ent.label_ in ['ORG', 'PERSON']:
                    # Check if not already found
                    if not any(p.value.lower() == ent.text.lower() for p in parties):
                        parties.append(LegalEntity(
                            entity_type='PARTY',
                            value=ent.text,
                            start_pos=ent.start_char,
                            end_pos=ent.end_char,
                            confidence=0.7,
                            context=text[max(0, ent.start_char-30):ent.end_char+30]
                        ))
        
        return self._deduplicate_entities(parties)
    
    def extract_dates(self, text: str) -> List[LegalEntity]:
        """
        Extract dates from contract text.
        """
        dates = []
        
        # Pattern 1: DD/MM/YYYY or DD-MM-YYYY
        pattern1 = r'\b(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})\b'
        matches1 = re.finditer(pattern1, text)
        for match in matches1:
            date_str = match.group(0)
            try:
                parsed = date_parser.parse(date_str, dayfirst=True)
                dates.append(LegalEntity(
                    entity_type='DATE',
                    value=date_str,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.95,
                    context=text[max(0, match.start()-40):match.end()+40],
                    normalized_value=parsed.strftime('%Y-%m-%d')
                ))
            except:
                pass
        
        # Pattern 2: Month DD, YYYY
        months = r'(January|February|March|April|May|June|July|August|September|October|November|December)'
        pattern2 = rf'{months}\s+(\d{{1,2}}),?\s+(\d{{4}})'
        matches2 = re.finditer(pattern2, text, re.IGNORECASE)
        for match in matches2:
            date_str = match.group(0)
            try:
                parsed = date_parser.parse(date_str)
                dates.append(LegalEntity(
                    entity_type='DATE',
                    value=date_str,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.95,
                    context=text[max(0, match.start()-40):match.end()+40],
                    normalized_value=parsed.strftime('%Y-%m-%d')
                ))
            except:
                pass
        
        # Pattern 3: DD Month YYYY
        pattern3 = rf'(\d{{1,2}})\s+{months}\s+(\d{{4}})'
        matches3 = re.finditer(pattern3, text, re.IGNORECASE)
        for match in matches3:
            date_str = match.group(0)
            try:
                parsed = date_parser.parse(date_str)
                dates.append(LegalEntity(
                    entity_type='DATE',
                    value=date_str,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.95,
                    context=text[max(0, match.start()-40):match.end()+40],
                    normalized_value=parsed.strftime('%Y-%m-%d')
                ))
            except:
                pass
        
        # Identify date types based on context
        for date_entity in dates:
            context_lower = date_entity.context.lower()
            if 'effective' in context_lower or 'commencement' in context_lower:
                date_entity.entity_type = 'EFFECTIVE_DATE'
            elif 'expir' in context_lower or 'terminat' in context_lower:
                date_entity.entity_type = 'EXPIRY_DATE'
            elif 'sign' in context_lower or 'execut' in context_lower:
                date_entity.entity_type = 'EXECUTION_DATE'
        
        return self._deduplicate_entities(dates)
    
    def extract_amounts(self, text: str) -> List[LegalEntity]:
        """
        Extract monetary amounts from contract text.
        """
        amounts = []
        
        for pattern, currency_type in self.currency_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                amount_str = match.group(0)
                value = match.group(1).replace(',', '').strip()
                
                # Skip empty values
                if not value:
                    continue
                
                try:
                    # Convert lakhs/crores to actual value
                    if currency_type == 'INR_LAKH':
                        normalized = float(value) * 100000
                        currency_type = 'INR'
                    elif currency_type == 'INR_CRORE':
                        normalized = float(value) * 10000000
                        currency_type = 'INR'
                    else:
                        normalized = float(value)
                except ValueError:
                    continue
                
                amounts.append(LegalEntity(
                    entity_type='AMOUNT',
                    value=amount_str,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.9,
                    context=text[max(0, match.start()-50):match.end()+50],
                    normalized_value=f"{currency_type} {normalized:,.2f}"
                ))
        
        # Identify amount types based on context
        for amount_entity in amounts:
            context_lower = amount_entity.context.lower()
            if 'penalty' in context_lower or 'fine' in context_lower:
                amount_entity.entity_type = 'PENALTY_AMOUNT'
            elif 'payment' in context_lower or 'fee' in context_lower or 'consideration' in context_lower:
                amount_entity.entity_type = 'PAYMENT_AMOUNT'
            elif 'deposit' in context_lower or 'security' in context_lower:
                amount_entity.entity_type = 'DEPOSIT_AMOUNT'
            elif 'liability' in context_lower or 'cap' in context_lower:
                amount_entity.entity_type = 'LIABILITY_CAP'
        
        return amounts
    
    def extract_durations(self, text: str) -> List[LegalEntity]:
        """
        Extract time durations from contract text.
        """
        durations = []
        
        # Combined duration pattern
        duration_pattern = r'(\d+)\s*(years?|yrs?|months?|mos?|weeks?|wks?|days?|hours?|hrs?)'
        matches = re.finditer(duration_pattern, text, re.IGNORECASE)
        
        for match in matches:
            value = match.group(1)
            unit = match.group(2).lower()
            
            # Normalize unit
            if unit.startswith('y'):
                normalized_unit = 'years'
            elif unit.startswith('mo'):
                normalized_unit = 'months'
            elif unit.startswith('w'):
                normalized_unit = 'weeks'
            elif unit.startswith('d'):
                normalized_unit = 'days'
            else:
                normalized_unit = 'hours'
            
            durations.append(LegalEntity(
                entity_type='DURATION',
                value=match.group(0),
                start_pos=match.start(),
                end_pos=match.end(),
                confidence=0.9,
                context=text[max(0, match.start()-50):match.end()+50],
                normalized_value=f"{value} {normalized_unit}"
            ))
        
        return durations
    
    def extract_jurisdictions(self, text: str) -> List[LegalEntity]:
        """
        Extract jurisdiction and governing law references.
        """
        jurisdictions = []
        
        # Pattern for jurisdiction clauses
        jurisdiction_patterns = [
            r'(?:jurisdiction|courts?\s+of|governed\s+by\s+the\s+laws?\s+of|subject\s+to)\s+([A-Za-z\s,]+?)(?:\.|,|\s+and|\s+shall)',
            r'(?:courts?\s+at|courts?\s+in)\s+([A-Za-z\s]+?)(?:\s+shall|\s+will|\.|,)'
        ]
        
        for pattern in jurisdiction_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                jurisdiction = match.group(1).strip()
                
                # Check if it's an Indian jurisdiction
                is_indian = any(j in jurisdiction.lower() for j in self.indian_jurisdictions)
                
                jurisdictions.append(LegalEntity(
                    entity_type='JURISDICTION',
                    value=jurisdiction,
                    start_pos=match.start(1),
                    end_pos=match.end(1),
                    confidence=0.85 if is_indian else 0.7,
                    context=text[max(0, match.start()-30):match.end()+30],
                    normalized_value='INDIA' if is_indian else 'FOREIGN'
                ))
        
        # Also check for explicit mentions of Indian jurisdictions
        for jurisdiction in self.indian_jurisdictions:
            pattern = rf'\b{jurisdiction}\b'
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                # Check context for legal relevance
                context = text[max(0, match.start()-100):match.end()+100].lower()
                if any(kw in context for kw in ['jurisdiction', 'court', 'law', 'govern', 'arbitrat']):
                    jurisdictions.append(LegalEntity(
                        entity_type='JURISDICTION',
                        value=match.group(0),
                        start_pos=match.start(),
                        end_pos=match.end(),
                        confidence=0.8,
                        context=context,
                        normalized_value='INDIA'
                    ))
        
        return self._deduplicate_entities(jurisdictions)
    
    def extract_obligations(self, text: str) -> List[LegalEntity]:
        """
        Extract contractual obligations.
        """
        obligations = []
        sentences = re.split(r'[.;]', text)
        
        for i, sentence in enumerate(sentences):
            for keyword in self.obligation_keywords:
                if keyword.lower() in sentence.lower():
                    # Extract the obligation statement
                    pattern = rf'{keyword}\s+(.+?)(?:\.|;|$)'
                    match = re.search(pattern, sentence, re.IGNORECASE)
                    if match:
                        obligations.append(LegalEntity(
                            entity_type='OBLIGATION',
                            value=match.group(0).strip(),
                            start_pos=0,  # Would need proper position tracking
                            end_pos=0,
                            confidence=0.85,
                            context=sentence.strip()
                        ))
                    break
        
        return obligations[:50]  # Limit to top 50
    
    def extract_rights(self, text: str) -> List[LegalEntity]:
        """
        Extract contractual rights.
        """
        rights = []
        sentences = re.split(r'[.;]', text)
        
        for sentence in sentences:
            for keyword in self.right_keywords:
                if keyword.lower() in sentence.lower():
                    pattern = rf'{keyword}\s+(.+?)(?:\.|;|$)'
                    match = re.search(pattern, sentence, re.IGNORECASE)
                    if match:
                        rights.append(LegalEntity(
                            entity_type='RIGHT',
                            value=match.group(0).strip(),
                            start_pos=0,
                            end_pos=0,
                            confidence=0.85,
                            context=sentence.strip()
                        ))
                    break
        
        return rights[:50]
    
    def extract_prohibitions(self, text: str) -> List[LegalEntity]:
        """
        Extract contractual prohibitions.
        """
        prohibitions = []
        sentences = re.split(r'[.;]', text)
        
        for sentence in sentences:
            for keyword in self.prohibition_keywords:
                if keyword.lower() in sentence.lower():
                    pattern = rf'{keyword}\s+(.+?)(?:\.|;|$)'
                    match = re.search(pattern, sentence, re.IGNORECASE)
                    if match:
                        prohibitions.append(LegalEntity(
                            entity_type='PROHIBITION',
                            value=match.group(0).strip(),
                            start_pos=0,
                            end_pos=0,
                            confidence=0.85,
                            context=sentence.strip()
                        ))
                    break
        
        return prohibitions[:50]
    
    def extract_deliverables(self, text: str) -> List[LegalEntity]:
        """
        Extract deliverables and milestones.
        """
        deliverables = []
        
        # Patterns for deliverables
        patterns = [
            r'(?:deliver|provide|submit|complete)\s+(?:the\s+)?(.+?)(?:\s+within|\s+by|\s+on|\.)',
            r'(?:deliverable|milestone|output):\s*(.+?)(?:\.|;|$)',
            r'(?:phase|stage)\s+\d+[:\s]+(.+?)(?:\.|;|$)'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                deliverable = match.group(1).strip()
                if len(deliverable) > 5 and len(deliverable) < 200:
                    deliverables.append(LegalEntity(
                        entity_type='DELIVERABLE',
                        value=deliverable,
                        start_pos=match.start(1),
                        end_pos=match.end(1),
                        confidence=0.75,
                        context=text[max(0, match.start()-30):match.end()+30]
                    ))
        
        return deliverables[:30]
    
    def extract_notice_periods(self, text: str) -> List[LegalEntity]:
        """
        Extract notice period requirements.
        """
        notice_periods = []
        
        # Pattern for notice periods
        pattern = r'(?:notice\s+(?:period\s+)?of|prior\s+(?:written\s+)?notice\s+of|advance\s+notice\s+of)\s+(\d+)\s*(days?|weeks?|months?)'
        matches = re.finditer(pattern, text, re.IGNORECASE)
        
        for match in matches:
            value = match.group(1)
            unit = match.group(2)
            
            notice_periods.append(LegalEntity(
                entity_type='NOTICE_PERIOD',
                value=f"{value} {unit}",
                start_pos=match.start(),
                end_pos=match.end(),
                confidence=0.9,
                context=text[max(0, match.start()-50):match.end()+50],
                normalized_value=f"{value} {unit.lower()}"
            ))
        
        return notice_periods
    
    def _deduplicate_entities(self, entities: List[LegalEntity]) -> List[LegalEntity]:
        """
        Remove duplicate entities based on value.
        """
        seen = set()
        unique = []
        
        for entity in entities:
            key = (entity.entity_type, entity.value.lower().strip())
            if key not in seen:
                seen.add(key)
                unique.append(entity)
        
        return unique
    
    def get_entity_summary(self, entities: Dict[str, List[LegalEntity]]) -> Dict:
        """
        Generate a summary of extracted entities.
        """
        summary = {
            'total_entities': sum(len(v) for v in entities.values()),
            'entity_counts': {k: len(v) for k, v in entities.items()},
            'key_parties': [e.value for e in entities.get('parties', [])[:5]],
            'key_dates': [e.value for e in entities.get('dates', [])[:5]],
            'total_amounts': [e.normalized_value for e in entities.get('amounts', [])],
            'jurisdictions': list(set(e.value for e in entities.get('jurisdictions', []))),
            'obligation_count': len(entities.get('obligations', [])),
            'right_count': len(entities.get('rights', [])),
            'prohibition_count': len(entities.get('prohibitions', []))
        }
        
        return summary

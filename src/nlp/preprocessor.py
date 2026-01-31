"""
Text Preprocessing Module for Legal Documents
Handles text cleaning, normalization, and tokenization
"""

import re
import string
from typing import List, Dict, Tuple, Optional

# Try to import NLTK, but provide fallbacks if not available
NLTK_AVAILABLE = False
try:
    import nltk
    from nltk.tokenize import sent_tokenize, word_tokenize
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer
    
    # Try to download required NLTK data silently
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        try:
            nltk.download('punkt', quiet=True)
        except:
            pass
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        try:
            nltk.download('stopwords', quiet=True)
        except:
            pass
    try:
        nltk.data.find('corpora/wordnet')
    except LookupError:
        try:
            nltk.download('wordnet', quiet=True)
        except:
            pass
    
    # Check if stopwords are available
    try:
        stopwords.words('english')
        NLTK_AVAILABLE = True
    except:
        NLTK_AVAILABLE = False
except ImportError:
    NLTK_AVAILABLE = False

# Fallback stopwords if NLTK not available
FALLBACK_STOPWORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
    'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
    'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'it',
    'its', 'they', 'them', 'their', 'we', 'our', 'you', 'your', 'he', 'she',
    'him', 'her', 'his', 'i', 'me', 'my', 'who', 'which', 'what', 'when',
    'where', 'why', 'how', 'all', 'each', 'every', 'both', 'few', 'more',
    'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same',
    'so', 'than', 'too', 'very', 'just', 'also', 'now', 'here', 'there', 'then'
}


class TextPreprocessor:
    """
    Advanced text preprocessing for legal contract documents.
    Implements multi-stage pipeline for text normalization and cleaning.
    """
    
    def __init__(self):
        self.lemmatizer = None
        if NLTK_AVAILABLE:
            try:
                self.lemmatizer = WordNetLemmatizer()
                self.stop_words = set(stopwords.words('english'))
            except:
                self.stop_words = FALLBACK_STOPWORDS.copy()
        else:
            self.stop_words = FALLBACK_STOPWORDS.copy()
        
        # Legal-specific stopwords to preserve
        self.legal_preserve_words = {
            'shall', 'must', 'may', 'will', 'should', 'herein', 'hereby',
            'hereto', 'thereof', 'therein', 'whereas', 'whereby', 'wherein',
            'notwithstanding', 'forthwith', 'hereunder', 'thereunder'
        }
        
        # Remove legal terms from stopwords
        self.stop_words -= self.legal_preserve_words
        
        # Common legal abbreviations
        self.legal_abbreviations = {
            'inc.': 'incorporated',
            'ltd.': 'limited',
            'pvt.': 'private',
            'llp': 'limited liability partnership',
            'llc': 'limited liability company',
            'co.': 'company',
            'corp.': 'corporation',
            'govt.': 'government',
            'rs.': 'rupees',
            'inr': 'indian rupees',
            'no.': 'number',
            'nos.': 'numbers',
            'viz.': 'namely',
            'i.e.': 'that is',
            'e.g.': 'for example',
            'etc.': 'et cetera',
            'w.r.t.': 'with respect to',
            'w.e.f.': 'with effect from'
        }
        
        # Section/clause markers
        self.section_patterns = [
            r'^\d+\.\s',           # 1. 
            r'^\d+\.\d+\s',        # 1.1 
            r'^\d+\.\d+\.\d+\s',   # 1.1.1
            r'^[a-z]\)\s',         # a)
            r'^\([a-z]\)\s',       # (a)
            r'^[ivxlcdm]+\.\s',    # i. ii. iii.
            r'^\([ivxlcdm]+\)\s',  # (i) (ii)
            r'^ARTICLE\s+\d+',     # ARTICLE 1
            r'^SECTION\s+\d+',     # SECTION 1
            r'^CLAUSE\s+\d+',      # CLAUSE 1
            r'^SCHEDULE\s+[A-Z\d]' # SCHEDULE A
        ]
        
    def preprocess(self, text: str, preserve_structure: bool = True) -> Dict:
        """
        Main preprocessing pipeline for contract text.
        
        Args:
            text: Raw contract text
            preserve_structure: Whether to preserve document structure
            
        Returns:
            Dictionary containing processed text and metadata
        """
        result = {
            'original_text': text,
            'cleaned_text': '',
            'normalized_text': '',
            'sentences': [],
            'tokens': [],
            'sections': [],
            'metadata': {}
        }
        
        # Stage 1: Basic cleaning
        cleaned = self._basic_clean(text)
        result['cleaned_text'] = cleaned
        
        # Stage 2: Normalize legal terms
        normalized = self._normalize_legal_terms(cleaned)
        result['normalized_text'] = normalized
        
        # Stage 3: Extract sections/clauses
        if preserve_structure:
            result['sections'] = self._extract_sections(normalized)
        
        # Stage 4: Sentence tokenization
        result['sentences'] = self._tokenize_sentences(normalized)
        
        # Stage 5: Word tokenization
        result['tokens'] = self._tokenize_words(normalized)
        
        # Stage 6: Extract metadata
        result['metadata'] = self._extract_metadata(text)
        
        return result
    
    def _basic_clean(self, text: str) -> str:
        """
        Perform basic text cleaning operations.
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page numbers and headers/footers patterns
        text = re.sub(r'Page\s+\d+\s+of\s+\d+', '', text, flags=re.IGNORECASE)
        text = re.sub(r'-\s*\d+\s*-', '', text)
        
        # Remove special characters but preserve legal symbols
        text = re.sub(r'[^\w\s\.\,\;\:\'\"\(\)\[\]\{\}\-\/\@\#\$\%\&\*\+\=\!\?\₹]', '', text)
        
        # Normalize quotes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        
        # Remove multiple periods (but keep ellipsis)
        text = re.sub(r'\.{4,}', '...', text)
        
        # Normalize dashes
        text = re.sub(r'[–—]', '-', text)
        
        return text.strip()
    
    def _normalize_legal_terms(self, text: str) -> str:
        """
        Normalize legal abbreviations and terms.
        """
        # Expand abbreviations
        for abbr, expansion in self.legal_abbreviations.items():
            pattern = re.compile(re.escape(abbr), re.IGNORECASE)
            text = pattern.sub(expansion, text)
        
        # Normalize party references
        text = re.sub(r'\b(first\s+party|party\s+of\s+the\s+first\s+part)\b', 
                     'FIRST_PARTY', text, flags=re.IGNORECASE)
        text = re.sub(r'\b(second\s+party|party\s+of\s+the\s+second\s+part)\b', 
                     'SECOND_PARTY', text, flags=re.IGNORECASE)
        
        # Normalize date formats
        text = self._normalize_dates(text)
        
        # Normalize currency
        text = self._normalize_currency(text)
        
        return text
    
    def _normalize_dates(self, text: str) -> str:
        """
        Normalize various date formats to standard format.
        """
        # Pattern: DD/MM/YYYY or DD-MM-YYYY
        text = re.sub(
            r'\b(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})\b',
            r'\1/\2/\3',
            text
        )
        
        # Pattern: Month DD, YYYY
        months = r'(January|February|March|April|May|June|July|August|September|October|November|December)'
        text = re.sub(
            rf'{months}\s+(\d{{1,2}}),?\s+(\d{{4}})',
            r'\1 \2, \3',
            text,
            flags=re.IGNORECASE
        )
        
        return text
    
    def _normalize_currency(self, text: str) -> str:
        """
        Normalize currency representations.
        """
        # INR patterns
        text = re.sub(r'₹\s*', 'INR ', text)
        text = re.sub(r'Rs\.?\s*', 'INR ', text, flags=re.IGNORECASE)
        text = re.sub(r'Rupees?\s*', 'INR ', text, flags=re.IGNORECASE)
        
        # Normalize large numbers (lakhs, crores)
        text = re.sub(r'(\d+)\s*lakh', r'\1,00,000', text, flags=re.IGNORECASE)
        text = re.sub(r'(\d+)\s*crore', r'\1,00,00,000', text, flags=re.IGNORECASE)
        
        return text
    
    def _extract_sections(self, text: str) -> List[Dict]:
        """
        Extract document sections and clauses with their hierarchy.
        """
        sections = []
        lines = text.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line is a section header
            is_section = False
            section_level = 0
            
            for i, pattern in enumerate(self.section_patterns):
                if re.match(pattern, line, re.IGNORECASE):
                    is_section = True
                    section_level = i // 3 + 1  # Approximate hierarchy level
                    break
            
            if is_section:
                # Save previous section
                if current_section:
                    current_section['content'] = ' '.join(current_content)
                    sections.append(current_section)
                
                # Start new section
                current_section = {
                    'header': line,
                    'level': section_level,
                    'content': ''
                }
                current_content = []
            else:
                current_content.append(line)
        
        # Save last section
        if current_section:
            current_section['content'] = ' '.join(current_content)
            sections.append(current_section)
        
        return sections
    
    def _tokenize_sentences(self, text: str) -> List[str]:
        """
        Tokenize text into sentences, handling legal document peculiarities.
        """
        # Pre-process to handle legal abbreviations that might confuse tokenizer
        temp_text = text
        for abbr in self.legal_abbreviations.keys():
            temp_text = temp_text.replace(abbr, abbr.replace('.', '<DOT>'))
        
        # Tokenize - use NLTK if available, otherwise use regex fallback
        if NLTK_AVAILABLE:
            try:
                sentences = sent_tokenize(temp_text)
            except:
                sentences = self._fallback_sent_tokenize(temp_text)
        else:
            sentences = self._fallback_sent_tokenize(temp_text)
        
        # Restore dots
        sentences = [s.replace('<DOT>', '.') for s in sentences]
        
        # Filter out very short sentences (likely artifacts)
        sentences = [s for s in sentences if len(s.split()) >= 3]
        
        return sentences
    
    def _fallback_sent_tokenize(self, text: str) -> List[str]:
        """Fallback sentence tokenization using regex."""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _tokenize_words(self, text: str, remove_stopwords: bool = False) -> List[str]:
        """
        Tokenize text into words with optional stopword removal.
        """
        if NLTK_AVAILABLE:
            try:
                tokens = word_tokenize(text.lower())
            except:
                tokens = self._fallback_word_tokenize(text.lower())
        else:
            tokens = self._fallback_word_tokenize(text.lower())
        
        # Remove punctuation tokens
        tokens = [t for t in tokens if t not in string.punctuation]
        
        if remove_stopwords:
            tokens = [t for t in tokens if t not in self.stop_words]
        
        return tokens
    
    def _fallback_word_tokenize(self, text: str) -> List[str]:
        """Fallback word tokenization using regex."""
        return re.findall(r'\b\w+\b', text.lower())
    
    def _extract_metadata(self, text: str) -> Dict:
        """
        Extract document metadata from text.
        """
        metadata = {
            'word_count': len(text.split()),
            'char_count': len(text),
            'sentence_count': len(self._tokenize_sentences(text)),
            'has_schedules': bool(re.search(r'SCHEDULE\s+[A-Z\d]', text, re.IGNORECASE)),
            'has_annexures': bool(re.search(r'ANNEXURE\s+[A-Z\d]', text, re.IGNORECASE)),
            'has_exhibits': bool(re.search(r'EXHIBIT\s+[A-Z\d]', text, re.IGNORECASE)),
            'estimated_pages': max(1, len(text) // 3000)  # Rough estimate
        }
        
        return metadata
    
    def get_legal_keywords(self, text: str) -> List[Tuple[str, int]]:
        """
        Extract legal keywords and their frequencies.
        """
        legal_keywords = [
            'agreement', 'contract', 'party', 'parties', 'shall', 'must',
            'obligation', 'liability', 'indemnify', 'terminate', 'termination',
            'breach', 'default', 'remedy', 'damages', 'penalty', 'warranty',
            'representation', 'covenant', 'condition', 'precedent', 'subsequent',
            'confidential', 'proprietary', 'intellectual property', 'jurisdiction',
            'arbitration', 'dispute', 'governing law', 'force majeure', 'assignment',
            'waiver', 'amendment', 'notice', 'effective date', 'term', 'renewal'
        ]
        
        text_lower = text.lower()
        keyword_freq = []
        
        for keyword in legal_keywords:
            count = len(re.findall(rf'\b{keyword}\b', text_lower))
            if count > 0:
                keyword_freq.append((keyword, count))
        
        return sorted(keyword_freq, key=lambda x: x[1], reverse=True)
    
    def extract_definitions(self, text: str) -> Dict[str, str]:
        """
        Extract defined terms from the contract.
        """
        definitions = {}
        
        # Pattern: "Term" means/shall mean...
        pattern1 = r'"([^"]+)"\s+(?:means|shall\s+mean|refers\s+to)\s+([^.]+\.)'
        matches1 = re.findall(pattern1, text, re.IGNORECASE)
        
        for term, definition in matches1:
            definitions[term.strip()] = definition.strip()
        
        # Pattern: Term: definition
        pattern2 = r'([A-Z][a-zA-Z\s]+):\s+means\s+([^.]+\.)'
        matches2 = re.findall(pattern2, text)
        
        for term, definition in matches2:
            definitions[term.strip()] = definition.strip()
        
        return definitions
    
    def segment_by_topic(self, text: str) -> Dict[str, str]:
        """
        Segment contract text by common legal topics.
        """
        topics = {
            'preamble': '',
            'definitions': '',
            'scope': '',
            'payment': '',
            'term_termination': '',
            'confidentiality': '',
            'ip_rights': '',
            'indemnification': '',
            'limitation_liability': '',
            'dispute_resolution': '',
            'general_provisions': ''
        }
        
        topic_patterns = {
            'preamble': r'(WHEREAS|RECITALS|BACKGROUND)',
            'definitions': r'(DEFINITIONS|INTERPRETATION)',
            'scope': r'(SCOPE\s+OF\s+WORK|SERVICES|DELIVERABLES)',
            'payment': r'(PAYMENT|COMPENSATION|FEES|CONSIDERATION)',
            'term_termination': r'(TERM|DURATION|TERMINATION)',
            'confidentiality': r'(CONFIDENTIAL|NON-DISCLOSURE)',
            'ip_rights': r'(INTELLECTUAL\s+PROPERTY|IP\s+RIGHTS|COPYRIGHT)',
            'indemnification': r'(INDEMNIF|HOLD\s+HARMLESS)',
            'limitation_liability': r'(LIMITATION\s+OF\s+LIABILITY|LIABILITY\s+CAP)',
            'dispute_resolution': r'(DISPUTE|ARBITRATION|JURISDICTION)',
            'general_provisions': r'(GENERAL|MISCELLANEOUS|BOILERPLATE)'
        }
        
        sections = self._extract_sections(text)
        
        for section in sections:
            header = section['header'].upper()
            content = section['content']
            
            for topic, pattern in topic_patterns.items():
                if re.search(pattern, header):
                    topics[topic] += content + ' '
                    break
        
        return {k: v.strip() for k, v in topics.items() if v.strip()}

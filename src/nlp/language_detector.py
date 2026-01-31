"""
Language Detection and Multilingual Support Module
Handles English and Hindi contract processing
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class LanguageInfo:
    """Information about detected language."""
    primary_language: str
    language_code: str
    confidence: float
    is_multilingual: bool
    language_distribution: Dict[str, float]


class LanguageHandler:
    """
    Multilingual support for contract analysis.
    Handles English and Hindi text detection, normalization, and translation.
    """
    
    def __init__(self):
        # Hindi Unicode range
        self.hindi_range = (0x0900, 0x097F)  # Devanagari script
        
        # Common Hindi legal terms
        self.hindi_legal_terms = {
            'अनुबंध': 'contract',
            'समझौता': 'agreement',
            'पक्ष': 'party',
            'शर्तें': 'terms',
            'नियम': 'conditions',
            'दायित्व': 'liability',
            'अधिकार': 'rights',
            'भुगतान': 'payment',
            'समाप्ति': 'termination',
            'विवाद': 'dispute',
            'मध्यस्थता': 'arbitration',
            'क्षेत्राधिकार': 'jurisdiction',
            'गोपनीयता': 'confidentiality',
            'क्षतिपूर्ति': 'indemnity',
            'वारंटी': 'warranty',
            'प्रतिनिधित्व': 'representation',
            'अवधि': 'term/duration',
            'नोटिस': 'notice',
            'संशोधन': 'amendment',
            'हस्ताक्षर': 'signature',
            'साक्षी': 'witness',
            'मुहर': 'seal',
            'रुपये': 'rupees',
            'लाख': 'lakh',
            'करोड़': 'crore',
            'प्रतिशत': 'percent',
            'वार्षिक': 'annual',
            'मासिक': 'monthly',
            'दैनिक': 'daily'
        }
        
        # Common English legal terms for detection
        self.english_legal_terms = [
            'agreement', 'contract', 'party', 'parties', 'whereas', 'hereby',
            'herein', 'thereof', 'shall', 'must', 'liability', 'indemnify',
            'terminate', 'jurisdiction', 'arbitration', 'confidential'
        ]
        
        # Transliteration mapping (Hindi to English phonetic)
        self.transliteration_map = {
            'अ': 'a', 'आ': 'aa', 'इ': 'i', 'ई': 'ee', 'उ': 'u', 'ऊ': 'oo',
            'ए': 'e', 'ऐ': 'ai', 'ओ': 'o', 'औ': 'au', 'अं': 'an', 'अः': 'ah',
            'क': 'k', 'ख': 'kh', 'ग': 'g', 'घ': 'gh', 'ङ': 'ng',
            'च': 'ch', 'छ': 'chh', 'ज': 'j', 'झ': 'jh', 'ञ': 'ny',
            'ट': 't', 'ठ': 'th', 'ड': 'd', 'ढ': 'dh', 'ण': 'n',
            'त': 't', 'थ': 'th', 'द': 'd', 'ध': 'dh', 'न': 'n',
            'प': 'p', 'फ': 'ph', 'ब': 'b', 'भ': 'bh', 'म': 'm',
            'य': 'y', 'र': 'r', 'ल': 'l', 'व': 'v', 'श': 'sh',
            'ष': 'sh', 'स': 's', 'ह': 'h',
            'ा': 'a', 'ि': 'i', 'ी': 'ee', 'ु': 'u', 'ू': 'oo',
            'े': 'e', 'ै': 'ai', 'ो': 'o', 'ौ': 'au',
            '्': '', 'ं': 'n', 'ः': 'h',
            '०': '0', '१': '1', '२': '2', '३': '3', '४': '4',
            '५': '5', '६': '6', '७': '7', '८': '8', '९': '9'
        }
    
    def detect_language(self, text: str) -> LanguageInfo:
        """
        Detect the primary language of the text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            LanguageInfo object with detection results
        """
        if not text:
            return LanguageInfo(
                primary_language='unknown',
                language_code='und',
                confidence=0.0,
                is_multilingual=False,
                language_distribution={}
            )
        
        # Count characters by script
        hindi_chars = 0
        english_chars = 0
        total_chars = 0
        
        for char in text:
            if char.isalpha():
                total_chars += 1
                code_point = ord(char)
                if self.hindi_range[0] <= code_point <= self.hindi_range[1]:
                    hindi_chars += 1
                elif char.isascii():
                    english_chars += 1
        
        if total_chars == 0:
            return LanguageInfo(
                primary_language='unknown',
                language_code='und',
                confidence=0.0,
                is_multilingual=False,
                language_distribution={}
            )
        
        # Calculate percentages
        hindi_pct = hindi_chars / total_chars
        english_pct = english_chars / total_chars
        
        # Determine primary language
        if hindi_pct > english_pct:
            primary = 'Hindi'
            code = 'hi'
            confidence = hindi_pct
        else:
            primary = 'English'
            code = 'en'
            confidence = english_pct
        
        # Check if multilingual
        is_multilingual = min(hindi_pct, english_pct) > 0.1
        
        return LanguageInfo(
            primary_language=primary,
            language_code=code,
            confidence=confidence,
            is_multilingual=is_multilingual,
            language_distribution={
                'hindi': round(hindi_pct, 3),
                'english': round(english_pct, 3)
            }
        )
    
    def extract_hindi_text(self, text: str) -> List[str]:
        """
        Extract Hindi text segments from mixed-language text.
        """
        hindi_segments = []
        current_segment = []
        
        for char in text:
            code_point = ord(char)
            if self.hindi_range[0] <= code_point <= self.hindi_range[1] or char in ' \n\t':
                current_segment.append(char)
            else:
                if current_segment:
                    segment = ''.join(current_segment).strip()
                    if segment and any(self.hindi_range[0] <= ord(c) <= self.hindi_range[1] for c in segment):
                        hindi_segments.append(segment)
                    current_segment = []
        
        # Don't forget the last segment
        if current_segment:
            segment = ''.join(current_segment).strip()
            if segment and any(self.hindi_range[0] <= ord(c) <= self.hindi_range[1] for c in segment):
                hindi_segments.append(segment)
        
        return hindi_segments
    
    def extract_english_text(self, text: str) -> List[str]:
        """
        Extract English text segments from mixed-language text.
        """
        english_segments = []
        current_segment = []
        
        for char in text:
            if char.isascii() or char in ' \n\t':
                current_segment.append(char)
            else:
                if current_segment:
                    segment = ''.join(current_segment).strip()
                    if segment and any(c.isalpha() for c in segment):
                        english_segments.append(segment)
                    current_segment = []
        
        if current_segment:
            segment = ''.join(current_segment).strip()
            if segment and any(c.isalpha() for c in segment):
                english_segments.append(segment)
        
        return english_segments
    
    def transliterate_hindi_to_english(self, hindi_text: str) -> str:
        """
        Transliterate Hindi text to English phonetic representation.
        """
        result = []
        
        for char in hindi_text:
            if char in self.transliteration_map:
                result.append(self.transliteration_map[char])
            else:
                result.append(char)
        
        return ''.join(result)
    
    def translate_hindi_legal_terms(self, text: str) -> Tuple[str, Dict[str, str]]:
        """
        Translate known Hindi legal terms to English.
        
        Returns:
            Tuple of (translated text, dictionary of translations made)
        """
        translations_made = {}
        translated_text = text
        
        for hindi_term, english_term in self.hindi_legal_terms.items():
            if hindi_term in translated_text:
                translated_text = translated_text.replace(hindi_term, f"[{english_term}]")
                translations_made[hindi_term] = english_term
        
        return translated_text, translations_made
    
    def normalize_for_nlp(self, text: str) -> Dict:
        """
        Normalize multilingual text for NLP processing.
        
        Returns:
            Dictionary with normalized text and metadata
        """
        lang_info = self.detect_language(text)
        
        result = {
            'original_text': text,
            'language_info': lang_info,
            'normalized_text': text,
            'hindi_segments': [],
            'english_segments': [],
            'translations': {}
        }
        
        if lang_info.is_multilingual or lang_info.language_code == 'hi':
            # Extract segments
            result['hindi_segments'] = self.extract_hindi_text(text)
            result['english_segments'] = self.extract_english_text(text)
            
            # Translate Hindi legal terms
            normalized, translations = self.translate_hindi_legal_terms(text)
            result['normalized_text'] = normalized
            result['translations'] = translations
            
            # If primarily Hindi, also provide transliteration
            if lang_info.language_code == 'hi':
                result['transliterated_text'] = self.transliterate_hindi_to_english(text)
        
        return result
    
    def prepare_for_llm(self, text: str) -> str:
        """
        Prepare text for LLM processing by normalizing Hindi content.
        """
        lang_info = self.detect_language(text)
        
        if lang_info.language_code == 'en' and not lang_info.is_multilingual:
            return text
        
        # For Hindi or mixed content, add context
        normalized = self.normalize_for_nlp(text)
        
        if normalized['translations']:
            # Add translation notes
            translation_notes = "\n\n[Hindi Terms Detected:\n"
            for hindi, english in normalized['translations'].items():
                translation_notes += f"  {hindi} = {english}\n"
            translation_notes += "]\n"
            
            return normalized['normalized_text'] + translation_notes
        
        return text
    
    def get_output_language_prompt(self, target_language: str = 'en') -> str:
        """
        Get prompt instruction for output language.
        """
        if target_language == 'hi':
            return "Please provide the response in Hindi (Devanagari script)."
        elif target_language == 'hi-en':
            return "Please provide the response in both Hindi and English."
        else:
            return "Please provide the response in simple, clear English suitable for business owners."
    
    def detect_legal_terms(self, text: str) -> Dict[str, List[str]]:
        """
        Detect legal terms in both English and Hindi.
        """
        detected = {
            'english_terms': [],
            'hindi_terms': []
        }
        
        text_lower = text.lower()
        
        # Check English terms
        for term in self.english_legal_terms:
            if term in text_lower:
                detected['english_terms'].append(term)
        
        # Check Hindi terms
        for hindi_term in self.hindi_legal_terms.keys():
            if hindi_term in text:
                detected['hindi_terms'].append(hindi_term)
        
        return detected
    
    def create_bilingual_summary(self, english_summary: str) -> Dict[str, str]:
        """
        Create a bilingual summary structure.
        Note: Actual Hindi translation would require an LLM or translation API.
        """
        return {
            'english': english_summary,
            'hindi_note': 'Hindi translation available upon request via LLM.',
            'simplified_english': self._simplify_english(english_summary)
        }
    
    def _simplify_english(self, text: str) -> str:
        """
        Simplify English text for non-native speakers.
        """
        # Replace complex legal terms with simpler alternatives
        simplifications = {
            'hereinafter': 'from now on',
            'hereby': 'by this',
            'herein': 'in this document',
            'thereof': 'of that',
            'therein': 'in that',
            'whereas': 'since',
            'notwithstanding': 'despite',
            'forthwith': 'immediately',
            'hereunder': 'under this agreement',
            'pursuant to': 'according to',
            'in lieu of': 'instead of',
            'inter alia': 'among other things',
            'mutatis mutandis': 'with necessary changes',
            'prima facie': 'at first look',
            'bona fide': 'genuine',
            'force majeure': 'unforeseeable circumstances'
        }
        
        simplified = text
        for complex_term, simple_term in simplifications.items():
            pattern = re.compile(re.escape(complex_term), re.IGNORECASE)
            simplified = pattern.sub(simple_term, simplified)
        
        return simplified
    
    def get_language_stats(self, text: str) -> Dict:
        """
        Get detailed language statistics for the text.
        """
        lang_info = self.detect_language(text)
        
        stats = {
            'primary_language': lang_info.primary_language,
            'confidence': lang_info.confidence,
            'is_multilingual': lang_info.is_multilingual,
            'distribution': lang_info.language_distribution,
            'word_count': len(text.split()),
            'hindi_word_count': len(' '.join(self.extract_hindi_text(text)).split()),
            'english_word_count': len(' '.join(self.extract_english_text(text)).split()),
            'legal_terms_detected': self.detect_legal_terms(text)
        }
        
        return stats

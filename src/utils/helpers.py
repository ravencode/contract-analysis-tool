"""
Helper Utilities Module
Common utility functions for the contract analysis system
"""

import re
import hashlib
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import json


def calculate_file_hash(content: bytes) -> str:
    """Calculate SHA256 hash of file content."""
    return hashlib.sha256(content).hexdigest()


def truncate_text(text: str, max_length: int = 500, suffix: str = "...") -> str:
    """Truncate text to specified length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def clean_text(text: str) -> str:
    """Clean and normalize text."""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove control characters
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    return text.strip()


def format_currency(amount: float, currency: str = "INR") -> str:
    """Format currency amount."""
    if currency == "INR":
        # Indian number formatting (lakhs, crores)
        if amount >= 10000000:
            return f"₹{amount/10000000:.2f} Cr"
        elif amount >= 100000:
            return f"₹{amount/100000:.2f} L"
        else:
            return f"₹{amount:,.2f}"
    else:
        return f"{currency} {amount:,.2f}"


def format_date(date_str: str, output_format: str = "%d %B %Y") -> str:
    """Format date string to readable format."""
    from dateutil import parser
    try:
        parsed = parser.parse(date_str)
        return parsed.strftime(output_format)
    except:
        return date_str


def calculate_reading_time(text: str, wpm: int = 200) -> int:
    """Calculate estimated reading time in minutes."""
    word_count = len(text.split())
    return max(1, round(word_count / wpm))


def extract_numbers(text: str) -> List[float]:
    """Extract all numbers from text."""
    pattern = r'[\d,]+\.?\d*'
    matches = re.findall(pattern, text)
    numbers = []
    for match in matches:
        try:
            num = float(match.replace(',', ''))
            numbers.append(num)
        except ValueError:
            continue
    return numbers


def highlight_text(text: str, keywords: List[str], 
                   marker: str = "**") -> str:
    """Highlight keywords in text."""
    for keyword in keywords:
        pattern = re.compile(rf'\b({re.escape(keyword)})\b', re.IGNORECASE)
        text = pattern.sub(f'{marker}\\1{marker}', text)
    return text


def split_into_sentences(text: str) -> List[str]:
    """Split text into sentences."""
    # Handle common abbreviations
    text = re.sub(r'\b(Mr|Mrs|Ms|Dr|Prof|Inc|Ltd|Co|vs|etc)\.\s', r'\1<DOT> ', text)
    
    # Split on sentence boundaries
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    # Restore dots
    sentences = [s.replace('<DOT>', '.') for s in sentences]
    
    return [s.strip() for s in sentences if s.strip()]


def get_word_frequency(text: str, top_n: int = 20) -> List[Tuple[str, int]]:
    """Get word frequency distribution."""
    from collections import Counter
    
    # Tokenize and clean
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    
    # Remove common stopwords
    stopwords = {'the', 'and', 'for', 'that', 'this', 'with', 'are', 'was',
                 'were', 'been', 'have', 'has', 'had', 'will', 'would', 'could',
                 'should', 'may', 'can', 'from', 'they', 'them', 'their', 'which'}
    words = [w for w in words if w not in stopwords]
    
    return Counter(words).most_common(top_n)


def create_summary_stats(text: str) -> Dict:
    """Create summary statistics for text."""
    sentences = split_into_sentences(text)
    words = text.split()
    
    return {
        'character_count': len(text),
        'word_count': len(words),
        'sentence_count': len(sentences),
        'paragraph_count': len(text.split('\n\n')),
        'avg_sentence_length': len(words) / len(sentences) if sentences else 0,
        'reading_time_minutes': calculate_reading_time(text)
    }


def safe_json_loads(json_str: str) -> Optional[Dict]:
    """Safely parse JSON string."""
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        # Try to extract JSON from markdown
        patterns = [
            r'```json\s*([\s\S]*?)\s*```',
            r'```\s*([\s\S]*?)\s*```',
            r'\{[\s\S]*\}'
        ]
        for pattern in patterns:
            match = re.search(pattern, json_str)
            if match:
                try:
                    json_content = match.group(1) if '```' in pattern else match.group(0)
                    return json.loads(json_content.strip())
                except json.JSONDecodeError:
                    continue
        return None


def format_risk_score(score: float) -> str:
    """Format risk score for display."""
    if score >= 0.8:
        return f"🔴 Critical ({score:.0%})"
    elif score >= 0.6:
        return f"🟠 High ({score:.0%})"
    elif score >= 0.35:
        return f"🟡 Medium ({score:.0%})"
    else:
        return f"🟢 Low ({score:.0%})"


def format_compliance_status(status: str) -> str:
    """Format compliance status for display."""
    status_lower = status.lower().replace('_', ' ')
    if 'compliant' in status_lower and 'non' not in status_lower and 'partial' not in status_lower:
        return f"✅ {status_lower.title()}"
    elif 'partial' in status_lower:
        return f"⚠️ {status_lower.title()}"
    else:
        return f"❌ {status_lower.title()}"


def generate_session_id() -> str:
    """Generate a unique session ID."""
    import uuid
    return f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"


def mask_sensitive_data(text: str) -> str:
    """Mask potentially sensitive data in text."""
    # Mask email addresses
    text = re.sub(r'\b[\w.-]+@[\w.-]+\.\w+\b', '[EMAIL]', text)
    
    # Mask phone numbers (Indian format)
    text = re.sub(r'\b(?:\+91[-\s]?)?[6-9]\d{9}\b', '[PHONE]', text)
    
    # Mask PAN numbers
    text = re.sub(r'\b[A-Z]{5}\d{4}[A-Z]\b', '[PAN]', text)
    
    # Mask Aadhaar numbers
    text = re.sub(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', '[AADHAAR]', text)
    
    return text


def validate_contract_text(text: str) -> Tuple[bool, str]:
    """Validate if text appears to be a contract."""
    if not text or len(text.strip()) < 100:
        return False, "Text is too short to be a valid contract"
    
    # Check for contract indicators
    contract_indicators = [
        r'\b(agreement|contract|deed|memorandum)\b',
        r'\b(party|parties)\b',
        r'\b(whereas|hereby|herein)\b',
        r'\b(terms|conditions)\b'
    ]
    
    text_lower = text.lower()
    matches = sum(1 for pattern in contract_indicators 
                  if re.search(pattern, text_lower))
    
    if matches < 2:
        return False, "Text does not appear to be a contract document"
    
    return True, "Valid contract document"


def create_progress_bar(current: int, total: int, width: int = 20) -> str:
    """Create a text-based progress bar."""
    if total == 0:
        return "[" + "=" * width + "]"
    
    progress = current / total
    filled = int(width * progress)
    bar = "=" * filled + "-" * (width - filled)
    percentage = progress * 100
    
    return f"[{bar}] {percentage:.0f}%"


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format."""
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} minutes"
    else:
        hours = seconds / 3600
        return f"{hours:.1f} hours"


def chunk_text(text: str, chunk_size: int = 4000, 
               overlap: int = 200) -> List[str]:
    """Split text into overlapping chunks for processing."""
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # Try to break at sentence boundary
        if end < len(text):
            # Look for sentence end near the chunk boundary
            search_start = max(end - 100, start)
            sentence_end = text.rfind('.', search_start, end)
            if sentence_end > start:
                end = sentence_end + 1
        
        chunks.append(text[start:end])
        start = end - overlap
    
    return chunks


def merge_dicts_deep(dict1: Dict, dict2: Dict) -> Dict:
    """Deep merge two dictionaries."""
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts_deep(result[key], value)
        elif key in result and isinstance(result[key], list) and isinstance(value, list):
            result[key] = result[key] + value
        else:
            result[key] = value
    
    return result

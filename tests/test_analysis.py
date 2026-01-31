"""
Test Script for Contract Analysis System
Validates core functionality without requiring API keys
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.nlp.preprocessor import TextPreprocessor
from src.nlp.entity_extractor import LegalEntityExtractor
from src.nlp.clause_parser import ClauseParser
from src.nlp.language_detector import LanguageHandler
from src.analysis.contract_classifier import ContractClassifier
from src.analysis.risk_analyzer import RiskAnalyzer
from src.analysis.compliance_checker import ComplianceChecker
from src.analysis.similarity_matcher import SimilarityMatcher
from src.document.extractor import DocumentExtractor


# Sample contract text for testing
SAMPLE_CONTRACT = """
EMPLOYMENT AGREEMENT

This Employment Agreement ("Agreement") is made on January 15, 2026

BETWEEN:

TechVision Solutions Private Limited, a company incorporated under the Companies Act, 
having its registered office at Bangalore, Karnataka (hereinafter referred to as the "Company")

AND

Rahul Sharma, residing at Koramangala, Bangalore (hereinafter referred to as the "Employee")

WHEREAS the Company desires to employ the Employee as a Senior Software Engineer.

1. POSITION AND DUTIES

1.1 The Company hereby employs the Employee in the position of Senior Software Engineer.
1.2 The Employee shall report to the Engineering Manager.

2. COMPENSATION

2.1 The Company shall pay the Employee a gross annual salary of INR 18,00,000 (Rupees Eighteen Lakhs only).
2.2 The Employee shall be entitled to Provident Fund and medical insurance of Rs. 5,00,000.

3. CONFIDENTIALITY

3.1 The Employee shall maintain strict confidentiality of all proprietary information and trade secrets.
3.2 This obligation shall survive termination for 3 years.

4. NON-COMPETE

4.1 During employment and for 24 months thereafter, the Employee shall not engage in any 
business that competes with the Company anywhere in India.

5. TERMINATION

5.1 Either Party may terminate with 90 days' written notice.
5.2 The Company may terminate immediately at its sole discretion without cause.

6. INTELLECTUAL PROPERTY

6.1 All intellectual property created by the Employee shall irrevocably belong to the Company.

7. DISPUTE RESOLUTION

7.1 Any dispute shall be referred to arbitration in Bangalore under the Arbitration Act, 1996.

8. GOVERNING LAW

8.1 This Agreement shall be governed by the laws of India.
8.2 The courts of Bangalore shall have exclusive jurisdiction.

IN WITNESS WHEREOF, the Parties have executed this Agreement.
"""


def test_preprocessor():
    """Test text preprocessing."""
    print("\n" + "="*50)
    print("Testing Text Preprocessor")
    print("="*50)
    
    preprocessor = TextPreprocessor()
    result = preprocessor.preprocess(SAMPLE_CONTRACT)
    
    print(f"✓ Original length: {len(SAMPLE_CONTRACT)} chars")
    print(f"✓ Cleaned length: {len(result['cleaned_text'])} chars")
    print(f"✓ Sentences found: {len(result['sentences'])}")
    print(f"✓ Tokens found: {len(result['tokens'])}")
    print(f"✓ Sections found: {len(result['sections'])}")
    
    keywords = preprocessor.get_legal_keywords(SAMPLE_CONTRACT)
    print(f"✓ Top keywords: {keywords[:5]}")
    
    return True


def test_entity_extractor():
    """Test entity extraction."""
    print("\n" + "="*50)
    print("Testing Entity Extractor")
    print("="*50)
    
    extractor = LegalEntityExtractor()
    entities = extractor.extract_all_entities(SAMPLE_CONTRACT)
    
    print(f"✓ Parties found: {len(entities['parties'])}")
    for party in entities['parties'][:3]:
        print(f"  - {party.value}")
    
    print(f"✓ Dates found: {len(entities['dates'])}")
    for date in entities['dates'][:3]:
        print(f"  - {date.value}")
    
    print(f"✓ Amounts found: {len(entities['amounts'])}")
    for amount in entities['amounts'][:3]:
        print(f"  - {amount.value}")
    
    print(f"✓ Obligations found: {len(entities['obligations'])}")
    print(f"✓ Rights found: {len(entities['rights'])}")
    print(f"✓ Prohibitions found: {len(entities['prohibitions'])}")
    
    return True


def test_clause_parser():
    """Test clause parsing."""
    print("\n" + "="*50)
    print("Testing Clause Parser")
    print("="*50)
    
    parser = ClauseParser()
    clauses = parser.parse_clauses(SAMPLE_CONTRACT)
    
    print(f"✓ Clauses found: {len(clauses)}")
    for clause in clauses[:5]:
        print(f"  - {clause.title} ({clause.clause_type.value})")
    
    analysis = parser.analyze_clause_structure(clauses)
    print(f"✓ Clause types: {list(analysis['by_type'].keys())}")
    print(f"✓ Missing standard clauses: {analysis['missing_standard_clauses']}")
    
    ambiguous = parser.detect_ambiguous_clauses(clauses)
    print(f"✓ Ambiguous clauses: {len(ambiguous)}")
    
    return True


def test_language_detector():
    """Test language detection."""
    print("\n" + "="*50)
    print("Testing Language Detector")
    print("="*50)
    
    handler = LanguageHandler()
    
    # Test English
    lang_info = handler.detect_language(SAMPLE_CONTRACT)
    print(f"✓ Primary language: {lang_info.primary_language}")
    print(f"✓ Confidence: {lang_info.confidence:.2%}")
    print(f"✓ Is multilingual: {lang_info.is_multilingual}")
    
    # Test Hindi
    hindi_text = "यह अनुबंध दोनों पक्षों के बीच है। भुगतान की शर्तें निम्नलिखित हैं।"
    hindi_info = handler.detect_language(hindi_text)
    print(f"✓ Hindi detection: {hindi_info.primary_language}")
    
    # Test legal terms
    terms = handler.detect_legal_terms(SAMPLE_CONTRACT)
    print(f"✓ English legal terms: {terms['english_terms'][:5]}")
    
    return True


def test_contract_classifier():
    """Test contract classification."""
    print("\n" + "="*50)
    print("Testing Contract Classifier")
    print("="*50)
    
    classifier = ContractClassifier()
    result = classifier.classify(SAMPLE_CONTRACT)
    
    print(f"✓ Contract type: {result.contract_type}")
    print(f"✓ Confidence: {result.confidence:.2%}")
    print(f"✓ Secondary types: {result.secondary_types[:3]}")
    print(f"✓ Reasoning: {result.reasoning[:100]}...")
    
    # Get type info
    type_info = classifier.get_contract_type_info(result.contract_type)
    print(f"✓ Key clauses for type: {type_info.get('key_clauses', [])[:5]}")
    
    return True


def test_risk_analyzer():
    """Test risk analysis."""
    print("\n" + "="*50)
    print("Testing Risk Analyzer")
    print("="*50)
    
    analyzer = RiskAnalyzer()
    result = analyzer.analyze_contract(SAMPLE_CONTRACT)
    
    print(f"✓ Overall risk score: {result.overall_score:.2%}")
    print(f"✓ Overall risk level: {result.overall_level.value}")
    print(f"✓ Risk distribution: {result.risk_distribution}")
    print(f"✓ High-risk clauses: {len(result.high_risk_clauses)}")
    
    print(f"✓ Priority issues:")
    for issue in result.priority_issues[:3]:
        print(f"  - {issue}")
    
    print(f"✓ Recommendations:")
    for rec in result.recommendations[:3]:
        print(f"  - {rec}")
    
    return True


def test_compliance_checker():
    """Test compliance checking."""
    print("\n" + "="*50)
    print("Testing Compliance Checker")
    print("="*50)
    
    checker = ComplianceChecker()
    result = checker.check_compliance(SAMPLE_CONTRACT, "Employment Agreement")
    
    print(f"✓ Overall status: {result.overall_status.value}")
    print(f"✓ Issues found: {len(result.issues)}")
    print(f"✓ Compliant areas: {len(result.compliant_areas)}")
    print(f"✓ Missing requirements: {result.missing_requirements[:3]}")
    print(f"✓ Laws checked: {result.laws_checked}")
    
    return True


def test_similarity_matcher():
    """Test template comparison."""
    print("\n" + "="*50)
    print("Testing Similarity Matcher")
    print("="*50)
    
    matcher = SimilarityMatcher()
    result = matcher.compare_to_template(SAMPLE_CONTRACT, "Employment Agreement")
    
    print(f"✓ Overall similarity: {result.overall_similarity:.2%}")
    print(f"✓ Quality score: {result.quality_score:.2%}")
    print(f"✓ Missing clauses: {result.missing_clauses[:5]}")
    print(f"✓ Matched clauses: {len(result.matched_clauses)}")
    
    return True


def test_document_extractor():
    """Test document extraction."""
    print("\n" + "="*50)
    print("Testing Document Extractor")
    print("="*50)
    
    extractor = DocumentExtractor()
    
    # Test TXT extraction
    txt_content = SAMPLE_CONTRACT.encode('utf-8')
    result = extractor.extract(file_content=txt_content, filename="test.txt")
    
    print(f"✓ Extraction success: {result.extraction_success}")
    print(f"✓ Word count: {result.word_count}")
    print(f"✓ File hash: {result.file_hash}")
    
    # Test validation
    is_valid, message = extractor.validate_file(txt_content, "test.txt")
    print(f"✓ Validation: {is_valid} - {message}")
    
    return True


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("CONTRACT ANALYSIS SYSTEM - TEST SUITE")
    print("="*60)
    
    tests = [
        ("Preprocessor", test_preprocessor),
        ("Entity Extractor", test_entity_extractor),
        ("Clause Parser", test_clause_parser),
        ("Language Detector", test_language_detector),
        ("Contract Classifier", test_contract_classifier),
        ("Risk Analyzer", test_risk_analyzer),
        ("Compliance Checker", test_compliance_checker),
        ("Similarity Matcher", test_similarity_matcher),
        ("Document Extractor", test_document_extractor),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success, None))
        except Exception as e:
            results.append((name, False, str(e)))
            print(f"✗ Error: {e}")
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    for name, success, error in results:
        status = "✓ PASS" if success else f"✗ FAIL: {error}"
        print(f"  {name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("="*60)
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

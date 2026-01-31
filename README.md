# Contract Analysis & Risk Assessment Bot 🔍⚖️

A sophisticated GenAI-powered legal assistant designed for Indian SMEs to understand complex contracts, identify legal risks, and receive actionable advice in plain language.

## Features

### Core Legal NLP Capabilities
- **Contract Type Classification**: Automatically identifies employment agreements, vendor contracts, lease agreements, partnership deeds, and service contracts
- **Clause & Sub-Clause Extraction**: Intelligent parsing of contract structure
- **Named Entity Recognition**: Extracts parties, dates, jurisdiction, liabilities, and amounts
- **Obligation/Right/Prohibition Identification**: Categorizes contractual terms
- **Risk & Compliance Detection**: Flags potential legal issues
- **Ambiguity Detection**: Identifies vague or unclear language
- **Clause Similarity Matching**: Compares against standard templates

### Risk Assessment
- Clause-level risk scores (Low/Medium/High)
- Contract-level composite risk score
- Detection of:
  - Penalty Clauses
  - Indemnity Clauses
  - Unilateral Termination Terms
  - Arbitration & Jurisdiction Terms
  - Auto-Renewal & Lock-in Periods
  - Non-compete & IP Transfer Clauses

### User-Facing Outputs
- Simplified contract summary
- Clause-by-clause plain-language explanation
- Unfavorable clause highlighting
- Suggested renegotiation alternatives
- SME-friendly contract templates
- PDF export for legal review

### Multilingual Support
- English and Hindi contract parsing
- Hindi→English normalization for NLP
- Output summaries in simple business English

## Installation

```bash
# Clone the repository
cd contract-tool

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_lg

# Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('averaged_perceptron_tagger')"

# Set up environment variables
cp .env.example .env
# Edit .env and add your OpenAI API key
```

## Usage

```bash
# Run the Streamlit application
streamlit run app.py
```

## Project Structure

```
contract-tool/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── config/
│   └── settings.py            # Application configuration
├── src/
│   ├── __init__.py
│   ├── nlp/
│   │   ├── __init__.py
│   │   ├── preprocessor.py    # Text preprocessing
│   │   ├── entity_extractor.py # NER for legal entities
│   │   ├── clause_parser.py   # Clause extraction
│   │   └── language_detector.py # Multilingual support
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── contract_classifier.py # Contract type classification
│   │   ├── risk_analyzer.py   # Risk scoring engine
│   │   ├── compliance_checker.py # Compliance validation
│   │   └── similarity_matcher.py # Template matching
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── gpt_client.py      # GPT-5 integration
│   │   ├── prompts.py         # Prompt templates
│   │   └── response_parser.py # LLM response handling
│   ├── document/
│   │   ├── __init__.py
│   │   ├── extractor.py       # PDF/DOCX text extraction
│   │   └── pdf_generator.py   # Report generation
│   └── utils/
│       ├── __init__.py
│       ├── audit_logger.py    # Audit trail management
│       └── helpers.py         # Utility functions
├── templates/
│   └── contracts/             # Standard contract templates
├── data/
│   ├── knowledge_base/        # SME contract knowledge
│   └── audit_logs/            # JSON audit logs
└── tests/
    └── sample_contracts/      # Test contracts
```

## Configuration

Create a `.env` file with:
```
OPENAI_API_KEY=your_api_key_here
```

## Tech Stack

- **LLM**: GPT-5 (OpenAI API)
- **NLP**: spaCy, NLTK
- **UI**: Streamlit
- **Document Processing**: PyPDF2, python-docx, pdfplumber
- **PDF Generation**: FPDF2, ReportLab

## License

MIT License - For educational and hackathon purposes.

## Authors

Built for Data Science Hackathon 2026

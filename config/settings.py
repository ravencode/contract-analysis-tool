"""
Application Configuration Settings
Contract Analysis & Risk Assessment Bot
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
TEMPLATES_DIR = BASE_DIR / "templates"
AUDIT_LOG_DIR = DATA_DIR / "audit_logs"
KNOWLEDGE_BASE_DIR = DATA_DIR / "knowledge_base"
UPLOADS_DIR = DATA_DIR / "uploads"

# Create directories if they don't exist
for directory in [DATA_DIR, AUDIT_LOG_DIR, KNOWLEDGE_BASE_DIR, UPLOADS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = "gpt-5-mini"
OPENAI_MAX_TOKENS = 4096
OPENAI_TEMPERATURE = 0.3  # Lower temperature for legal analysis accuracy

# Contract Types
CONTRACT_TYPES = [
    "Employment Agreement",
    "Vendor Contract",
    "Lease Agreement",
    "Partnership Deed",
    "Service Contract",
    "Non-Disclosure Agreement",
    "Consultancy Agreement",
    "Supply Agreement",
    "Franchise Agreement",
    "Joint Venture Agreement"
]

# Risk Categories
RISK_CATEGORIES = {
    "penalty_clause": {
        "name": "Penalty Clauses",
        "keywords": ["penalty", "liquidated damages", "fine", "forfeit", "punitive"],
        "weight": 0.15
    },
    "indemnity_clause": {
        "name": "Indemnity Clauses",
        "keywords": ["indemnify", "indemnification", "hold harmless", "defend", "indemnity"],
        "weight": 0.15
    },
    "termination_clause": {
        "name": "Unilateral Termination",
        "keywords": ["terminate", "termination", "cancel", "revoke", "end agreement"],
        "weight": 0.12
    },
    "arbitration_clause": {
        "name": "Arbitration & Jurisdiction",
        "keywords": ["arbitration", "jurisdiction", "dispute resolution", "governing law", "venue"],
        "weight": 0.10
    },
    "auto_renewal": {
        "name": "Auto-Renewal & Lock-in",
        "keywords": ["auto-renewal", "automatic renewal", "lock-in", "minimum term", "commitment period"],
        "weight": 0.10
    },
    "non_compete": {
        "name": "Non-Compete Clauses",
        "keywords": ["non-compete", "non-competition", "restrictive covenant", "compete"],
        "weight": 0.12
    },
    "ip_transfer": {
        "name": "IP Transfer Clauses",
        "keywords": ["intellectual property", "ip rights", "patent", "copyright", "trademark", "ownership transfer"],
        "weight": 0.13
    },
    "liability_limitation": {
        "name": "Liability Limitation",
        "keywords": ["limitation of liability", "cap on liability", "maximum liability", "exclude liability"],
        "weight": 0.08
    },
    "confidentiality": {
        "name": "Confidentiality & NDA",
        "keywords": ["confidential", "confidentiality", "non-disclosure", "proprietary", "trade secret"],
        "weight": 0.05
    }
}

# Risk Score Thresholds
RISK_THRESHOLDS = {
    "low": (0, 0.33),
    "medium": (0.33, 0.66),
    "high": (0.66, 1.0)
}

# Entity Types for NER
ENTITY_TYPES = [
    "PARTY",           # Contract parties
    "DATE",            # Important dates
    "AMOUNT",          # Financial amounts
    "DURATION",        # Time periods
    "JURISDICTION",    # Legal jurisdiction
    "OBLIGATION",      # Contractual obligations
    "RIGHT",           # Contractual rights
    "DELIVERABLE",     # Deliverables/milestones
    "PENALTY",         # Penalty amounts
    "NOTICE_PERIOD"    # Notice periods
]

# Supported Languages
SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "Hindi"
}

# File Upload Settings
ALLOWED_EXTENSIONS = [".pdf", ".docx", ".doc", ".txt"]
MAX_FILE_SIZE_MB = 10

# Clause Categories
CLAUSE_CATEGORIES = [
    "Definitions",
    "Scope of Work",
    "Payment Terms",
    "Delivery & Performance",
    "Warranties & Representations",
    "Indemnification",
    "Limitation of Liability",
    "Confidentiality",
    "Intellectual Property",
    "Term & Termination",
    "Dispute Resolution",
    "Force Majeure",
    "Assignment",
    "Notices",
    "Governing Law",
    "Entire Agreement",
    "Amendment",
    "Severability",
    "Waiver",
    "Miscellaneous"
]

# Indian Law Compliance Checkpoints
INDIAN_LAW_COMPLIANCE = {
    "stamp_duty": "Contract should mention stamp duty applicability",
    "jurisdiction": "Jurisdiction should be within India for enforceability",
    "arbitration_act": "Arbitration clauses should comply with Arbitration and Conciliation Act, 1996",
    "contract_act": "Terms should not violate Indian Contract Act, 1872",
    "it_act": "Digital contracts should comply with IT Act, 2000",
    "consumer_protection": "B2C contracts should comply with Consumer Protection Act, 2019",
    "competition_act": "Non-compete clauses should comply with Competition Act, 2002",
    "labour_laws": "Employment contracts should comply with applicable labour laws"
}

# UI Configuration
STREAMLIT_CONFIG = {
    "page_title": "Contract Analysis Bot",
    "page_icon": "⚖️",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Color Scheme for Risk Visualization
RISK_COLORS = {
    "low": "#28a745",      # Green
    "medium": "#ffc107",   # Yellow/Amber
    "high": "#dc3545"      # Red
}

# Audit Log Settings
AUDIT_LOG_FORMAT = {
    "timestamp": True,
    "user_session": True,
    "action_type": True,
    "contract_hash": True,
    "analysis_results": True
}

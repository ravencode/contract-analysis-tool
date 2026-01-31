"""
Contract Analysis & Risk Assessment Bot
Main Streamlit Application
"""

import streamlit as st
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from datetime import datetime
import json
import plotly.express as px
import plotly.graph_objects as go

# Import project modules
from config.settings import STREAMLIT_CONFIG, RISK_COLORS, CONTRACT_TYPES
from src.document.extractor import DocumentExtractor
from src.nlp.preprocessor import TextPreprocessor
from src.nlp.entity_extractor import LegalEntityExtractor
from src.nlp.clause_parser import ClauseParser
from src.nlp.language_detector import LanguageHandler
from src.analysis.contract_classifier import ContractClassifier
from src.analysis.risk_analyzer import RiskAnalyzer, RiskLevel
from src.analysis.compliance_checker import ComplianceChecker
from src.analysis.similarity_matcher import SimilarityMatcher
from src.llm.gpt_client import GPTClient
from src.llm.response_parser import ResponseParser
from src.document.pdf_generator import PDFReportGenerator
from src.utils.audit_logger import AuditLogger
from src.utils.helpers import format_risk_score, format_compliance_status, create_summary_stats

# Page configuration
st.set_page_config(
    page_title=STREAMLIT_CONFIG["page_title"],
    page_icon=STREAMLIT_CONFIG["page_icon"],
    layout=STREAMLIT_CONFIG["layout"],
    initial_sidebar_state=STREAMLIT_CONFIG["initial_sidebar_state"]
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1e3a5f;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .risk-high {
        background-color: #ffebee;
        border-left: 4px solid #f44336;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .risk-medium {
        background-color: #fff8e1;
        border-left: 4px solid #ff9800;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .risk-low {
        background-color: #e8f5e9;
        border-left: 4px solid #4caf50;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f6;
        border-radius: 4px;
        padding: 10px 20px;
    }
    .clause-card {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        background: #fafafa;
    }
    .entity-tag {
        display: inline-block;
        background: #e3f2fd;
        padding: 4px 12px;
        border-radius: 16px;
        margin: 4px;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables."""
    if 'contract_text' not in st.session_state:
        st.session_state.contract_text = None
    if 'contract_filename' not in st.session_state:
        st.session_state.contract_filename = None
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = {}
    if 'audit_logger' not in st.session_state:
        st.session_state.audit_logger = AuditLogger()
    if 'gpt_client' not in st.session_state:
        st.session_state.gpt_client = GPTClient()


def render_sidebar():
    """Render the sidebar with navigation and settings."""
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/contract.png", width=80)
        st.markdown("## ⚖️ Contract Analysis Bot")
        st.markdown("---")
        
        # Navigation
        page = st.radio(
            "Navigation",
            ["📤 Upload Contract", "📊 Analysis Dashboard", "📋 Clause Analysis", 
             "⚠️ Risk Assessment", "✅ Compliance Check", "📝 Templates", 
             "❓ Ask Questions", "📁 Export Reports"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Current contract info
        if st.session_state.contract_text:
            st.markdown("---")
            st.markdown("### 📄 Current Contract")
            st.info(f"**{st.session_state.contract_filename}**")
            stats = create_summary_stats(st.session_state.contract_text)
            st.caption(f"📝 {stats['word_count']:,} words")
            st.caption(f"⏱️ ~{stats['reading_time_minutes']} min read")
        
        return page


def render_upload_page():
    """Render the contract upload page."""
    st.markdown('<h1 class="main-header">📤 Upload Your Contract</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Upload a contract document for comprehensive AI-powered analysis</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Choose a contract file",
            type=['pdf', 'docx', 'doc', 'txt'],
            help="Supported formats: PDF, DOCX, DOC, TXT (Max 10MB)"
        )
        
        if uploaded_file:
            with st.spinner("Extracting text from document..."):
                extractor = DocumentExtractor()
                file_content = uploaded_file.read()
                
                result = extractor.extract(
                    file_content=file_content,
                    filename=uploaded_file.name
                )
                
                if result.extraction_success:
                    st.session_state.contract_text = result.text
                    st.session_state.contract_filename = result.filename
                    st.session_state.analysis_results = {}  # Reset analysis
                    
                    # Log upload
                    st.session_state.audit_logger.log_upload(
                        filename=result.filename,
                        file_size=len(file_content),
                        file_type=result.file_type,
                        contract_text=result.text
                    )
                    
                    st.success(f"✅ Successfully extracted text from **{result.filename}**")
                    
                    # Show extraction stats
                    col_a, col_b, col_c = st.columns(3)
                    col_a.metric("Pages", result.page_count)
                    col_b.metric("Words", f"{result.word_count:,}")
                    col_c.metric("Characters", f"{result.char_count:,}")
                    
                    # Language detection
                    lang_handler = LanguageHandler()
                    lang_info = lang_handler.detect_language(result.text)
                    
                    if lang_info.is_multilingual:
                        st.info(f"🌐 Multilingual document detected: {lang_info.language_distribution}")
                    
                    # Preview
                    with st.expander("📖 Preview Extracted Text"):
                        st.text_area("Contract Text", result.text[:5000] + "..." if len(result.text) > 5000 else result.text, height=300)
                else:
                    st.error(f"❌ Failed to extract text: {result.error_message}")
    
    with col2:
        st.markdown("### 📋 Supported Formats")
        st.markdown("""
        - **PDF** - Text-based PDFs
        - **DOCX** - Microsoft Word
        - **DOC** - Legacy Word
        - **TXT** - Plain text
        """)
        
        st.markdown("### 🔒 Privacy")
        st.markdown("""
        - Documents are processed locally
        - Only text is sent to AI for analysis
        - Audit logs maintain confidentiality
        """)
        
        if st.session_state.contract_text:
            if st.button("🚀 Start Analysis", type="primary", use_container_width=True):
                st.switch_page = "📊 Analysis Dashboard"
                st.rerun()


def render_analysis_dashboard():
    """Render the main analysis dashboard."""
    if not st.session_state.contract_text:
        st.warning("⚠️ Please upload a contract first!")
        return
    
    st.markdown('<h1 class="main-header">📊 Analysis Dashboard</h1>', unsafe_allow_html=True)
    
    # Run analysis if not already done
    if 'classification' not in st.session_state.analysis_results:
        with st.spinner("🔍 Analyzing contract..."):
            run_full_analysis()
    
    results = st.session_state.analysis_results
    
    # Top metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        contract_type = results.get('classification', {}).get('contract_type', 'Unknown')
        st.metric("Contract Type", contract_type)
    
    with col2:
        risk_score = results.get('risk', {}).get('overall_score', 0.5)
        risk_level = results.get('risk', {}).get('overall_level', 'medium')
        if hasattr(risk_level, 'value'):
            risk_level = risk_level.value
        st.metric("Risk Score", f"{risk_score:.0%}", delta=risk_level.upper())
    
    with col3:
        compliance_status = results.get('compliance', {}).get('overall_status', 'unknown')
        if hasattr(compliance_status, 'value'):
            compliance_status = compliance_status.value
        st.metric("Compliance", compliance_status.replace('_', ' ').title())
    
    with col4:
        clause_count = len(results.get('clauses', []))
        st.metric("Clauses Found", clause_count)
    
    st.markdown("---")
    
    # Two column layout
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        # Contract Summary
        st.markdown("### 📝 Contract Summary")
        
        if 'summary' in results and results['summary']:
            st.markdown(results['summary'])
        else:
            # Generate summary using GPT if available
            if st.session_state.gpt_client.is_configured():
                with st.spinner("Generating summary..."):
                    response = st.session_state.gpt_client.generate_summary(
                        st.session_state.contract_text
                    )
                    if response.success:
                        results['summary'] = response.content
                        st.markdown(response.content)
                    else:
                        st.warning("Could not generate AI summary. Showing basic analysis.")
                        show_basic_summary(results)
            else:
                show_basic_summary(results)
        
        # Key Entities
        st.markdown("### 🏷️ Key Information Extracted")
        entities = results.get('entities', {})
        
        if entities:
            tabs = st.tabs(["Parties", "Dates", "Amounts", "Obligations"])
            
            with tabs[0]:
                parties = entities.get('parties', [])
                if parties:
                    for party in parties[:5]:
                        st.markdown(f"<span class='entity-tag'>👤 {party.value if hasattr(party, 'value') else party}</span>", unsafe_allow_html=True)
                else:
                    st.caption("No parties identified")
            
            with tabs[1]:
                dates = entities.get('dates', [])
                if dates:
                    for date in dates[:5]:
                        st.markdown(f"<span class='entity-tag'>📅 {date.value if hasattr(date, 'value') else date}</span>", unsafe_allow_html=True)
                else:
                    st.caption("No dates identified")
            
            with tabs[2]:
                amounts = entities.get('amounts', [])
                if amounts:
                    for amount in amounts[:5]:
                        st.markdown(f"<span class='entity-tag'>💰 {amount.value if hasattr(amount, 'value') else amount}</span>", unsafe_allow_html=True)
                else:
                    st.caption("No amounts identified")
            
            with tabs[3]:
                obligations = entities.get('obligations', [])
                if obligations:
                    for obl in obligations[:5]:
                        st.markdown(f"- {obl.value if hasattr(obl, 'value') else obl}")
                else:
                    st.caption("No obligations identified")
    
    with col_right:
        # Risk Distribution Chart
        st.markdown("### 📊 Risk Distribution")
        
        risk_dist = results.get('risk', {}).get('risk_distribution', {})
        if risk_dist:
            # Filter out zero values
            filtered_dist = {k: v for k, v in risk_dist.items() if v > 0}
            
            if filtered_dist:
                # Map risk levels to colors
                color_map = {
                    'low': '#4caf50',
                    'medium': '#ff9800', 
                    'high': '#f44336',
                    'critical': '#9c27b0'
                }
                labels = list(filtered_dist.keys())
                values = list(filtered_dist.values())
                colors = [color_map.get(label.lower(), '#999999') for label in labels]
                
                fig = go.Figure(data=[go.Pie(
                    labels=[l.capitalize() for l in labels],
                    values=values,
                    marker_colors=colors,
                    hole=0.4,
                    textinfo='label+percent',
                    textposition='auto'
                )])
                fig.update_layout(
                    showlegend=True,
                    height=250,
                    margin=dict(l=20, r=20, t=20, b=20)
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No risk data available for visualization.")
        else:
            st.info("No risk distribution data available.")
        
        # Priority Issues
        st.markdown("### ⚠️ Priority Issues")
        priority_issues = results.get('risk', {}).get('priority_issues', [])
        
        if priority_issues:
            for issue in priority_issues[:5]:
                st.markdown(f"""
                <div class="risk-high">
                    ⚠️ {issue}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("No critical issues found!")


def show_basic_summary(results):
    """Show basic summary without GPT."""
    classification = results.get('classification', {})
    entities = results.get('entities', {})
    
    st.markdown(f"""
    **Contract Type:** {classification.get('contract_type', 'Unknown')}
    
    **Parties Involved:** {', '.join([p.value if hasattr(p, 'value') else str(p) for p in entities.get('parties', [])[:3]]) or 'Not identified'}
    
    **Key Dates:** {', '.join([d.value if hasattr(d, 'value') else str(d) for d in entities.get('dates', [])[:3]]) or 'Not identified'}
    
    **Jurisdiction:** {', '.join([j.value if hasattr(j, 'value') else str(j) for j in entities.get('jurisdictions', [])[:2]]) or 'Not specified'}
    """)


def run_full_analysis():
    """Run comprehensive contract analysis."""
    text = st.session_state.contract_text
    results = {}
    
    # 1. Classification
    classifier = ContractClassifier()
    classification = classifier.classify(text)
    results['classification'] = {
        'contract_type': classification.contract_type,
        'confidence': classification.confidence,
        'reasoning': classification.reasoning
    }
    
    # 2. Entity Extraction
    entity_extractor = LegalEntityExtractor()
    entities = entity_extractor.extract_all_entities(text)
    results['entities'] = entities
    
    # 3. Clause Parsing
    clause_parser = ClauseParser()
    clauses = clause_parser.parse_clauses(text)
    results['clauses'] = clauses
    
    # 4. Risk Analysis
    risk_analyzer = RiskAnalyzer()
    
    # Prepare clauses for risk analysis
    clause_dicts = []
    for clause in clauses:
        clause_dicts.append({
            'id': clause.clause_id,
            'type': clause.clause_type.value if hasattr(clause.clause_type, 'value') else str(clause.clause_type),
            'text': clause.content
        })
    
    risk_result = risk_analyzer.analyze_contract(text, clause_dicts if clause_dicts else None)
    results['risk'] = {
        'overall_score': risk_result.overall_score,
        'overall_level': risk_result.overall_level,
        'risk_distribution': risk_result.risk_distribution,
        'priority_issues': risk_result.priority_issues,
        'recommendations': risk_result.recommendations,
        'clause_risks': risk_result.clause_risks
    }
    
    # 5. Compliance Check
    compliance_checker = ComplianceChecker()
    compliance = compliance_checker.check_compliance(text, classification.contract_type)
    results['compliance'] = {
        'overall_status': compliance.overall_status,
        'issues': compliance.issues,
        'compliant_areas': compliance.compliant_areas,
        'missing_requirements': compliance.missing_requirements,
        'recommendations': compliance.recommendations,
        'laws_checked': compliance.laws_checked
    }
    
    # 6. Template Comparison
    similarity_matcher = SimilarityMatcher()
    template_comparison = similarity_matcher.compare_to_template(text, classification.contract_type)
    results['template_comparison'] = {
        'overall_similarity': template_comparison.overall_similarity,
        'quality_score': template_comparison.quality_score,
        'missing_clauses': template_comparison.missing_clauses,
        'recommendations': template_comparison.recommendations
    }
    
    # Log analysis
    st.session_state.audit_logger.log_analysis(
        filename=st.session_state.contract_filename,
        contract_text=text,
        analysis_type="full_analysis",
        results={'risk_score': risk_result.overall_score}
    )
    
    st.session_state.analysis_results = results


def render_clause_analysis():
    """Render clause-by-clause analysis page."""
    if not st.session_state.contract_text:
        st.warning("⚠️ Please upload a contract first!")
        return
    
    st.markdown('<h1 class="main-header">📋 Clause-by-Clause Analysis</h1>', unsafe_allow_html=True)
    
    if 'clauses' not in st.session_state.analysis_results:
        with st.spinner("Parsing clauses..."):
            run_full_analysis()
    
    clauses = st.session_state.analysis_results.get('clauses', [])
    clause_risks = st.session_state.analysis_results.get('risk', {}).get('clause_risks', [])
    
    if not clauses:
        st.info("No distinct clauses identified. The document may not follow standard clause structure.")
        return
    
    # Filter options
    col1, col2 = st.columns([1, 1])
    with col1:
        risk_filter = st.multiselect(
            "Filter by Risk Level",
            ["Low", "Medium", "High", "Critical"],
            default=["High", "Critical"]
        )
    with col2:
        search_term = st.text_input("Search clauses", placeholder="Enter keyword...")
    
    st.markdown("---")
    
    # Display clauses
    for i, clause in enumerate(clauses):
        # Find corresponding risk
        clause_risk = None
        for cr in clause_risks:
            if cr.clause_id == clause.clause_id:
                clause_risk = cr
                break
        
        risk_level = clause_risk.risk_level.value if clause_risk else "low"
        
        # Apply filters
        if risk_filter and risk_level.title() not in risk_filter:
            continue
        
        if search_term and search_term.lower() not in clause.content.lower():
            continue
        
        # Determine styling
        risk_class = f"risk-{risk_level}"
        
        with st.expander(f"📄 {clause.title or f'Clause {i+1}'} | Risk: {risk_level.upper()}", expanded=False):
            st.markdown(f"""
            <div class="{risk_class}">
                <strong>Type:</strong> {clause.clause_type.value if hasattr(clause.clause_type, 'value') else clause.clause_type}<br>
                <strong>Risk Score:</strong> {clause_risk.risk_score if clause_risk else 'N/A'}
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("**Content:**")
            st.markdown(clause.content[:1000] + "..." if len(clause.content) > 1000 else clause.content)
            
            if clause_risk and clause_risk.red_flags:
                st.markdown("**🚩 Red Flags:**")
                for flag in clause_risk.red_flags:
                    st.markdown(f"- {flag}")
            
            if clause_risk and clause_risk.mitigation_suggestions:
                st.markdown("**💡 Suggestions:**")
                for suggestion in clause_risk.mitigation_suggestions:
                    st.markdown(f"- {suggestion}")
            
            # GPT explanation button
            if st.session_state.gpt_client.is_configured():
                if st.button(f"🤖 Explain in Simple Terms", key=f"explain_{i}"):
                    with st.spinner("Generating explanation..."):
                        response = st.session_state.gpt_client.explain_clause(
                            clause.content,
                            clause.clause_type.value if hasattr(clause.clause_type, 'value') else str(clause.clause_type)
                        )
                        if response.success:
                            st.markdown("---")
                            st.markdown("### Plain Language Explanation")
                            st.markdown(response.content)


def render_risk_assessment():
    """Render risk assessment page."""
    if not st.session_state.contract_text:
        st.warning("⚠️ Please upload a contract first!")
        return
    
    st.markdown('<h1 class="main-header">⚠️ Risk Assessment</h1>', unsafe_allow_html=True)
    
    if 'risk' not in st.session_state.analysis_results:
        with st.spinner("Analyzing risks..."):
            run_full_analysis()
    
    risk_data = st.session_state.analysis_results.get('risk', {})
    
    # Overall Risk Score
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        overall_score = risk_data.get('overall_score', 0.5)
        overall_level = risk_data.get('overall_level', 'medium')
        if hasattr(overall_level, 'value'):
            overall_level = overall_level.value
        
        # Risk gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=overall_score * 100,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Overall Risk Score"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': RISK_COLORS.get(overall_level, '#ff9800')},
                'steps': [
                    {'range': [0, 33], 'color': '#e8f5e9'},
                    {'range': [33, 66], 'color': '#fff8e1'},
                    {'range': [66, 100], 'color': '#ffebee'}
                ],
                'threshold': {
                    'line': {'color': 'red', 'width': 4},
                    'thickness': 0.75,
                    'value': overall_score * 100
                }
            }
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Risk Categories
    st.markdown("### 📊 Risk by Category")
    
    clause_risks = risk_data.get('clause_risks', [])
    
    if clause_risks:
        # Group by category
        category_scores = {}
        for cr in clause_risks:
            cat = cr.category
            if cat not in category_scores:
                category_scores[cat] = []
            category_scores[cat].append(cr.risk_score)
        
        # Average scores
        avg_scores = {cat: sum(scores)/len(scores) for cat, scores in category_scores.items()}
        
        # Bar chart
        fig = px.bar(
            x=list(avg_scores.keys()),
            y=list(avg_scores.values()),
            color=list(avg_scores.values()),
            color_continuous_scale=['green', 'yellow', 'red'],
            labels={'x': 'Category', 'y': 'Risk Score'}
        )
        fig.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    # Priority Issues
    st.markdown("### 🚨 Priority Issues")
    
    priority_issues = risk_data.get('priority_issues', [])
    
    if priority_issues:
        for issue in priority_issues:
            st.markdown(f"""
            <div class="risk-high">
                ⚠️ <strong>{issue}</strong>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("✅ No critical issues identified!")
    
    # Recommendations
    st.markdown("### 💡 Recommendations")
    
    recommendations = risk_data.get('recommendations', [])
    
    for rec in recommendations:
        if rec.startswith('⚠️') or rec.startswith('CRITICAL'):
            st.error(rec)
        elif rec.startswith('⚡') or rec.startswith('HIGH'):
            st.warning(rec)
        elif rec.startswith('✅'):
            st.success(rec)
        else:
            st.info(rec)


def render_compliance_check():
    """Render compliance check page."""
    if not st.session_state.contract_text:
        st.warning("⚠️ Please upload a contract first!")
        return
    
    st.markdown('<h1 class="main-header">✅ Compliance Check</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Checking compliance with Indian laws and regulations</p>', unsafe_allow_html=True)
    
    if 'compliance' not in st.session_state.analysis_results:
        with st.spinner("Checking compliance..."):
            run_full_analysis()
    
    compliance_data = st.session_state.analysis_results.get('compliance', {})
    
    # Overall Status
    status = compliance_data.get('overall_status', 'unknown')
    if hasattr(status, 'value'):
        status = status.value
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if status == 'compliant':
            st.success(f"### ✅ {status.replace('_', ' ').title()}")
        elif status == 'partially_compliant':
            st.warning(f"### ⚠️ {status.replace('_', ' ').title()}")
        else:
            st.error(f"### ❌ {status.replace('_', ' ').title()}")
    
    with col2:
        issues = compliance_data.get('issues', [])
        st.metric("Issues Found", len(issues))
    
    with col3:
        laws_checked = compliance_data.get('laws_checked', [])
        st.metric("Laws Checked", len(laws_checked))
    
    st.markdown("---")
    
    # Laws Checked
    st.markdown("### 📚 Laws Checked")
    
    for law in laws_checked:
        st.markdown(f"- ✓ {law}")
    
    # Issues
    if issues:
        st.markdown("### ⚠️ Compliance Issues")
        
        for issue in issues:
            severity = issue.severity if hasattr(issue, 'severity') else 'Medium'
            law_ref = issue.law_reference if hasattr(issue, 'law_reference') else 'Unknown'
            description = issue.issue_description if hasattr(issue, 'issue_description') else str(issue)
            
            severity_class = 'risk-high' if severity in ['High', 'Critical'] else 'risk-medium'
            
            st.markdown(f"""
            <div class="{severity_class}">
                <strong>[{law_ref}]</strong> - {severity}<br>
                {description}
            </div>
            """, unsafe_allow_html=True)
    
    # Missing Requirements
    missing = compliance_data.get('missing_requirements', [])
    if missing:
        st.markdown("### 📋 Missing Requirements")
        for req in missing:
            st.markdown(f"- ⚠️ {req}")
    
    # Recommendations
    recommendations = compliance_data.get('recommendations', [])
    if recommendations:
        st.markdown("### 💡 Recommendations")
        for rec in recommendations:
            st.info(rec)


def render_templates():
    """Render contract templates page."""
    st.markdown('<h1 class="main-header">📝 Contract Templates</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">SME-friendly standard contract templates</p>', unsafe_allow_html=True)
    
    # Template selection
    template_type = st.selectbox(
        "Select Contract Type",
        CONTRACT_TYPES
    )
    
    # Get template
    similarity_matcher = SimilarityMatcher()
    templates = similarity_matcher.get_template_for_type(template_type)
    
    if templates:
        st.markdown(f"### 📄 {template_type} Template Clauses")
        
        for clause_name, clause_info in templates.items():
            with st.expander(f"📌 {clause_name.replace('_', ' ').title()}", expanded=False):
                st.markdown("**Standard Template:**")
                st.code(clause_info['template'], language=None)
                
                if clause_info.get('required'):
                    st.markdown("✅ **Required clause**")
                else:
                    st.markdown("ℹ️ *Optional clause*")
                
                st.markdown("**Keywords:**")
                st.markdown(", ".join(clause_info.get('keywords', [])))
    
    # Download template
    st.markdown("---")
    st.markdown("### 📥 Download Full Template")
    
    if st.button("Generate Template Document"):
        # Generate a basic template
        template_text = f"# {template_type}\n\n"
        template_text += f"Date: {datetime.now().strftime('%d %B %Y')}\n\n"
        template_text += "---\n\n"
        
        for clause_name, clause_info in templates.items():
            template_text += f"## {clause_name.replace('_', ' ').title()}\n\n"
            template_text += f"{clause_info['template']}\n\n"
        
        st.download_button(
            label="📄 Download Template (TXT)",
            data=template_text,
            file_name=f"{template_type.lower().replace(' ', '_')}_template.txt",
            mime="text/plain"
        )


def render_ask_questions():
    """Render the Q&A page."""
    if not st.session_state.contract_text:
        st.warning("⚠️ Please upload a contract first!")
        return
    
    st.markdown('<h1 class="main-header">❓ Ask Questions</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Ask any question about your contract</p>', unsafe_allow_html=True)
    
    if not st.session_state.gpt_client.is_configured():
        st.warning("⚠️ Please configure your OpenAI API key in Settings to use this feature.")
        return
    
    # Suggested questions
    st.markdown("### 💡 Suggested Questions")
    
    suggested = [
        "What are the main obligations of each party?",
        "What are the termination conditions?",
        "Are there any penalty clauses?",
        "What is the dispute resolution mechanism?",
        "What are the payment terms?",
        "Is there a non-compete clause?"
    ]
    
    cols = st.columns(3)
    for i, q in enumerate(suggested):
        with cols[i % 3]:
            if st.button(q, key=f"suggested_{i}"):
                st.session_state.current_question = q
    
    st.markdown("---")
    
    # Custom question
    question = st.text_input(
        "Your Question",
        value=st.session_state.get('current_question', ''),
        placeholder="Ask anything about the contract..."
    )
    
    if st.button("🔍 Get Answer", type="primary"):
        if question:
            with st.spinner("Analyzing contract to answer your question..."):
                response = st.session_state.gpt_client.custom_query(
                    st.session_state.contract_text,
                    question
                )
                
                if response.success:
                    st.markdown("### 📝 Answer")
                    st.markdown(response.content)
                    
                    # Log query
                    st.session_state.audit_logger.log_query(
                        filename=st.session_state.contract_filename,
                        contract_text=st.session_state.contract_text,
                        query=question,
                        response_summary=response.content[:200]
                    )
                else:
                    st.error(f"Error: {response.error}")
        else:
            st.warning("Please enter a question.")


def render_export_reports():
    """Render export reports page."""
    if not st.session_state.contract_text:
        st.warning("⚠️ Please upload a contract first!")
        return
    
    st.markdown('<h1 class="main-header">📁 Export Reports</h1>', unsafe_allow_html=True)
    
    if not st.session_state.analysis_results:
        st.warning("Please run analysis first from the Dashboard.")
        return
    
    results = st.session_state.analysis_results
    
    st.markdown("### 📊 Available Reports")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📄 Full Analysis Report (PDF)")
        st.markdown("Comprehensive report with all analysis results")
        
        if st.button("Generate PDF Report", type="primary"):
            with st.spinner("Generating PDF..."):
                pdf_generator = PDFReportGenerator()
                
                pdf_bytes = pdf_generator.generate_analysis_report(
                    contract_info={'filename': st.session_state.contract_filename},
                    classification=results.get('classification', {}),
                    risk_analysis={
                        'overall_score': results.get('risk', {}).get('overall_score', 0.5),
                        'overall_level': results.get('risk', {}).get('overall_level', 'medium'),
                        'risk_distribution': results.get('risk', {}).get('risk_distribution', {}),
                        'priority_issues': results.get('risk', {}).get('priority_issues', [])
                    },
                    compliance={
                        'overall_status': results.get('compliance', {}).get('overall_status', 'unknown'),
                        'issues': results.get('compliance', {}).get('issues', []),
                        'laws_checked': results.get('compliance', {}).get('laws_checked', [])
                    },
                    entities=results.get('entities', {}),
                    summary=results.get('summary', ''),
                    recommendations=results.get('risk', {}).get('recommendations', [])
                )
                
                st.download_button(
                    label="Download PDF Report",
                    data=bytes(pdf_bytes),
                    file_name=f"contract_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf"
                )
                
                # Log export
                st.session_state.audit_logger.log_export(
                    filename=st.session_state.contract_filename,
                    contract_text=st.session_state.contract_text,
                    export_format="PDF",
                    export_type="Full Analysis"
                )
    
    with col2:
        st.markdown("#### 📋 JSON Data Export")
        st.markdown("Raw analysis data in JSON format")
        
        if st.button("Export JSON Data"):
            # Prepare JSON-serializable data
            export_data = {
                'filename': st.session_state.contract_filename,
                'analysis_date': datetime.now().isoformat(),
                'classification': results.get('classification', {}),
                'risk_summary': {
                    'overall_score': results.get('risk', {}).get('overall_score', 0.5),
                    'overall_level': str(results.get('risk', {}).get('overall_level', 'medium')),
                    'risk_distribution': results.get('risk', {}).get('risk_distribution', {}),
                    'priority_issues': results.get('risk', {}).get('priority_issues', [])
                },
                'compliance_summary': {
                    'status': str(results.get('compliance', {}).get('overall_status', 'unknown')),
                    'laws_checked': results.get('compliance', {}).get('laws_checked', [])
                }
            }
            
            json_str = json.dumps(export_data, indent=2, default=str)
            
            st.download_button(
                label="📥 Download JSON",
                data=json_str,
                file_name=f"contract_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    st.markdown("---")
    
    # Audit Log
    st.markdown("### 📜 Audit Trail")
    
    session_logs = st.session_state.audit_logger.get_session_logs()
    
    if session_logs:
        for log in session_logs[-10:]:  # Last 10 entries
            st.markdown(f"- **{log.get('timestamp', '')}** | {log.get('action_type', '')} | {log.get('user_action', '')}")
    else:
        st.caption("No audit entries for this session.")


def main():
    """Main application entry point."""
    init_session_state()
    
    page = render_sidebar()
    
    # Route to appropriate page
    if page == "📤 Upload Contract":
        render_upload_page()
    elif page == "📊 Analysis Dashboard":
        render_analysis_dashboard()
    elif page == "📋 Clause Analysis":
        render_clause_analysis()
    elif page == "⚠️ Risk Assessment":
        render_risk_assessment()
    elif page == "✅ Compliance Check":
        render_compliance_check()
    elif page == "📝 Templates":
        render_templates()
    elif page == "❓ Ask Questions":
        render_ask_questions()
    elif page == "📁 Export Reports":
        render_export_reports()


if __name__ == "__main__":
    main()

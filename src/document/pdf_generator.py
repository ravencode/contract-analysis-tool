"""
PDF Report Generator Module
Generates professional PDF reports for contract analysis
"""

import os
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass
import io


@dataclass
class ReportSection:
    """A section in the PDF report."""
    title: str
    content: str
    section_type: str  # text, table, list, risk_indicator


class PDFReportGenerator:
    """
    Generates professional PDF reports for contract analysis.
    Uses FPDF2 for PDF generation.
    """
    
    def __init__(self):
        self.page_width = 210  # A4 width in mm
        self.page_height = 297  # A4 height in mm
        self.margin = 20
        self.content_width = self.page_width - (2 * self.margin)
        
        # Colors
        self.colors = {
            'primary': (41, 128, 185),      # Blue
            'secondary': (52, 73, 94),       # Dark gray
            'success': (39, 174, 96),        # Green
            'warning': (241, 196, 15),       # Yellow
            'danger': (231, 76, 60),         # Red
            'light': (236, 240, 241),        # Light gray
            'white': (255, 255, 255),
            'black': (0, 0, 0)
        }
    
    def _safe_text(self, text: str) -> str:
        """Convert text to ASCII-safe format for PDF."""
        if not text:
            return ""
        # Replace common Unicode characters with ASCII equivalents
        replacements = {
            '₹': 'Rs.',
            '€': 'EUR',
            '£': 'GBP',
            '–': '-',
            '—': '-',
            '"': '"',
            '"': '"',
            ''': "'",
            ''': "'",
            '…': '...',
            '•': '-',
            '→': '->',
            '←': '<-',
            '✓': '[OK]',
            '✗': '[X]',
            '⚠': '[!]',
            '⚡': '[!]',
            '✅': '[OK]',
            '❌': '[X]',
        }
        result = str(text)
        for unicode_char, ascii_char in replacements.items():
            result = result.replace(unicode_char, ascii_char)
        # Encode to latin-1 and replace any remaining problematic characters
        return result.encode('latin-1', errors='replace').decode('latin-1')
    
    def generate_analysis_report(self, 
                                  contract_info: Dict,
                                  classification: Dict,
                                  risk_analysis: Dict,
                                  compliance: Dict,
                                  entities: Dict,
                                  summary: str,
                                  recommendations: List[str]) -> bytes:
        """
        Generate a comprehensive analysis report.
        
        Args:
            contract_info: Basic contract information
            classification: Contract classification results
            risk_analysis: Risk analysis results
            compliance: Compliance check results
            entities: Extracted entities
            summary: Contract summary
            recommendations: List of recommendations
            
        Returns:
            PDF content as bytes
        """
        from fpdf import FPDF
        
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Add first page with header
        pdf.add_page()
        self._add_header(pdf, contract_info.get('filename', 'Contract Analysis Report'))
        
        # Executive Summary
        self._add_section_title(pdf, "Executive Summary")
        self._add_text(pdf, summary[:2000] if summary else "No summary available.")
        
        # Contract Classification
        self._add_section_title(pdf, "Contract Classification")
        self._add_classification_section(pdf, classification)
        
        # Risk Assessment
        pdf.add_page()
        self._add_header(pdf, "Risk Assessment")
        self._add_risk_section(pdf, risk_analysis)
        
        # Compliance Status
        pdf.add_page()
        self._add_header(pdf, "Compliance Check")
        self._add_compliance_section(pdf, compliance)
        
        # Key Entities
        pdf.add_page()
        self._add_header(pdf, "Extracted Information")
        self._add_entities_section(pdf, entities)
        
        # Recommendations
        pdf.add_page()
        self._add_header(pdf, "Recommendations")
        self._add_recommendations_section(pdf, recommendations)
        
        # Footer with timestamp
        self._add_footer(pdf)
        
        return pdf.output()
    
    def generate_summary_report(self,
                                 contract_info: Dict,
                                 summary: str,
                                 key_points: List[str],
                                 risk_level: str,
                                 risk_score: float) -> bytes:
        """
        Generate a brief summary report.
        
        Args:
            contract_info: Basic contract information
            summary: Contract summary
            key_points: Key points from analysis
            risk_level: Overall risk level
            risk_score: Overall risk score
            
        Returns:
            PDF content as bytes
        """
        from fpdf import FPDF
        
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        
        # Header
        self._add_header(pdf, "Contract Summary Report")
        
        # Contract Info
        pdf.set_font('Helvetica', 'B', 12)
        pdf.cell(0, 10, f"Document: {contract_info.get('filename', 'Unknown')}", ln=True)
        pdf.cell(0, 10, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
        pdf.ln(5)
        
        # Risk Indicator
        self._add_risk_indicator(pdf, risk_level, risk_score)
        pdf.ln(10)
        
        # Summary
        self._add_section_title(pdf, "Summary")
        self._add_text(pdf, summary)
        
        # Key Points
        if key_points:
            self._add_section_title(pdf, "Key Points")
            for point in key_points[:10]:
                pdf.set_font('Helvetica', '', 10)
                pdf.multi_cell(self.content_width, 6, self._safe_text(f"- {str(point)[:150]}"))
        
        self._add_footer(pdf)
        
        return pdf.output()
    
    def _add_header(self, pdf, title: str):
        """Add report header."""
        # Background bar
        pdf.set_fill_color(*self.colors['primary'])
        pdf.rect(0, 0, self.page_width, 40, 'F')
        
        # Title
        pdf.set_text_color(*self.colors['white'])
        pdf.set_font('Helvetica', 'B', 20)
        pdf.set_xy(self.margin, 12)
        pdf.cell(0, 10, title, ln=True)
        
        # Subtitle
        pdf.set_font('Helvetica', '', 10)
        pdf.set_xy(self.margin, 25)
        pdf.cell(0, 10, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Reset position and color
        pdf.set_text_color(*self.colors['black'])
        pdf.set_xy(self.margin, 50)
    
    def _add_section_title(self, pdf, title: str):
        """Add a section title."""
        pdf.ln(5)
        pdf.set_font('Helvetica', 'B', 14)
        pdf.set_text_color(*self.colors['primary'])
        pdf.cell(0, 10, title, ln=True)
        pdf.set_text_color(*self.colors['black'])
        
        # Underline
        pdf.set_draw_color(*self.colors['primary'])
        pdf.line(self.margin, pdf.get_y(), self.page_width - self.margin, pdf.get_y())
        pdf.ln(5)
    
    def _add_text(self, pdf, text: str):
        """Add paragraph text."""
        pdf.set_font('Helvetica', '', 10)
        # Ensure text is safe for PDF
        safe_text = str(text).encode('latin-1', errors='replace').decode('latin-1')
        pdf.multi_cell(self.content_width, 6, safe_text)
        pdf.ln(3)
    
    def _add_classification_section(self, pdf, classification: Dict):
        """Add contract classification section."""
        pdf.set_font('Helvetica', '', 11)
        
        # Contract Type
        contract_type = classification.get('contract_type', 'Unknown')
        confidence = classification.get('confidence', 0)
        
        pdf.set_font('Helvetica', 'B', 11)
        pdf.cell(50, 8, "Contract Type:")
        pdf.set_font('Helvetica', '', 11)
        pdf.cell(0, 8, contract_type, ln=True)
        
        pdf.set_font('Helvetica', 'B', 11)
        pdf.cell(50, 8, "Confidence:")
        pdf.set_font('Helvetica', '', 11)
        pdf.cell(0, 8, f"{confidence:.0%}", ln=True)
        
        # Parties
        parties = classification.get('parties', [])
        if parties:
            pdf.set_font('Helvetica', 'B', 11)
            pdf.cell(50, 8, "Parties:")
            pdf.set_font('Helvetica', '', 11)
            pdf.multi_cell(0, 8, ', '.join(parties[:5]))
        
        # Jurisdiction
        jurisdiction = classification.get('jurisdiction', '')
        if jurisdiction:
            pdf.set_font('Helvetica', 'B', 11)
            pdf.cell(50, 8, "Jurisdiction:")
            pdf.set_font('Helvetica', '', 11)
            pdf.cell(0, 8, jurisdiction, ln=True)
    
    def _add_risk_section(self, pdf, risk_analysis: Dict):
        """Add risk analysis section."""
        # Overall Risk
        overall_score = risk_analysis.get('overall_score', 0.5)
        overall_level = risk_analysis.get('overall_level', 'medium')
        
        self._add_risk_indicator(pdf, overall_level, overall_score)
        pdf.ln(10)
        
        # Risk Distribution
        distribution = risk_analysis.get('risk_distribution', {})
        if distribution:
            pdf.set_font('Helvetica', 'B', 11)
            pdf.cell(0, 8, "Risk Distribution:", ln=True)
            pdf.set_font('Helvetica', '', 10)
            
            for level, count in distribution.items():
                color = self._get_risk_color(level)
                pdf.set_text_color(*color)
                pdf.cell(0, 6, f"  - {level.upper()}: {count} clauses", ln=True)
            
            pdf.set_text_color(*self.colors['black'])
        
        # Priority Issues
        priority_issues = risk_analysis.get('priority_issues', [])
        if priority_issues:
            pdf.ln(5)
            pdf.set_font('Helvetica', 'B', 11)
            pdf.cell(0, 8, "Priority Issues:", ln=True)
            pdf.set_font('Helvetica', '', 10)
            
            for issue in priority_issues[:5]:
                pdf.set_text_color(*self.colors['danger'])
                # Truncate long issues to prevent overflow
                issue_text = str(issue)[:150] if len(str(issue)) > 150 else str(issue)
                pdf.multi_cell(self.content_width, 6, self._safe_text(f"[!] {issue_text}"))
            
            pdf.set_text_color(*self.colors['black'])
    
    def _add_risk_indicator(self, pdf, risk_level: str, risk_score: float):
        """Add visual risk indicator."""
        # Determine color
        if isinstance(risk_level, str):
            level_str = risk_level.lower()
        else:
            level_str = str(risk_level).lower()
        
        color = self._get_risk_color(level_str)
        
        # Risk box
        pdf.set_fill_color(*color)
        pdf.set_text_color(*self.colors['white'])
        pdf.set_font('Helvetica', 'B', 12)
        
        # Draw box
        box_width = 80
        box_height = 25
        x = (self.page_width - box_width) / 2
        y = pdf.get_y()
        
        pdf.rect(x, y, box_width, box_height, 'F')
        pdf.set_xy(x, y + 5)
        pdf.cell(box_width, 8, f"RISK: {level_str.upper()}", align='C', ln=True)
        pdf.set_xy(x, y + 15)
        pdf.set_font('Helvetica', '', 10)
        pdf.cell(box_width, 6, f"Score: {risk_score:.2f}", align='C')
        
        pdf.set_text_color(*self.colors['black'])
        pdf.set_xy(self.margin, y + box_height + 5)
    
    def _add_compliance_section(self, pdf, compliance: Dict):
        """Add compliance check section."""
        status = compliance.get('overall_status', 'unknown')
        if hasattr(status, 'value'):
            status = status.value
        
        # Status indicator
        if status == 'compliant':
            color = self.colors['success']
            icon = "[OK]"
        elif status == 'partially_compliant':
            color = self.colors['warning']
            icon = "[!]"
        else:
            color = self.colors['danger']
            icon = "[X]"
        
        pdf.set_text_color(*color)
        pdf.set_font('Helvetica', 'B', 14)
        pdf.cell(0, 10, f"{icon} Status: {status.upper().replace('_', ' ')}", ln=True)
        pdf.set_text_color(*self.colors['black'])
        
        # Laws Checked
        laws = compliance.get('laws_checked', [])
        if laws:
            pdf.ln(5)
            pdf.set_font('Helvetica', 'B', 11)
            pdf.cell(0, 8, "Laws Checked:", ln=True)
            pdf.set_font('Helvetica', '', 10)
            for law in laws:
                pdf.cell(0, 6, f"  - {law}", ln=True)
        
        # Issues
        issues = compliance.get('issues', [])
        if issues:
            pdf.ln(5)
            pdf.set_font('Helvetica', 'B', 11)
            pdf.set_text_color(*self.colors['danger'])
            pdf.cell(0, 8, f"Issues Found ({len(issues)}):", ln=True)
            pdf.set_text_color(*self.colors['black'])
            pdf.set_font('Helvetica', '', 10)
            
            for issue in issues[:5]:
                if hasattr(issue, 'law_reference'):
                    text = f"- [{issue.law_reference}] {issue.issue_description}"[:150]
                    pdf.multi_cell(self.content_width, 6, self._safe_text(text))
                else:
                    pdf.multi_cell(self.content_width, 6, self._safe_text(f"- {str(issue)[:150]}"))
    
    def _add_entities_section(self, pdf, entities: Dict):
        """Add extracted entities section."""
        # Parties
        parties = entities.get('parties', [])
        if parties:
            pdf.set_font('Helvetica', 'B', 11)
            pdf.cell(0, 8, "Parties Identified:", ln=True)
            pdf.set_font('Helvetica', '', 10)
            for party in parties[:5]:
                val = party.value if hasattr(party, 'value') else str(party)
                pdf.cell(0, 6, self._safe_text(f"  - {val}"), ln=True)
            pdf.ln(3)
        
        # Dates
        dates = entities.get('dates', [])
        if dates:
            pdf.set_font('Helvetica', 'B', 11)
            pdf.cell(0, 8, "Key Dates:", ln=True)
            pdf.set_font('Helvetica', '', 10)
            for date in dates[:5]:
                val = date.value if hasattr(date, 'value') else str(date)
                pdf.cell(0, 6, self._safe_text(f"  - {val}"), ln=True)
            pdf.ln(3)
        
        # Amounts
        amounts = entities.get('amounts', [])
        if amounts:
            pdf.set_font('Helvetica', 'B', 11)
            pdf.cell(0, 8, "Financial Amounts:", ln=True)
            pdf.set_font('Helvetica', '', 10)
            for amount in amounts[:5]:
                val = amount.value if hasattr(amount, 'value') else str(amount)
                pdf.cell(0, 6, self._safe_text(f"  - {val}"), ln=True)
            pdf.ln(3)
        
        # Jurisdictions
        jurisdictions = entities.get('jurisdictions', [])
        if jurisdictions:
            pdf.set_font('Helvetica', 'B', 11)
            pdf.cell(0, 8, "Jurisdiction:", ln=True)
            pdf.set_font('Helvetica', '', 10)
            for j in jurisdictions[:3]:
                val = j.value if hasattr(j, 'value') else str(j)
                pdf.cell(0, 6, self._safe_text(f"  - {val}"), ln=True)
    
    def _add_recommendations_section(self, pdf, recommendations: List[str]):
        """Add recommendations section."""
        if not recommendations:
            pdf.set_font('Helvetica', '', 11)
            pdf.cell(0, 10, "No specific recommendations at this time.", ln=True)
            return
        
        pdf.set_font('Helvetica', '', 10)
        
        for i, rec in enumerate(recommendations, 1):
            # Check for priority indicators
            if 'CRITICAL' in rec or 'HIGH RISK' in rec:
                pdf.set_text_color(*self.colors['danger'])
            elif 'HIGH' in rec or 'MODERATE' in rec:
                pdf.set_text_color(*self.colors['warning'])
            elif 'LOW' in rec or 'appears' in rec:
                pdf.set_text_color(*self.colors['success'])
            else:
                pdf.set_text_color(*self.colors['black'])
            
            rec_text = str(rec)[:200] if len(str(rec)) > 200 else str(rec)
            pdf.multi_cell(self.content_width, 6, self._safe_text(f"{i}. {rec_text}"))
            pdf.ln(2)
        
        pdf.set_text_color(*self.colors['black'])
    
    def _add_footer(self, pdf):
        """Add footer to all pages."""
        total_pages = pdf.page_no()
        
        for page in range(1, total_pages + 1):
            pdf.page = page
            pdf.set_y(-15)
            pdf.set_font('Helvetica', 'I', 8)
            pdf.set_text_color(*self.colors['secondary'])
            pdf.cell(0, 10, f'Page {page} of {total_pages} | Contract Analysis Bot | Confidential', align='C')
    
    def _get_risk_color(self, level: str) -> tuple:
        """Get color for risk level."""
        level = level.lower() if isinstance(level, str) else 'medium'
        
        if level in ['critical', 'high']:
            return self.colors['danger']
        elif level == 'medium':
            return self.colors['warning']
        else:
            return self.colors['success']
    
    def generate_clause_report(self, clauses: List[Dict]) -> bytes:
        """
        Generate a report focused on clause analysis.
        
        Args:
            clauses: List of analyzed clauses
            
        Returns:
            PDF content as bytes
        """
        from fpdf import FPDF
        
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        
        self._add_header(pdf, "Clause-by-Clause Analysis")
        
        for i, clause in enumerate(clauses[:20], 1):  # Limit to 20 clauses
            pdf.set_font('Helvetica', 'B', 11)
            title = clause.get('title', f'Clause {i}')
            pdf.cell(0, 8, f"{i}. {title}", ln=True)
            
            # Risk indicator
            risk_level = clause.get('risk_level', 'low')
            color = self._get_risk_color(risk_level)
            pdf.set_text_color(*color)
            pdf.set_font('Helvetica', 'B', 9)
            pdf.cell(0, 6, f"Risk: {risk_level.upper()}", ln=True)
            pdf.set_text_color(*self.colors['black'])
            
            # Content preview
            content = clause.get('content', '')[:300]
            pdf.set_font('Helvetica', '', 9)
            pdf.multi_cell(0, 5, content + "..." if len(clause.get('content', '')) > 300 else content)
            
            pdf.ln(5)
            
            # Check if we need a new page
            if pdf.get_y() > 250:
                pdf.add_page()
        
        self._add_footer(pdf)
        
        return pdf.output()

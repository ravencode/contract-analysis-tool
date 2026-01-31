"""
Prompt Templates for GPT-based Legal Analysis
Structured prompts for various contract analysis tasks
"""

from typing import Dict, List, Optional


class PromptTemplates:
    """
    Collection of prompt templates for legal contract analysis.
    Designed for GPT-5 (or GPT-4) for accurate legal reasoning.
    """
    
    @staticmethod
    def contract_classification() -> str:
        """Prompt for classifying contract type."""
        return """You are an expert legal analyst specializing in Indian contract law.

Analyze the following contract and classify it into ONE of these categories:
- Employment Agreement
- Vendor Contract
- Lease Agreement
- Partnership Deed
- Service Contract
- Non-Disclosure Agreement
- Consultancy Agreement
- Supply Agreement
- Franchise Agreement
- Joint Venture Agreement
- Other (specify)

Also identify:
1. The primary purpose of the contract
2. The main parties involved
3. The governing jurisdiction
4. Key subject matter

CONTRACT TEXT:
{contract_text}

Respond in JSON format:
{{
    "contract_type": "...",
    "confidence": 0.0-1.0,
    "purpose": "...",
    "parties": ["party1", "party2"],
    "jurisdiction": "...",
    "subject_matter": "...",
    "reasoning": "..."
}}"""

    @staticmethod
    def clause_explanation() -> str:
        """Prompt for explaining a clause in plain language."""
        return """You are a legal expert helping small business owners understand contracts.

Explain the following contract clause in simple, plain language that a non-lawyer can understand.
Avoid legal jargon. Use everyday examples where helpful.

CLAUSE:
{clause_text}

CLAUSE TYPE: {clause_type}

Provide:
1. **Simple Explanation**: What this clause means in plain English
2. **What It Means For You**: Practical implications for a business owner
3. **Key Points**: 3-5 bullet points of the most important aspects
4. **Watch Out For**: Any potential concerns or things to be careful about
5. **Common Questions**: 2-3 questions a business owner might have about this clause

Keep the language simple and business-focused."""

    @staticmethod
    def risk_assessment() -> str:
        """Prompt for assessing risk in a clause."""
        return """You are a legal risk analyst specializing in contract review for Indian SMEs.

Analyze the following clause for potential risks and concerns.

CLAUSE:
{clause_text}

CLAUSE TYPE: {clause_type}
CONTRACT TYPE: {contract_type}

Assess the following:

1. **Risk Level**: Rate as LOW, MEDIUM, or HIGH
2. **Risk Score**: Provide a score from 0.0 to 1.0
3. **Risk Factors**: List specific risk factors identified
4. **Potential Impact**: What could go wrong for the business
5. **Red Flags**: Any particularly concerning language
6. **Mitigation Suggestions**: How to reduce the risk
7. **Negotiation Points**: What to ask for in negotiations

Consider these risk categories:
- Financial risk
- Operational risk
- Legal/compliance risk
- Reputational risk
- Strategic risk

Respond in JSON format:
{{
    "risk_level": "LOW/MEDIUM/HIGH",
    "risk_score": 0.0-1.0,
    "risk_factors": ["factor1", "factor2"],
    "potential_impact": "...",
    "red_flags": ["flag1", "flag2"],
    "mitigation_suggestions": ["suggestion1", "suggestion2"],
    "negotiation_points": ["point1", "point2"],
    "explanation": "..."
}}"""

    @staticmethod
    def contract_summary() -> str:
        """Prompt for generating a contract summary."""
        return """You are a legal expert creating a summary for business owners.

Create a comprehensive yet easy-to-understand summary of this contract.

CONTRACT TEXT:
{contract_text}

Generate a summary with these sections:

## Contract Overview
- Type of contract
- Parties involved
- Effective date and duration
- Primary purpose

## Key Terms
- Main obligations of each party
- Payment terms and amounts
- Deliverables or services
- Important deadlines

## Rights and Protections
- Your rights under this contract
- Protections provided
- Limitations on the other party

## Risks and Concerns
- Potential risks identified
- Unfavorable terms
- Areas needing attention

## Important Clauses
- Termination conditions
- Penalty clauses
- Dispute resolution
- Confidentiality requirements

## Recommendations
- Things to negotiate
- Clauses to modify
- Additional protections to request

## Quick Reference
- Key dates
- Key amounts
- Key contacts/notices

Write in clear, simple language suitable for a business owner without legal background."""

    @staticmethod
    def unfavorable_terms_detection() -> str:
        """Prompt for identifying unfavorable terms."""
        return """You are a legal advocate protecting the interests of small business owners.

Review this contract and identify terms that are unfavorable or potentially harmful to the business owner.

CONTRACT TEXT:
{contract_text}

PARTY TO PROTECT: {party_name}

Identify and analyze:

1. **Unfavorable Terms**: List each unfavorable term with:
   - The exact clause text
   - Why it's unfavorable
   - Severity (Minor/Moderate/Severe)
   - Suggested alternative language

2. **One-Sided Provisions**: Terms that heavily favor the other party

3. **Hidden Risks**: Subtle language that could cause problems

4. **Missing Protections**: Standard protections that are absent

5. **Unusual Clauses**: Terms that deviate from standard practice

6. **Compliance Concerns**: Terms that may conflict with Indian laws

Respond in JSON format:
{{
    "unfavorable_terms": [
        {{
            "clause_text": "...",
            "issue": "...",
            "severity": "Minor/Moderate/Severe",
            "suggested_alternative": "...",
            "explanation": "..."
        }}
    ],
    "one_sided_provisions": [...],
    "hidden_risks": [...],
    "missing_protections": [...],
    "unusual_clauses": [...],
    "compliance_concerns": [...],
    "overall_assessment": "...",
    "priority_issues": [...]
}}"""

    @staticmethod
    def alternative_clause_suggestion() -> str:
        """Prompt for suggesting alternative clause language."""
        return """You are a contract drafting expert helping businesses negotiate better terms.

The following clause has been identified as potentially unfavorable or risky:

ORIGINAL CLAUSE:
{original_clause}

ISSUE IDENTIFIED:
{issue}

PARTY TO PROTECT: {party_name}

Provide:

1. **Alternative Clause**: Rewrite the clause to be more balanced/favorable
2. **Explanation**: Why the alternative is better
3. **Key Changes**: Specific changes made and their impact
4. **Negotiation Script**: How to present this to the other party
5. **Fallback Position**: A compromise if the full alternative is rejected
6. **Industry Standard**: What is typically seen in similar contracts

Format the alternative clause professionally, ready to be inserted into a contract."""

    @staticmethod
    def compliance_check() -> str:
        """Prompt for checking compliance with Indian laws."""
        return """You are a legal compliance expert specializing in Indian business law.

Review this contract for compliance with applicable Indian laws and regulations.

CONTRACT TEXT:
{contract_text}

CONTRACT TYPE: {contract_type}

Check compliance with:
1. Indian Contract Act, 1872
2. Arbitration and Conciliation Act, 1996
3. Information Technology Act, 2000
4. Consumer Protection Act, 2019 (if applicable)
5. Competition Act, 2002
6. Applicable labour laws (for employment contracts)
7. Stamp duty requirements
8. Registration requirements

For each potential issue, provide:
- The specific clause or provision
- The law/regulation it may violate
- The nature of non-compliance
- Recommended correction
- Risk if not corrected

Respond in JSON format:
{{
    "compliance_status": "Compliant/Partially Compliant/Non-Compliant",
    "issues": [
        {{
            "clause": "...",
            "law": "...",
            "issue": "...",
            "severity": "Low/Medium/High",
            "recommendation": "...",
            "risk": "..."
        }}
    ],
    "missing_requirements": [...],
    "recommendations": [...],
    "overall_assessment": "..."
}}"""

    @staticmethod
    def obligation_extraction() -> str:
        """Prompt for extracting obligations, rights, and prohibitions."""
        return """You are a legal analyst extracting contractual terms.

Analyze this contract and extract all obligations, rights, and prohibitions.

CONTRACT TEXT:
{contract_text}

For each party, identify:

## OBLIGATIONS (things they MUST do)
- The specific obligation
- Deadline or timeline (if any)
- Consequences of non-compliance
- Related clause reference

## RIGHTS (things they CAN do)
- The specific right
- Conditions for exercising the right
- Limitations on the right
- Related clause reference

## PROHIBITIONS (things they CANNOT do)
- The specific prohibition
- Exceptions (if any)
- Consequences of violation
- Related clause reference

Respond in JSON format:
{{
    "party_1": {{
        "name": "...",
        "obligations": [...],
        "rights": [...],
        "prohibitions": [...]
    }},
    "party_2": {{
        "name": "...",
        "obligations": [...],
        "rights": [...],
        "prohibitions": [...]
    }},
    "mutual_obligations": [...],
    "mutual_rights": [...],
    "mutual_prohibitions": [...]
}}"""

    @staticmethod
    def ambiguity_detection() -> str:
        """Prompt for detecting ambiguous language."""
        return """You are a legal precision expert identifying vague or ambiguous contract language.

Review this contract for ambiguous, vague, or unclear terms that could lead to disputes.

CONTRACT TEXT:
{contract_text}

Identify:

1. **Vague Terms**: Words like "reasonable", "material", "substantial", "promptly"
2. **Undefined Terms**: Important terms used without definition
3. **Conflicting Provisions**: Clauses that contradict each other
4. **Missing Specifics**: Where numbers, dates, or details should be specified
5. **Interpretation Issues**: Language that could be interpreted multiple ways
6. **Incomplete Provisions**: Clauses that seem unfinished or incomplete

For each issue:
- Quote the problematic text
- Explain why it's ambiguous
- Suggest how to clarify
- Rate the risk (Low/Medium/High)

Respond in JSON format:
{{
    "ambiguities": [
        {{
            "text": "...",
            "type": "vague_term/undefined/conflicting/missing/interpretation/incomplete",
            "issue": "...",
            "suggestion": "...",
            "risk_level": "Low/Medium/High"
        }}
    ],
    "total_issues": 0,
    "high_priority_issues": [...],
    "recommendations": [...]
}}"""

    @staticmethod
    def template_comparison() -> str:
        """Prompt for comparing contract to standard template."""
        return """You are a contract standardization expert.

Compare this contract against standard industry practices for this type of agreement.

CONTRACT TEXT:
{contract_text}

CONTRACT TYPE: {contract_type}
STANDARD TEMPLATE ELEMENTS: {template_elements}

Analyze:

1. **Present Standard Clauses**: Which standard clauses are included
2. **Missing Standard Clauses**: Which standard clauses are absent
3. **Non-Standard Clauses**: Unusual or custom provisions
4. **Deviations**: Where the contract differs from standard practice
5. **Quality Assessment**: Overall quality compared to standards

For each deviation or missing element:
- Explain the standard practice
- Note what's different or missing
- Assess the impact
- Recommend action

Respond in JSON format:
{{
    "present_clauses": [...],
    "missing_clauses": [...],
    "non_standard_clauses": [...],
    "deviations": [
        {{
            "standard": "...",
            "actual": "...",
            "impact": "...",
            "recommendation": "..."
        }}
    ],
    "quality_score": 0.0-1.0,
    "overall_assessment": "..."
}}"""

    @staticmethod
    def negotiation_strategy() -> str:
        """Prompt for generating negotiation strategy."""
        return """You are a negotiation strategist helping businesses get better contract terms.

Based on the contract analysis, develop a negotiation strategy.

CONTRACT SUMMARY:
{contract_summary}

IDENTIFIED ISSUES:
{issues}

PARTY POSITION: {party_position}

Create a negotiation strategy including:

1. **Priority Issues**: Rank issues by importance
2. **Must-Have Changes**: Non-negotiable modifications
3. **Nice-to-Have Changes**: Preferred but flexible
4. **Trade-offs**: What can be conceded in exchange
5. **Talking Points**: Key arguments for each issue
6. **Alternative Solutions**: Creative compromises
7. **Walk-Away Points**: When to reject the contract
8. **Timeline**: Suggested negotiation approach

Provide specific language and scripts for key negotiations."""

    @staticmethod
    def hindi_translation() -> str:
        """Prompt for translating analysis to Hindi."""
        return """You are a bilingual legal expert fluent in English and Hindi.

Translate the following contract analysis summary into Hindi.
Use simple Hindi that business owners can understand.
Keep legal terms in English with Hindi explanations in parentheses.

ENGLISH SUMMARY:
{english_summary}

Provide the translation in Devanagari script.
Maintain the same structure and formatting as the original."""

    @staticmethod
    def executive_summary() -> str:
        """Prompt for generating executive summary."""
        return """You are a legal advisor preparing a brief for busy executives.

Create a concise executive summary of this contract analysis.

FULL ANALYSIS:
{full_analysis}

The summary should be:
- Maximum 500 words
- Bullet-pointed for quick reading
- Highlight only critical issues
- Include clear recommendations
- Provide a go/no-go recommendation

Structure:
1. **Contract Overview** (2-3 sentences)
2. **Key Terms** (5 bullet points max)
3. **Critical Risks** (top 3 only)
4. **Immediate Actions Required**
5. **Recommendation**: Proceed / Proceed with Changes / Do Not Proceed

Be direct and actionable."""

    @staticmethod
    def get_system_prompt() -> str:
        """Get the system prompt for legal analysis."""
        return """You are an expert legal AI assistant specializing in contract analysis for Indian small and medium businesses (SMEs).

Your role is to:
1. Analyze contracts thoroughly and accurately
2. Identify risks and unfavorable terms
3. Explain legal concepts in simple, plain language
4. Provide actionable advice for business owners
5. Ensure compliance with Indian laws
6. Suggest improvements and alternatives

Guidelines:
- Always prioritize the interests of the SME/business owner
- Be thorough but concise
- Use simple language, avoid unnecessary jargon
- Provide specific, actionable recommendations
- Flag any serious concerns prominently
- Consider the Indian legal and business context
- Maintain confidentiality and professionalism

You have expertise in:
- Indian Contract Act, 1872
- Arbitration and Conciliation Act, 1996
- Information Technology Act, 2000
- Consumer Protection Act, 2019
- Competition Act, 2002
- Labour laws applicable to employment contracts
- Standard commercial contract practices in India"""

    @staticmethod
    def build_prompt(template_name: str, **kwargs) -> str:
        """
        Build a complete prompt from template and parameters.
        
        Args:
            template_name: Name of the template method
            **kwargs: Parameters to fill in the template
            
        Returns:
            Formatted prompt string
        """
        templates = PromptTemplates()
        template_method = getattr(templates, template_name, None)
        
        if template_method is None:
            raise ValueError(f"Unknown template: {template_name}")
        
        template = template_method()
        
        try:
            return template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing required parameter: {e}")

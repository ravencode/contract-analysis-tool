"""
GPT Client Module
Integration with OpenAI GPT for legal reasoning
"""

import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import openai
from openai import OpenAI

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.settings import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_MAX_TOKENS, OPENAI_TEMPERATURE
from src.llm.prompts import PromptTemplates


@dataclass
class GPTResponse:
    """Data class for GPT response."""
    content: str
    parsed_json: Optional[Dict] = None
    tokens_used: int = 0
    model: str = ""
    success: bool = True
    error: Optional[str] = None


class GPTClient:
    """
    Client for interacting with OpenAI GPT models for legal analysis.
    Handles prompt construction, API calls, and response parsing.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or OPENAI_API_KEY
        self.model = OPENAI_MODEL
        self.max_tokens = OPENAI_MAX_TOKENS
        self.temperature = OPENAI_TEMPERATURE
        
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)
        else:
            self.client = None
        
        self.prompts = PromptTemplates()
        self.system_prompt = PromptTemplates.get_system_prompt()
    
    def is_configured(self) -> bool:
        """Check if the client is properly configured."""
        return self.api_key is not None and len(self.api_key) > 0
    
    def _call_gpt(self, user_prompt: str, 
                  system_prompt: Optional[str] = None,
                  temperature: Optional[float] = None,
                  max_tokens: Optional[int] = None,
                  json_mode: bool = False) -> GPTResponse:
        """
        Make a call to the GPT API.
        
        Args:
            user_prompt: The user message/prompt
            system_prompt: Optional system prompt override
            temperature: Optional temperature override
            max_tokens: Optional max tokens override
            json_mode: Whether to request JSON response
            
        Returns:
            GPTResponse object
        """
        if not self.is_configured():
            return GPTResponse(
                content="",
                success=False,
                error="OpenAI API key not configured. Please set OPENAI_API_KEY in .env file."
            )
        
        try:
            messages = [
                {"role": "system", "content": system_prompt or self.system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature or self.temperature,
                "max_tokens": max_tokens or self.max_tokens
            }
            
            if json_mode:
                kwargs["response_format"] = {"type": "json_object"}
            
            response = self.client.chat.completions.create(**kwargs)
            
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else 0
            
            # Try to parse JSON if expected
            parsed_json = None
            if json_mode or content.strip().startswith('{'):
                try:
                    # Clean up the response if needed
                    json_str = content
                    if '```json' in json_str:
                        json_str = json_str.split('```json')[1].split('```')[0]
                    elif '```' in json_str:
                        json_str = json_str.split('```')[1].split('```')[0]
                    parsed_json = json.loads(json_str.strip())
                except json.JSONDecodeError:
                    pass
            
            return GPTResponse(
                content=content,
                parsed_json=parsed_json,
                tokens_used=tokens_used,
                model=self.model,
                success=True
            )
            
        except openai.APIConnectionError as e:
            return GPTResponse(
                content="",
                success=False,
                error=f"Connection error: {str(e)}"
            )
        except openai.RateLimitError as e:
            return GPTResponse(
                content="",
                success=False,
                error=f"Rate limit exceeded: {str(e)}"
            )
        except openai.APIStatusError as e:
            return GPTResponse(
                content="",
                success=False,
                error=f"API error: {str(e)}"
            )
        except Exception as e:
            return GPTResponse(
                content="",
                success=False,
                error=f"Unexpected error: {str(e)}"
            )
    
    def classify_contract(self, contract_text: str) -> GPTResponse:
        """
        Classify the type of contract.
        
        Args:
            contract_text: The contract text to classify
            
        Returns:
            GPTResponse with classification results
        """
        # Truncate if too long
        max_chars = 15000
        if len(contract_text) > max_chars:
            contract_text = contract_text[:max_chars] + "\n\n[... contract continues ...]"
        
        prompt = PromptTemplates.build_prompt(
            'contract_classification',
            contract_text=contract_text
        )
        
        return self._call_gpt(prompt, json_mode=True)
    
    def explain_clause(self, clause_text: str, clause_type: str) -> GPTResponse:
        """
        Explain a clause in plain language.
        
        Args:
            clause_text: The clause to explain
            clause_type: The type of clause
            
        Returns:
            GPTResponse with explanation
        """
        prompt = PromptTemplates.build_prompt(
            'clause_explanation',
            clause_text=clause_text,
            clause_type=clause_type
        )
        
        return self._call_gpt(prompt)
    
    def assess_clause_risk(self, clause_text: str, 
                           clause_type: str,
                           contract_type: str) -> GPTResponse:
        """
        Assess the risk level of a clause.
        
        Args:
            clause_text: The clause to assess
            clause_type: The type of clause
            contract_type: The type of contract
            
        Returns:
            GPTResponse with risk assessment
        """
        prompt = PromptTemplates.build_prompt(
            'risk_assessment',
            clause_text=clause_text,
            clause_type=clause_type,
            contract_type=contract_type
        )
        
        return self._call_gpt(prompt, json_mode=True)
    
    def generate_summary(self, contract_text: str) -> GPTResponse:
        """
        Generate a comprehensive contract summary.
        
        Args:
            contract_text: The contract to summarize
            
        Returns:
            GPTResponse with summary
        """
        # Truncate if too long
        max_chars = 20000
        if len(contract_text) > max_chars:
            contract_text = contract_text[:max_chars] + "\n\n[... contract continues ...]"
        
        prompt = PromptTemplates.build_prompt(
            'contract_summary',
            contract_text=contract_text
        )
        
        return self._call_gpt(prompt, max_tokens=4000)
    
    def detect_unfavorable_terms(self, contract_text: str,
                                  party_name: str) -> GPTResponse:
        """
        Detect unfavorable terms in the contract.
        
        Args:
            contract_text: The contract to analyze
            party_name: The party to protect
            
        Returns:
            GPTResponse with unfavorable terms
        """
        max_chars = 18000
        if len(contract_text) > max_chars:
            contract_text = contract_text[:max_chars] + "\n\n[... contract continues ...]"
        
        prompt = PromptTemplates.build_prompt(
            'unfavorable_terms_detection',
            contract_text=contract_text,
            party_name=party_name
        )
        
        return self._call_gpt(prompt, json_mode=True, max_tokens=4000)
    
    def suggest_alternative_clause(self, original_clause: str,
                                    issue: str,
                                    party_name: str) -> GPTResponse:
        """
        Suggest alternative clause language.
        
        Args:
            original_clause: The original clause text
            issue: The identified issue
            party_name: The party to protect
            
        Returns:
            GPTResponse with alternative suggestion
        """
        prompt = PromptTemplates.build_prompt(
            'alternative_clause_suggestion',
            original_clause=original_clause,
            issue=issue,
            party_name=party_name
        )
        
        return self._call_gpt(prompt)
    
    def check_compliance(self, contract_text: str,
                         contract_type: str) -> GPTResponse:
        """
        Check contract compliance with Indian laws.
        
        Args:
            contract_text: The contract to check
            contract_type: The type of contract
            
        Returns:
            GPTResponse with compliance results
        """
        max_chars = 18000
        if len(contract_text) > max_chars:
            contract_text = contract_text[:max_chars] + "\n\n[... contract continues ...]"
        
        prompt = PromptTemplates.build_prompt(
            'compliance_check',
            contract_text=contract_text,
            contract_type=contract_type
        )
        
        return self._call_gpt(prompt, json_mode=True)
    
    def extract_obligations(self, contract_text: str) -> GPTResponse:
        """
        Extract obligations, rights, and prohibitions.
        
        Args:
            contract_text: The contract to analyze
            
        Returns:
            GPTResponse with extracted terms
        """
        max_chars = 18000
        if len(contract_text) > max_chars:
            contract_text = contract_text[:max_chars] + "\n\n[... contract continues ...]"
        
        prompt = PromptTemplates.build_prompt(
            'obligation_extraction',
            contract_text=contract_text
        )
        
        return self._call_gpt(prompt, json_mode=True, max_tokens=4000)
    
    def detect_ambiguities(self, contract_text: str) -> GPTResponse:
        """
        Detect ambiguous language in the contract.
        
        Args:
            contract_text: The contract to analyze
            
        Returns:
            GPTResponse with ambiguity detection results
        """
        max_chars = 18000
        if len(contract_text) > max_chars:
            contract_text = contract_text[:max_chars] + "\n\n[... contract continues ...]"
        
        prompt = PromptTemplates.build_prompt(
            'ambiguity_detection',
            contract_text=contract_text
        )
        
        return self._call_gpt(prompt, json_mode=True)
    
    def compare_to_template(self, contract_text: str,
                            contract_type: str,
                            template_elements: List[str]) -> GPTResponse:
        """
        Compare contract to standard template.
        
        Args:
            contract_text: The contract to compare
            contract_type: The type of contract
            template_elements: Standard elements to check
            
        Returns:
            GPTResponse with comparison results
        """
        max_chars = 15000
        if len(contract_text) > max_chars:
            contract_text = contract_text[:max_chars] + "\n\n[... contract continues ...]"
        
        prompt = PromptTemplates.build_prompt(
            'template_comparison',
            contract_text=contract_text,
            contract_type=contract_type,
            template_elements=', '.join(template_elements)
        )
        
        return self._call_gpt(prompt, json_mode=True)
    
    def generate_executive_summary(self, full_analysis: str) -> GPTResponse:
        """
        Generate an executive summary of the analysis.
        
        Args:
            full_analysis: The complete analysis text
            
        Returns:
            GPTResponse with executive summary
        """
        prompt = PromptTemplates.build_prompt(
            'executive_summary',
            full_analysis=full_analysis
        )
        
        return self._call_gpt(prompt, max_tokens=1000)
    
    def translate_to_hindi(self, english_summary: str) -> GPTResponse:
        """
        Translate analysis summary to Hindi.
        
        Args:
            english_summary: The English summary to translate
            
        Returns:
            GPTResponse with Hindi translation
        """
        prompt = PromptTemplates.build_prompt(
            'hindi_translation',
            english_summary=english_summary
        )
        
        return self._call_gpt(prompt)
    
    def custom_query(self, contract_text: str, query: str) -> GPTResponse:
        """
        Answer a custom query about the contract.
        
        Args:
            contract_text: The contract text
            query: The user's question
            
        Returns:
            GPTResponse with answer
        """
        max_chars = 15000
        if len(contract_text) > max_chars:
            contract_text = contract_text[:max_chars] + "\n\n[... contract continues ...]"
        
        prompt = f"""Based on the following contract, please answer this question:

QUESTION: {query}

CONTRACT TEXT:
{contract_text}

Provide a clear, helpful answer based on the contract content. If the answer cannot be determined from the contract, say so clearly."""
        
        return self._call_gpt(prompt)
    
    def batch_analyze(self, contract_text: str, 
                      analyses: List[str]) -> Dict[str, GPTResponse]:
        """
        Perform multiple analyses on a contract.
        
        Args:
            contract_text: The contract to analyze
            analyses: List of analysis types to perform
            
        Returns:
            Dictionary of analysis type to GPTResponse
        """
        results = {}
        
        analysis_methods = {
            'classify': lambda: self.classify_contract(contract_text),
            'summary': lambda: self.generate_summary(contract_text),
            'obligations': lambda: self.extract_obligations(contract_text),
            'ambiguities': lambda: self.detect_ambiguities(contract_text),
        }
        
        for analysis in analyses:
            if analysis in analysis_methods:
                results[analysis] = analysis_methods[analysis]()
        
        return results

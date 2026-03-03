"""
LLM-based parameter extraction service
Extracts structured parameters from natural language queries
"""
import os
import json
from datetime import datetime, timedelta, date
from typing import Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv
from dateutil.relativedelta import relativedelta

from models.schemas import ExtractedParameters, EventType

load_dotenv()


class LLMParameterExtractor:
    """Extract structured parameters from natural language queries using LLM"""
    
    def __init__(self):
        # Force reload environment variables
        load_dotenv(override=True)
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in .env file")
        
        print(f"🔑 API Key loaded: {api_key[:20]}...{api_key[-10:]}")
        
        # Configure for Groq API (OpenAI-compatible)
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1"
        )
        self.model = os.getenv("OPENAI_MODEL", "llama-3.3-70b-versatile")
        print(f"✅ Using Groq API with model: {self.model}")
        
    def _resolve_relative_dates(self, date_str: str, reference_date: Optional[date] = None) -> date:
        """
        Resolve relative date expressions to actual dates
        Supports: "past 2 weeks", "last month", "past 3 days", etc.
        """
        if reference_date is None:
            reference_date = date.today()
            
        date_str_lower = date_str.lower().strip()
        
        # Handle "today"
        if date_str_lower == "today":
            return reference_date
            
        # Handle "yesterday"
        if date_str_lower == "yesterday":
            return reference_date - timedelta(days=1)
            
        # Handle "past X days/weeks/months"
        if "past" in date_str_lower or "last" in date_str_lower:
            parts = date_str_lower.split()
            
            # Find the number
            number = None
            unit = None
            for i, part in enumerate(parts):
                if part.isdigit():
                    number = int(part)
                    if i + 1 < len(parts):
                        unit = parts[i + 1]
                    break
            
            if number and unit:
                if "day" in unit:
                    return reference_date - timedelta(days=number)
                elif "week" in unit:
                    return reference_date - timedelta(weeks=number)
                elif "month" in unit:
                    return reference_date - relativedelta(months=number)
                elif "year" in unit:
                    return reference_date - relativedelta(years=number)
        
        # If can't parse, try to parse as ISO date
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except:
            # Default to 30 days ago if can't parse
            return reference_date - timedelta(days=30)
    
    def extract_parameters(self, query: str) -> ExtractedParameters:
        """
        Extract structured parameters from natural language query
        
        Args:
            query: Natural language query from user
            
        Returns:
            ExtractedParameters object with structured data
        """
        
        # System prompt for parameter extraction
        system_prompt = """You are an expert at extracting structured parameters from Earth observation queries.

Extract the following information from the user's query:
1. event_type: Must be one of "flood", "vegetation", or "generic"
2. state: Indian state name (normalize to proper case)
3. district: District name if mentioned (optional)
4. start_date: Start date in YYYY-MM-DD format
5. end_date: End date in YYYY-MM-DD format
6. confidence: Your confidence in the extraction (0.0 to 1.0)

For relative dates like "past 2 weeks", "last month", calculate from today's date.
Today's date is: """ + str(date.today()) + """

Event type classification rules:
- "flood", "flooding", "inundation", "water logging" → flood
- "vegetation", "crop", "NDVI", "greenness", "crop stress", "agriculture" → vegetation
- "dataset", "available data", "satellite coverage", "data availability" → generic

Return ONLY a valid JSON object with these exact keys:
{
    "event_type": "flood|vegetation|generic",
    "state": "State Name",
    "district": "District Name or null",
    "start_date": "YYYY-MM-DD",
    "end_date": "YYYY-MM-DD",
    "confidence": 0.95
}"""

        try:
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            # Parse response
            content = response.choices[0].message.content
            extracted_data = json.loads(content)
            
            # Handle relative dates in the extracted data
            start_date_str = extracted_data.get("start_date", "")
            end_date_str = extracted_data.get("end_date", "")
            
            # If dates look like relative expressions, resolve them
            if not start_date_str or "past" in start_date_str.lower() or "last" in start_date_str.lower():
                start_date = self._resolve_relative_dates(start_date_str if start_date_str else "past 30 days")
            else:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
                
            if not end_date_str or end_date_str == start_date_str:
                end_date = date.today()
            else:
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            
            # Create ExtractedParameters object
            params = ExtractedParameters(
                event_type=EventType(extracted_data["event_type"]),
                state=extracted_data["state"],
                district=extracted_data.get("district"),
                start_date=start_date,
                end_date=end_date,
                confidence=extracted_data.get("confidence", 0.9)
            )
            
            return params
            
        except Exception as e:
            # If extraction fails, raise with helpful error
            raise ValueError(f"Failed to extract parameters from query: {str(e)}")
    
    def validate_extraction(self, params: ExtractedParameters) -> Dict[str, Any]:
        """
        Validate extracted parameters and return validation result
        
        Returns:
            Dict with 'valid' boolean and 'errors' list
        """
        errors = []
        
        # Check if dates are valid
        if params.start_date > params.end_date:
            errors.append("Start date cannot be after end date")
        
        # Check if dates are not too far in the future
        if params.end_date > date.today() + timedelta(days=7):
            errors.append("End date cannot be more than 7 days in the future")
        
        # Check if date range is reasonable (not more than 2 years)
        date_diff = (params.end_date - params.start_date).days
        if date_diff > 730:
            errors.append("Date range cannot exceed 2 years")
        
        # Check confidence threshold
        if params.confidence < 0.5:
            errors.append("Low confidence in parameter extraction. Please rephrase your query.")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }


# Singleton instance
_extractor_instance = None

def get_extractor() -> LLMParameterExtractor:
    """Get singleton instance of LLM extractor"""
    global _extractor_instance
    if _extractor_instance is None:
        _extractor_instance = LLMParameterExtractor()
    return _extractor_instance
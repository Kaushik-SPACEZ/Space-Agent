"""
Intent classification service
Routes queries to appropriate pipelines based on extracted parameters
"""
from typing import Optional, Dict, Any
from models.schemas import ExtractedParameters, EventType


class IntentClassifier:
    """Classify intent and route to appropriate pipeline"""
    
    def __init__(self):
        # Pipeline mapping
        self.pipeline_map = {
            EventType.FLOOD: "flood",
            EventType.VEGETATION: "vegetation",
            EventType.GENERIC: "generic"
        }
    
    def classify_intent(self, params: ExtractedParameters) -> str:
        """
        Classify the intent and return pipeline name
        
        Args:
            params: Extracted parameters from query
            
        Returns:
            Pipeline name (flood, vegetation, generic)
        """
        return self.pipeline_map.get(params.event_type, "generic")
    
    def validate_params(self, params: ExtractedParameters) -> Dict[str, Any]:
        """
        Validate parameters for the classified intent
        
        Returns:
            Dict with 'valid' boolean and 'message' string
        """
        # Check required fields
        if not params.state:
            return {
                "valid": False,
                "message": "State name is required. Please specify an Indian state."
            }
        
        if not params.start_date or not params.end_date:
            return {
                "valid": False,
                "message": "Date range is required. Please specify start and end dates."
            }
        
        # Check confidence threshold
        if params.confidence < 0.6:
            return {
                "valid": False,
                "message": "Unable to understand your query clearly. Please rephrase with more specific details."
            }
        
        return {
            "valid": True,
            "message": "Parameters validated successfully"
        }
    
    def get_clarification_prompt(self, params: ExtractedParameters) -> Optional[str]:
        """
        Generate clarification prompt if needed
        
        Returns:
            Clarification question or None
        """
        if params.confidence < 0.7:
            if params.event_type == EventType.FLOOD:
                return "Did you mean flood monitoring or water body analysis?"
            elif params.event_type == EventType.VEGETATION:
                return "Did you mean crop monitoring or vegetation health analysis?"
        
        return None


# Singleton instance
_classifier_instance = None

def get_classifier() -> IntentClassifier:
    """Get singleton instance of intent classifier"""
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = IntentClassifier()
    return _classifier_instance
"""
Earth Agent - Main orchestrator for Earth observation queries
Routes queries to appropriate pipelines
"""
from typing import Dict, Any, Optional
from datetime import datetime
import os

from models.schemas import (
    QueryInput, 
    ExtractedParameters, 
    PipelineResponse, 
    ErrorResponse,
    EventType
)
from services.llm_extractor import get_extractor
from services.intent_classifier import get_classifier
from pipelines.flood_pipeline import FloodPipeline
from pipelines.vegetation_pipeline import VegetationPipeline
from pipelines.generic_pipeline import GenericPipeline
from pipelines.base_pipeline import BasePipeline


class EarthAgent:
    """
    Main Earth Observation Agent
    Orchestrates the entire query processing pipeline
    """
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        
        # Initialize services
        self.extractor = get_extractor()
        self.classifier = get_classifier()
        
        # Initialize pipeline registry
        self.pipelines: Dict[str, BasePipeline] = {
            "flood": FloodPipeline(data_dir),
            "vegetation": VegetationPipeline(data_dir),
            "generic": GenericPipeline(data_dir)
        }
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Main entry point for processing user queries
        
        Args:
            query: Natural language query from user
            
        Returns:
            Dict containing either PipelineResponse or ErrorResponse
        """
        try:
            # Step 1: Extract parameters from query using LLM
            params = self.extractor.extract_parameters(query)
            
            # Step 2: Validate extraction
            validation = self.extractor.validate_extraction(params)
            if not validation["valid"]:
                return self._create_error_response(
                    error="; ".join(validation["errors"]),
                    error_type="validation_error"
                )
            
            # Step 3: Classify intent and get pipeline name
            pipeline_name = self.classifier.classify_intent(params)
            
            # Step 4: Validate parameters for the pipeline
            param_validation = self.classifier.validate_params(params)
            if not param_validation["valid"]:
                return self._create_error_response(
                    error=param_validation["message"],
                    error_type="invalid_parameters"
                )
            
            # Step 5: Route to appropriate pipeline
            pipeline = self.route_to_pipeline(pipeline_name)
            
            # Step 6: Process query through pipeline
            response = pipeline.process(params)
            
            # Step 7: Return successful response
            return {
                "success": True,
                "data": response.model_dump(),
                "query_info": {
                    "original_query": query,
                    "extracted_params": params.model_dump(),
                    "pipeline_used": pipeline_name
                }
            }
            
        except ValueError as e:
            # Handle data not found errors
            error_msg = str(e)
            
            # Try to provide helpful suggestions
            suggestion = None
            available_options = None
            
            if "No data found" in error_msg:
                try:
                    # Get available date ranges for the state
                    pipeline = self.route_to_pipeline(pipeline_name)
                    date_ranges = pipeline.get_available_date_ranges(params.state)
                    
                    if date_ranges:
                        available_options = [
                            f"{dr['start']} to {dr['end']}" for dr in date_ranges[:5]
                        ]
                        suggestion = f"Try querying data for one of these available date ranges"
                except:
                    pass
            
            return self._create_error_response(
                error=error_msg,
                error_type="no_data_found",
                suggestion=suggestion,
                available_options=available_options
            )
            
        except Exception as e:
            # Handle unexpected errors
            return self._create_error_response(
                error=f"An unexpected error occurred: {str(e)}",
                error_type="internal_error"
            )
    
    def route_to_pipeline(self, pipeline_name: str) -> BasePipeline:
        """
        Route to the appropriate pipeline based on classification
        
        Args:
            pipeline_name: Name of the pipeline (flood, vegetation, generic)
            
        Returns:
            Pipeline instance
        """
        pipeline = self.pipelines.get(pipeline_name)
        
        if pipeline is None:
            raise ValueError(f"Unknown pipeline: {pipeline_name}")
        
        return pipeline
    
    def register_pipeline(self, name: str, pipeline: BasePipeline):
        """
        Register a new pipeline (for extensibility)
        
        Args:
            name: Pipeline name
            pipeline: Pipeline instance
        """
        self.pipelines[name] = pipeline
    
    def _create_error_response(
        self, 
        error: str, 
        error_type: str,
        suggestion: Optional[str] = None,
        available_options: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Create standardized error response
        """
        error_response = ErrorResponse(
            error=error,
            error_type=error_type,
            suggestion=suggestion,
            available_options=available_options
        )
        
        return {
            "success": False,
            "error": error_response.model_dump()
        }
    
    def get_pipeline_info(self) -> Dict[str, Any]:
        """
        Get information about available pipelines
        """
        return {
            "available_pipelines": list(self.pipelines.keys()),
            "pipeline_descriptions": {
                "flood": "Flood monitoring and extent analysis",
                "vegetation": "Vegetation health and crop monitoring (NDVI)",
                "generic": "General dataset availability and metadata"
            }
        }
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on the agent and all pipelines
        """
        health = {
            "agent_status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "pipelines": {}
        }
        
        # Check each pipeline
        for name, pipeline in self.pipelines.items():
            try:
                # Try to load dataset
                pipeline.load_dataset()
                health["pipelines"][name] = {
                    "status": "healthy",
                    "dataset_loaded": True
                }
            except Exception as e:
                health["pipelines"][name] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
                health["agent_status"] = "degraded"
        
        return health


# Singleton instance
_agent_instance = None

def get_agent(data_dir: str = "data") -> EarthAgent:
    """Get singleton instance of Earth Agent"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = EarthAgent(data_dir)
    return _agent_instance

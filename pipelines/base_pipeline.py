"""
Base pipeline abstract class
All pipelines must inherit from this class
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import pandas as pd
from datetime import datetime
import os

from models.schemas import ExtractedParameters, PipelineResponse, LocationInfo, TimeRange


class BasePipeline(ABC):
    """Abstract base class for all Earth observation pipelines"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.dataset: Optional[pd.DataFrame] = None
        self.pipeline_name = self.__class__.__name__.replace("Pipeline", "").lower()
    
    @abstractmethod
    def load_dataset(self) -> pd.DataFrame:
        """
        Load the dataset for this pipeline
        Must be implemented by subclasses
        """
        pass
    
    @abstractmethod
    def query_dataset(self, params: ExtractedParameters) -> pd.DataFrame:
        """
        Query the dataset based on extracted parameters
        Must be implemented by subclasses
        """
        pass
    
    @abstractmethod
    def format_response(self, data: pd.DataFrame, params: ExtractedParameters) -> PipelineResponse:
        """
        Format the query results into standardized response
        Must be implemented by subclasses
        """
        pass
    
    def validate_params(self, params: ExtractedParameters) -> bool:
        """
        Validate parameters for this pipeline
        Can be overridden by subclasses for specific validation
        """
        if not params.state:
            return False
        if not params.start_date or not params.end_date:
            return False
        return True
    
    def process(self, params: ExtractedParameters) -> PipelineResponse:
        """
        Main processing method - orchestrates the pipeline
        
        Args:
            params: Extracted parameters from query
            
        Returns:
            PipelineResponse with results
        """
        start_time = datetime.now()
        
        # Validate parameters
        if not self.validate_params(params):
            raise ValueError("Invalid parameters for pipeline")
        
        # Load dataset if not already loaded
        if self.dataset is None:
            self.dataset = self.load_dataset()
        
        # Query dataset
        results = self.query_dataset(params)
        
        # Check if results are empty
        if results.empty:
            raise ValueError(f"No data found for {params.state} between {params.start_date} and {params.end_date}")
        
        # Format response
        response = self.format_response(results, params)
        
        # Add metadata
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        response.metadata.update({
            "processing_time_ms": round(processing_time, 2),
            "pipeline": self.pipeline_name,
            "records_found": len(results)
        })
        
        return response
    
    def _create_location_info(self, params: ExtractedParameters, lat: Optional[float] = None, 
                             lon: Optional[float] = None) -> LocationInfo:
        """Helper to create LocationInfo object"""
        location = LocationInfo(
            state=params.state,
            district=params.district
        )
        if lat is not None and lon is not None:
            location.coordinates = {"lat": lat, "lon": lon}
        return location
    
    def _create_time_range(self, params: ExtractedParameters) -> TimeRange:
        """Helper to create TimeRange object"""
        duration = (params.end_date - params.start_date).days
        return TimeRange(
            start=params.start_date,
            end=params.end_date,
            duration_days=duration
        )
    
    def _create_geojson_point(self, lat: float, lon: float, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Helper to create GeoJSON point feature"""
        return {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [lon, lat]
            },
            "properties": properties
        }
    
    def _create_geojson_collection(self, features: list) -> Dict[str, Any]:
        """Helper to create GeoJSON FeatureCollection"""
        return {
            "type": "FeatureCollection",
            "features": features
        }
    
    def get_available_date_ranges(self, state: str) -> list:
        """
        Get available date ranges for a given state
        Useful for error messages
        """
        if self.dataset is None:
            self.dataset = self.load_dataset()
        
        state_data = self.dataset[self.dataset['state'].str.lower() == state.lower()]
        
        if state_data.empty:
            return []
        
        # Convert to datetime if needed
        if not pd.api.types.is_datetime64_any_dtype(state_data['start_date']):
            state_data['start_date'] = pd.to_datetime(state_data['start_date'])
            state_data['end_date'] = pd.to_datetime(state_data['end_date'])
        
        date_ranges = []
        for _, row in state_data.iterrows():
            date_ranges.append({
                "start": row['start_date'].strftime("%Y-%m-%d"),
                "end": row['end_date'].strftime("%Y-%m-%d")
            })
        
        return date_ranges
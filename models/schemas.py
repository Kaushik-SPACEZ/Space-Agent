"""
Data models and schemas for Earth Observation Agent
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List, Literal
from datetime import datetime, date
from enum import Enum


class EventType(str, Enum):
    """Supported event types"""
    FLOOD = "flood"
    VEGETATION = "vegetation"
    GENERIC = "generic"


class QueryInput(BaseModel):
    """Raw user query input"""
    query: str = Field(..., description="Natural language query from user")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "Show flood in Tamil Nadu past 2 weeks"
            }
        }


class ExtractedParameters(BaseModel):
    """Structured parameters extracted from user query by LLM"""
    event_type: EventType = Field(..., description="Type of Earth observation event")
    state: str = Field(..., description="Indian state name")
    district: Optional[str] = Field(None, description="District name (optional)")
    start_date: date = Field(..., description="Start date for query")
    end_date: date = Field(..., description="End date for query")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Extraction confidence score")
    
    @validator('state')
    def validate_state(cls, v):
        """Normalize state names"""
        return v.strip().title()
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_type": "flood",
                "state": "Tamil Nadu",
                "district": "Chennai",
                "start_date": "2024-01-15",
                "end_date": "2024-01-29",
                "confidence": 0.95
            }
        }


class LocationInfo(BaseModel):
    """Location information"""
    state: str
    district: Optional[str] = None
    coordinates: Optional[Dict[str, float]] = None  # {"lat": x, "lon": y}


class TimeRange(BaseModel):
    """Time range information"""
    start: date
    end: date
    duration_days: Optional[int] = None


class FloodDetails(BaseModel):
    """Flood-specific details"""
    flooded_area_sqkm: float = Field(..., description="Flooded area in square kilometers")
    resolution: str = Field(..., description="Satellite resolution (e.g., '10m')")
    acquisition_time: datetime = Field(..., description="Satellite data acquisition time")
    confidence: float = Field(default=0.9, ge=0.0, le=1.0)
    affected_districts: Optional[List[str]] = None
    water_level_change_m: Optional[float] = None


class VegetationDetails(BaseModel):
    """Vegetation/crop monitoring details"""
    vegetation_index_type: str = Field(default="NDVI", description="Type of vegetation index")
    mean_ndvi: float = Field(..., ge=-1.0, le=1.0, description="Mean NDVI value")
    min_ndvi: float = Field(..., ge=-1.0, le=1.0)
    max_ndvi: float = Field(..., ge=-1.0, le=1.0)
    bands_used: List[str] = Field(default=["Red", "NIR"], description="Spectral bands used")
    scene_count: int = Field(..., description="Number of satellite scenes available")
    crop_stress_detected: bool = Field(default=False)
    resolution: str = Field(..., description="Satellite resolution")


class GenericDatasetDetails(BaseModel):
    """Generic dataset availability details"""
    available_datasets: List[str] = Field(..., description="List of available dataset types")
    satellites: List[str] = Field(..., description="Available satellites")
    date_range_available: Dict[str, str] = Field(..., description="Available date ranges")
    total_scenes: int = Field(..., description="Total number of scenes available")
    data_types: List[str] = Field(..., description="Types of data available")


class PipelineResponse(BaseModel):
    """Standardized response format from all pipelines"""
    report_type: str = Field(..., description="Type of report (flood_monitoring, vegetation_monitoring, etc.)")
    location: LocationInfo
    time_range: TimeRange
    satellite: str = Field(..., description="Primary satellite used")
    details: Dict[str, Any] = Field(..., description="Pipeline-specific details")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Processing metadata")
    geojson: Optional[Dict[str, Any]] = Field(None, description="GeoJSON representation if applicable")
    
    class Config:
        json_schema_extra = {
            "example": {
                "report_type": "flood_monitoring",
                "location": {
                    "state": "Tamil Nadu",
                    "district": "Chennai"
                },
                "time_range": {
                    "start": "2024-01-15",
                    "end": "2024-01-29",
                    "duration_days": 14
                },
                "satellite": "Sentinel-1",
                "details": {
                    "flooded_area_sqkm": 245.6,
                    "resolution": "10m",
                    "acquisition_time": "2024-01-28T10:30:00Z",
                    "confidence": 0.92
                },
                "metadata": {
                    "processing_time_ms": 234,
                    "data_source": "flood_data.csv",
                    "pipeline": "flood"
                }
            }
        }


class ErrorResponse(BaseModel):
    """Error response format"""
    error: str
    error_type: str
    suggestion: Optional[str] = None
    available_options: Optional[List[str]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "No data found for the specified time range",
                "error_type": "no_data_found",
                "suggestion": "Try querying between 2023-06-01 and 2024-01-31",
                "available_options": ["2023-06-15 to 2023-06-30", "2023-12-01 to 2023-12-15"]
            }
        }


# Dataset models for CSV data
class FloodDataRecord(BaseModel):
    """Flood dataset record"""
    state: str
    district: Optional[str]
    start_date: date
    end_date: date
    flooded_area_sqkm: float
    satellite: str
    resolution: str
    acquisition_time: datetime
    confidence: float
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class VegetationDataRecord(BaseModel):
    """Vegetation dataset record"""
    state: str
    district: Optional[str]
    start_date: date
    end_date: date
    mean_ndvi: float
    min_ndvi: float
    max_ndvi: float
    satellite: str
    resolution: str
    scene_count: int
    crop_stress_detected: bool
    latitude: Optional[float] = None
    longitude: Optional[float] = None
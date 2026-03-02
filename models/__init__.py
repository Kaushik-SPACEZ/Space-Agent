"""
Data models and schemas for Earth Observation Agent
"""
from models.schemas import (
    QueryInput,
    ExtractedParameters,
    PipelineResponse,
    ErrorResponse,
    EventType,
    LocationInfo,
    TimeRange,
    FloodDetails,
    VegetationDetails,
    GenericDatasetDetails
)

__all__ = [
    "QueryInput",
    "ExtractedParameters",
    "PipelineResponse",
    "ErrorResponse",
    "EventType",
    "LocationInfo",
    "TimeRange",
    "FloodDetails",
    "VegetationDetails",
    "GenericDatasetDetails"
]
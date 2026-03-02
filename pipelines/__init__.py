"""
Pipelines for Earth Observation Agent
"""
from pipelines.base_pipeline import BasePipeline
from pipelines.flood_pipeline import FloodPipeline
from pipelines.vegetation_pipeline import VegetationPipeline
from pipelines.generic_pipeline import GenericPipeline

__all__ = [
    "BasePipeline",
    "FloodPipeline",
    "VegetationPipeline",
    "GenericPipeline"
]
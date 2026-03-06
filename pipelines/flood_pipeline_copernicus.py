"""
Enhanced Flood Pipeline with Copernicus Integration
Queries real Sentinel-1 satellite data for flood monitoring
"""
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any
import logging

from services.copernicus_api import copernicus_api

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FloodPipelineCopernicus:
    """
    Enhanced flood pipeline that queries real Copernicus Sentinel-1 data
    """
    
    def __init__(self):
        self.api = copernicus_api
    
    def query_floods(self, state: str, start_date: str = None, end_date: str = None, days_back: int = 30) -> Dict[str, Any]:
        """
        Query flood data for a specific state
        
        Args:
            state: Indian state name (e.g., "Tamil Nadu", "Bihar")
            start_date: Start date (YYYY-MM-DD) - optional
            end_date: End date (YYYY-MM-DD) - optional  
            days_back: Number of days to look back if dates not provided
            
        Returns:
            Dictionary with Sentinel-1 scenes and metadata
        """
        try:
            # Calculate date range
            if not end_date:
                end_date = datetime.now()
            else:
                end_date = datetime.strptime(end_date, "%Y-%m-%d")
            
            if not start_date:
                start_date = end_date - timedelta(days=days_back)
            else:
                start_date = datetime.strptime(start_date, "%Y-%m-%d")
            
            # Get bounding box for state
            bbox = self.api.get_indian_state_bbox(state)
            
            logger.info(f"Querying Copernicus for {state}: {start_date.date()} to {end_date.date()}")
            
            # Query Copernicus STAC API
            results = self.api.search_stac_floods(
                bbox=bbox,
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d"),
                collections=["sentinel-1-grd"],
                limit=20
            )
            
            features = results.get("features", [])
            
            if not features:
                return {
                    "status": "success",
                    "message": f"No Sentinel-1 data found for {state} in the specified date range",
                    "data": [],
                    "metadata": {
                        "state": state,
                        "date_range": f"{start_date.date()} to {end_date.date()}",
                        "total_scenes": 0
                    }
                }
            
            # Format results
            formatted_scenes = []
            for feature in features:
                props = feature.get("properties", {})
                formatted_scenes.append({
                    "scene_id": feature.get("id"),
                    "state": state,
                    "acquisition_date": props.get("datetime"),
                    "platform": props.get("platform", "N/A"),
                    "instrument_mode": props.get("sar:instrument_mode", "N/A"),
                    "polarization": props.get("sar:polarizations", []),
                    "orbit_direction": props.get("sat:orbit_state", "N/A"),
                    "data_type": "Sentinel-1 SAR (Flood Detection)",
                    "bbox": feature.get("bbox"),
                    "geometry": feature.get("geometry"),
                    "description": f"SAR data suitable for flood detection - water appears dark in SAR images"
                })
            
            return {
                "status": "success",
                "data": formatted_scenes,
                "metadata": {
                    "state": state,
                    "date_range": f"{start_date.date()} to {end_date.date()}",
                    "total_scenes": len(formatted_scenes),
                    "data_source": "Copernicus Sentinel-1 GRD",
                    "satellite": "Sentinel-1",
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error querying floods: {e}")
            return {
                "status": "error",
                "error": str(e),
                "data": []
            }
    
    def get_latest_scene(self, state: str) -> Dict[str, Any]:
        """Get the most recent Sentinel-1 scene for a state"""
        result = self.query_floods(state, days_back=7)
        
        if result["status"] == "success" and result["data"]:
            return {
                "status": "success",
                "data": result["data"][0],
                "metadata": result["metadata"]
            }
        return result
    
    def compare_dates(self, state: str, date1: str, date2: str) -> Dict[str, Any]:
        """
        Get scenes for two different dates for before/after comparison
        Useful for flood event analysis
        """
        # Get scene for date 1
        result1 = self.query_floods(state, start_date=date1, end_date=date1, days_back=1)
        
        # Get scene for date 2  
        result2 = self.query_floods(state, start_date=date2, end_date=date2, days_back=1)
        
        return {
            "status": "success",
            "before": result1.get("data", []),
            "after": result2.get("data", []),
            "metadata": {
                "state": state,
                "date1": date1,
                "date2": date2,
                "purpose": "before_after_flood_comparison"
            }
        }


# Singleton instance
_pipeline_instance = None

def get_flood_pipeline() -> FloodPipelineCopernicus:
    """Get singleton instance of flood pipeline"""
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = FloodPipelineCopernicus()
    return _pipeline_instance
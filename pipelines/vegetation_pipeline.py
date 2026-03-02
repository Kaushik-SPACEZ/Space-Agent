"""
Vegetation/Crop monitoring pipeline
Handles NDVI and crop health queries
"""
import pandas as pd
from datetime import datetime
from typing import Dict, Any

from pipelines.base_pipeline import BasePipeline
from models.schemas import (
    ExtractedParameters, 
    PipelineResponse, 
    VegetationDetails
)


class VegetationPipeline(BasePipeline):
    """Pipeline for vegetation and crop monitoring"""
    
    def __init__(self, data_dir: str = "data"):
        super().__init__(data_dir)
        self.dataset_file = f"{data_dir}/vegetation_data.csv"
    
    def load_dataset(self) -> pd.DataFrame:
        """Load vegetation dataset from CSV"""
        df = pd.read_csv(self.dataset_file)
        
        # Convert date columns to datetime
        df['start_date'] = pd.to_datetime(df['start_date'])
        df['end_date'] = pd.to_datetime(df['end_date'])
        
        return df
    
    def query_dataset(self, params: ExtractedParameters) -> pd.DataFrame:
        """
        Query vegetation dataset based on parameters
        
        Filters by:
        - State (required)
        - District (optional)
        - Date range overlap
        """
        df = self.dataset.copy()
        
        # Filter by state (case-insensitive)
        df = df[df['state'].str.lower() == params.state.lower()]
        
        # Filter by district if provided
        if params.district:
            df = df[df['district'].str.lower() == params.district.lower()]
        
        # Filter by date range - find records that overlap with query range
        query_start = pd.Timestamp(params.start_date)
        query_end = pd.Timestamp(params.end_date)
        
        df = df[
            (df['start_date'] <= query_end) & 
            (df['end_date'] >= query_start)
        ]
        
        # Sort by start date (most recent first)
        df = df.sort_values('start_date', ascending=False)
        
        return df
    
    def format_response(self, data: pd.DataFrame, params: ExtractedParameters) -> PipelineResponse:
        """
        Format vegetation data into standardized response with GeoJSON
        """
        # Get the most recent record
        latest_record = data.iloc[0]
        
        # Calculate average NDVI across all records
        avg_mean_ndvi = data['mean_ndvi'].mean()
        overall_min_ndvi = data['min_ndvi'].min()
        overall_max_ndvi = data['max_ndvi'].max()
        
        # Check for crop stress
        crop_stress_detected = data['crop_stress_detected'].any()
        
        # Total scene count
        total_scenes = data['scene_count'].sum()
        
        # Create vegetation details
        veg_details = VegetationDetails(
            vegetation_index_type="NDVI",
            mean_ndvi=round(avg_mean_ndvi, 3),
            min_ndvi=round(overall_min_ndvi, 3),
            max_ndvi=round(overall_max_ndvi, 3),
            bands_used=["Red", "NIR"],
            scene_count=int(total_scenes),
            crop_stress_detected=bool(crop_stress_detected),
            resolution=latest_record['resolution']
        )
        
        # Create location info
        location = self._create_location_info(
            params,
            lat=latest_record.get('latitude'),
            lon=latest_record.get('longitude')
        )
        
        # Create time range
        time_range = self._create_time_range(params)
        
        # Create GeoJSON features for all vegetation records
        geojson_features = []
        for _, row in data.iterrows():
            if pd.notna(row.get('latitude')) and pd.notna(row.get('longitude')):
                feature = self._create_geojson_point(
                    lat=row['latitude'],
                    lon=row['longitude'],
                    properties={
                        "state": row['state'],
                        "district": row['district'],
                        "mean_ndvi": round(row['mean_ndvi'], 3),
                        "crop_stress_detected": bool(row['crop_stress_detected']),
                        "satellite": row['satellite'],
                        "scene_count": int(row['scene_count']),
                        "date_range": f"{row['start_date'].strftime('%Y-%m-%d')} to {row['end_date'].strftime('%Y-%m-%d')}"
                    }
                )
                geojson_features.append(feature)
        
        geojson = self._create_geojson_collection(geojson_features) if geojson_features else None
        
        # Create response
        response = PipelineResponse(
            report_type="vegetation_monitoring",
            location=location,
            time_range=time_range,
            satellite=latest_record['satellite'],
            details=veg_details.model_dump(),
            geojson=geojson,
            metadata={
                "data_source": "vegetation_data.csv",
                "total_records": len(data),
                "crop_health_status": self._assess_crop_health(avg_mean_ndvi, crop_stress_detected)
            }
        )
        
        return response
    
    def _assess_crop_health(self, mean_ndvi: float, stress_detected: bool) -> str:
        """
        Assess overall crop health based on NDVI values
        
        NDVI ranges:
        - < 0.2: Bare soil, no vegetation
        - 0.2 - 0.5: Sparse vegetation, stressed crops
        - 0.5 - 0.7: Moderate vegetation, healthy crops
        - > 0.7: Dense vegetation, very healthy crops
        """
        if stress_detected:
            return "Crop stress detected - requires attention"
        
        if mean_ndvi < 0.2:
            return "No significant vegetation detected"
        elif mean_ndvi < 0.5:
            return "Sparse vegetation - potential stress"
        elif mean_ndvi < 0.7:
            return "Healthy vegetation"
        else:
            return "Very healthy, dense vegetation"
    
    def get_vegetation_statistics(self, params: ExtractedParameters) -> Dict[str, Any]:
        """
        Get additional vegetation statistics for the query
        """
        results = self.query_dataset(params)
        
        if results.empty:
            return {}
        
        return {
            "total_records": len(results),
            "average_ndvi": round(results['mean_ndvi'].mean(), 3),
            "ndvi_range": {
                "min": round(results['min_ndvi'].min(), 3),
                "max": round(results['max_ndvi'].max(), 3)
            },
            "crop_stress_percentage": round(
                (results['crop_stress_detected'].sum() / len(results)) * 100, 1
            ),
            "total_scenes_available": int(results['scene_count'].sum()),
            "districts_monitored": results['district'].dropna().unique().tolist(),
            "satellites_used": results['satellite'].unique().tolist(),
            "date_range": {
                "earliest": results['start_date'].min().strftime("%Y-%m-%d"),
                "latest": results['end_date'].max().strftime("%Y-%m-%d")
            }
        }
    
    def get_ndvi_trend(self, params: ExtractedParameters) -> Dict[str, Any]:
        """
        Get NDVI trend over time for the query
        """
        results = self.query_dataset(params)
        
        if results.empty:
            return {}
        
        # Sort by date
        results = results.sort_values('start_date')
        
        trend_data = []
        for _, row in results.iterrows():
            trend_data.append({
                "date": row['start_date'].strftime("%Y-%m-%d"),
                "mean_ndvi": round(row['mean_ndvi'], 3),
                "crop_stress": bool(row['crop_stress_detected'])
            })
        
        # Calculate trend direction
        if len(trend_data) > 1:
            first_ndvi = trend_data[0]['mean_ndvi']
            last_ndvi = trend_data[-1]['mean_ndvi']
            trend_direction = "improving" if last_ndvi > first_ndvi else "declining"
        else:
            trend_direction = "stable"
        
        return {
            "trend_data": trend_data,
            "trend_direction": trend_direction,
            "total_data_points": len(trend_data)
        }
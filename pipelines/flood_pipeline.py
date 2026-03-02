"""
Flood monitoring pipeline
Handles flood-related queries and returns flood extent data
"""
import pandas as pd
from datetime import datetime
from typing import Dict, Any

from pipelines.base_pipeline import BasePipeline
from models.schemas import (
    ExtractedParameters, 
    PipelineResponse, 
    FloodDetails
)


class FloodPipeline(BasePipeline):
    """Pipeline for flood monitoring and analysis"""
    
    def __init__(self, data_dir: str = "data"):
        super().__init__(data_dir)
        self.dataset_file = f"{data_dir}/flood_data.csv"
    
    def load_dataset(self) -> pd.DataFrame:
        """Load flood dataset from CSV"""
        df = pd.read_csv(self.dataset_file)
        
        # Convert date columns to datetime
        df['start_date'] = pd.to_datetime(df['start_date'])
        df['end_date'] = pd.to_datetime(df['end_date'])
        df['acquisition_time'] = pd.to_datetime(df['acquisition_time'])
        
        return df
    
    def query_dataset(self, params: ExtractedParameters) -> pd.DataFrame:
        """
        Query flood dataset based on parameters
        
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
        # A record overlaps if: record_start <= query_end AND record_end >= query_start
        query_start = pd.Timestamp(params.start_date)
        query_end = pd.Timestamp(params.end_date)
        
        df = df[
            (df['start_date'] <= query_end) & 
            (df['end_date'] >= query_start)
        ]
        
        # Sort by acquisition time (most recent first)
        df = df.sort_values('acquisition_time', ascending=False)
        
        return df
    
    def format_response(self, data: pd.DataFrame, params: ExtractedParameters) -> PipelineResponse:
        """
        Format flood data into standardized response with GeoJSON
        """
        # Get the most recent record
        latest_record = data.iloc[0]
        
        # Calculate total flooded area if multiple records
        total_flooded_area = data['flooded_area_sqkm'].sum()
        
        # Get affected districts
        affected_districts = data['district'].dropna().unique().tolist()
        
        # Create flood details
        flood_details = FloodDetails(
            flooded_area_sqkm=round(total_flooded_area, 2),
            resolution=latest_record['resolution'],
            acquisition_time=latest_record['acquisition_time'],
            confidence=latest_record['confidence'],
            affected_districts=affected_districts if affected_districts else None
        )
        
        # Create location info
        location = self._create_location_info(
            params,
            lat=latest_record.get('latitude'),
            lon=latest_record.get('longitude')
        )
        
        # Create time range
        time_range = self._create_time_range(params)
        
        # Create GeoJSON features for all flood events
        geojson_features = []
        for _, row in data.iterrows():
            if pd.notna(row.get('latitude')) and pd.notna(row.get('longitude')):
                feature = self._create_geojson_point(
                    lat=row['latitude'],
                    lon=row['longitude'],
                    properties={
                        "state": row['state'],
                        "district": row['district'],
                        "flooded_area_sqkm": row['flooded_area_sqkm'],
                        "satellite": row['satellite'],
                        "acquisition_time": row['acquisition_time'].isoformat(),
                        "confidence": row['confidence']
                    }
                )
                geojson_features.append(feature)
        
        geojson = self._create_geojson_collection(geojson_features) if geojson_features else None
        
        # Create response
        response = PipelineResponse(
            report_type="flood_monitoring",
            location=location,
            time_range=time_range,
            satellite=latest_record['satellite'],
            details=flood_details.model_dump(),
            geojson=geojson,
            metadata={
                "data_source": "flood_data.csv",
                "total_events": len(data)
            }
        )
        
        return response
    
    def get_flood_statistics(self, params: ExtractedParameters) -> Dict[str, Any]:
        """
        Get additional flood statistics for the query
        """
        results = self.query_dataset(params)
        
        if results.empty:
            return {}
        
        return {
            "total_events": len(results),
            "total_area_affected_sqkm": round(results['flooded_area_sqkm'].sum(), 2),
            "average_area_per_event": round(results['flooded_area_sqkm'].mean(), 2),
            "max_single_event_area": round(results['flooded_area_sqkm'].max(), 2),
            "affected_districts": results['district'].dropna().unique().tolist(),
            "satellites_used": results['satellite'].unique().tolist(),
            "date_range": {
                "earliest": results['start_date'].min().strftime("%Y-%m-%d"),
                "latest": results['end_date'].max().strftime("%Y-%m-%d")
            }
        }
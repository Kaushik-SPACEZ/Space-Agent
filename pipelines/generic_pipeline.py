"""
Generic dataset query pipeline
Returns available satellite data and metadata for a location and time range
"""
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List
import os

from pipelines.base_pipeline import BasePipeline
from models.schemas import (
    ExtractedParameters, 
    PipelineResponse, 
    GenericDatasetDetails
)


class GenericPipeline(BasePipeline):
    """Pipeline for generic dataset availability queries"""
    
    def __init__(self, data_dir: str = "data"):
        super().__init__(data_dir)
        self.flood_file = f"{data_dir}/flood_data.csv"
        self.vegetation_file = f"{data_dir}/vegetation_data.csv"
    
    def load_dataset(self) -> pd.DataFrame:
        """
        Load all available datasets and combine metadata
        """
        datasets = []
        
        # Load flood data
        if os.path.exists(self.flood_file):
            flood_df = pd.read_csv(self.flood_file)
            flood_df['dataset_type'] = 'flood'
            flood_df['start_date'] = pd.to_datetime(flood_df['start_date'])
            flood_df['end_date'] = pd.to_datetime(flood_df['end_date'])
            datasets.append(flood_df)
        
        # Load vegetation data
        if os.path.exists(self.vegetation_file):
            veg_df = pd.read_csv(self.vegetation_file)
            veg_df['dataset_type'] = 'vegetation'
            veg_df['start_date'] = pd.to_datetime(veg_df['start_date'])
            veg_df['end_date'] = pd.to_datetime(veg_df['end_date'])
            datasets.append(veg_df)
        
        # Combine all datasets
        if datasets:
            combined_df = pd.concat(datasets, ignore_index=True)
            return combined_df
        else:
            return pd.DataFrame()
    
    def query_dataset(self, params: ExtractedParameters) -> pd.DataFrame:
        """
        Query all datasets for availability in the specified location and time range
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
        
        return df
    
    def format_response(self, data: pd.DataFrame, params: ExtractedParameters) -> PipelineResponse:
        """
        Format generic dataset availability into standardized response
        """
        # Get unique dataset types
        available_datasets = data['dataset_type'].unique().tolist()
        
        # Get unique satellites
        satellites = data['satellite'].unique().tolist()
        
        # Get date range for each dataset type
        date_ranges = {}
        for dataset_type in available_datasets:
            type_data = data[data['dataset_type'] == dataset_type]
            date_ranges[dataset_type] = {
                "earliest": type_data['start_date'].min().strftime("%Y-%m-%d"),
                "latest": type_data['end_date'].max().strftime("%Y-%m-%d"),
                "total_records": len(type_data)
            }
        
        # Count total scenes
        total_scenes = len(data)
        
        # Determine data types available
        data_types = []
        if 'flood' in available_datasets:
            data_types.extend(['SAR', 'Flood Extent', 'Water Body Detection'])
        if 'vegetation' in available_datasets:
            data_types.extend(['Optical', 'NDVI', 'Vegetation Index', 'Crop Monitoring'])
        
        # Create generic dataset details
        generic_details = GenericDatasetDetails(
            available_datasets=available_datasets,
            satellites=satellites,
            date_range_available=date_ranges,
            total_scenes=total_scenes,
            data_types=list(set(data_types))  # Remove duplicates
        )
        
        # Get a representative record for location
        latest_record = data.iloc[0] if not data.empty else None
        
        # Create location info
        location = self._create_location_info(
            params,
            lat=latest_record.get('latitude') if latest_record is not None else None,
            lon=latest_record.get('longitude') if latest_record is not None else None
        )
        
        # Create time range
        time_range = self._create_time_range(params)
        
        # Create GeoJSON features for dataset coverage
        geojson_features = []
        for dataset_type in available_datasets:
            type_data = data[data['dataset_type'] == dataset_type]
            
            # Get representative location for this dataset type
            for _, row in type_data.head(5).iterrows():  # Limit to 5 per type
                if pd.notna(row.get('latitude')) and pd.notna(row.get('longitude')):
                    feature = self._create_geojson_point(
                        lat=row['latitude'],
                        lon=row['longitude'],
                        properties={
                            "dataset_type": row['dataset_type'],
                            "state": row['state'],
                            "district": row['district'],
                            "satellite": row['satellite'],
                            "date_range": f"{row['start_date'].strftime('%Y-%m-%d')} to {row['end_date'].strftime('%Y-%m-%d')}"
                        }
                    )
                    geojson_features.append(feature)
        
        geojson = self._create_geojson_collection(geojson_features) if geojson_features else None
        
        # Create response
        response = PipelineResponse(
            report_type="dataset_availability",
            location=location,
            time_range=time_range,
            satellite=", ".join(satellites),
            details=generic_details.model_dump(),
            geojson=geojson,
            metadata={
                "data_sources": ["flood_data.csv", "vegetation_data.csv"],
                "query_type": "generic_availability"
            }
        )
        
        return response
    
    def get_dataset_summary(self, params: ExtractedParameters) -> Dict[str, Any]:
        """
        Get detailed summary of available datasets
        """
        results = self.query_dataset(params)
        
        if results.empty:
            return {
                "message": "No datasets available for the specified location and time range"
            }
        
        summary = {
            "total_records": len(results),
            "datasets": {}
        }
        
        # Summarize each dataset type
        for dataset_type in results['dataset_type'].unique():
            type_data = results[results['dataset_type'] == dataset_type]
            
            summary["datasets"][dataset_type] = {
                "record_count": len(type_data),
                "satellites": type_data['satellite'].unique().tolist(),
                "date_range": {
                    "start": type_data['start_date'].min().strftime("%Y-%m-%d"),
                    "end": type_data['end_date'].max().strftime("%Y-%m-%d")
                },
                "districts_covered": type_data['district'].dropna().unique().tolist(),
                "resolutions": type_data['resolution'].unique().tolist()
            }
        
        return summary
    
    def get_satellite_coverage(self, state: str) -> Dict[str, Any]:
        """
        Get satellite coverage information for a specific state
        """
        if self.dataset is None:
            self.dataset = self.load_dataset()
        
        state_data = self.dataset[self.dataset['state'].str.lower() == state.lower()]
        
        if state_data.empty:
            return {
                "message": f"No satellite coverage data available for {state}"
            }
        
        coverage = {
            "state": state,
            "satellites": {},
            "total_coverage_records": len(state_data)
        }
        
        # Summarize by satellite
        for satellite in state_data['satellite'].unique():
            sat_data = state_data[state_data['satellite'] == satellite]
            
            coverage["satellites"][satellite] = {
                "record_count": len(sat_data),
                "dataset_types": sat_data['dataset_type'].unique().tolist(),
                "date_range": {
                    "earliest": sat_data['start_date'].min().strftime("%Y-%m-%d"),
                    "latest": sat_data['end_date'].max().strftime("%Y-%m-%d")
                },
                "resolution": sat_data['resolution'].unique().tolist()
            }
        
        return coverage
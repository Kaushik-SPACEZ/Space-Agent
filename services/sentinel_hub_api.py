"""
Sentinel Hub Catalog API Integration
Implements STAC-based API for searching satellite data archives
"""

import os
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SentinelHubAPI:
    """
    Client for Sentinel Hub Catalog API
    Implements STAC specification for geospatial data search
    """
    
    def __init__(self):
        self.base_url = "https://services.sentinel-hub.com/api/v1/catalog"
        self.oauth_url = "https://services.sentinel-hub.com/oauth/token"
        self.client_id = os.getenv("SENTINEL_HUB_CLIENT_ID")
        self.client_secret = os.getenv("SENTINEL_HUB_CLIENT_SECRET")
        self.access_token = None
        
    def authenticate(self) -> bool:
        """
        Authenticate with Sentinel Hub OAuth2
        Returns True if successful
        """
        if not self.client_id or not self.client_secret:
            logger.warning("Sentinel Hub credentials not configured")
            return False
            
        try:
            response = requests.post(
                self.oauth_url,
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret
                }
            )
            response.raise_for_status()
            self.access_token = response.json()["access_token"]
            logger.info("Successfully authenticated with Sentinel Hub")
            return True
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication"""
        if not self.access_token:
            self.authenticate()
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def search_stac(
        self,
        bbox: List[float],
        datetime_range: str,
        collections: List[str],
        limit: int = 10,
        query: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Search for satellite data using STAC API
        
        Args:
            bbox: Bounding box [west, south, east, north] in WGS84
            datetime_range: ISO 8601 datetime or range (e.g., "2023-01-01/2023-12-31")
            collections: List of collection IDs (e.g., ["sentinel-2-l2a"])
            limit: Maximum number of results
            query: Additional query parameters
            
        Returns:
            STAC FeatureCollection with search results
        """
        search_url = f"{self.base_url}/search"
        
        payload = {
            "bbox": bbox,
            "datetime": datetime_range,
            "collections": collections,
            "limit": limit
        }
        
        if query:
            payload["query"] = query
        
        try:
            response = requests.post(
                search_url,
                json=payload,
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"STAC search failed: {e}")
            return {"type": "FeatureCollection", "features": []}
    
    def get_collections(self) -> List[Dict[str, Any]]:
        """
        Get available data collections
        
        Returns:
            List of STAC collection objects
        """
        collections_url = f"{self.base_url}/collections"
        
        try:
            response = requests.get(
                collections_url,
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json().get("collections", [])
        except Exception as e:
            logger.error(f"Failed to fetch collections: {e}")
            return []
    
    def get_collection(self, collection_id: str) -> Optional[Dict[str, Any]]:
        """
        Get details for a specific collection
        
        Args:
            collection_id: Collection identifier (e.g., "sentinel-2-l2a")
            
        Returns:
            STAC collection object or None
        """
        collection_url = f"{self.base_url}/collections/{collection_id}"
        
        try:
            response = requests.get(
                collection_url,
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to fetch collection {collection_id}: {e}")
            return None
    
    def search_sentinel2(
        self,
        bbox: List[float],
        start_date: str,
        end_date: str,
        max_cloud_cover: float = 30.0,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Convenience method to search Sentinel-2 L2A data
        
        Args:
            bbox: Bounding box [west, south, east, north]
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            max_cloud_cover: Maximum cloud coverage percentage
            limit: Maximum number of results
            
        Returns:
            STAC FeatureCollection with Sentinel-2 scenes
        """
        datetime_range = f"{start_date}/{end_date}"
        
        query = {
            "eo:cloud_cover": {
                "lte": max_cloud_cover
            }
        }
        
        return self.search_stac(
            bbox=bbox,
            datetime_range=datetime_range,
            collections=["sentinel-2-l2a"],
            limit=limit,
            query=query
        )
    
    def search_sentinel1(
        self,
        bbox: List[float],
        start_date: str,
        end_date: str,
        orbit_direction: Optional[str] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Convenience method to search Sentinel-1 SAR data
        
        Args:
            bbox: Bounding box [west, south, east, north]
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            orbit_direction: "ASCENDING" or "DESCENDING"
            limit: Maximum number of results
            
        Returns:
            STAC FeatureCollection with Sentinel-1 scenes
        """
        datetime_range = f"{start_date}/{end_date}"
        
        query = {}
        if orbit_direction:
            query["sat:orbit_state"] = {"eq": orbit_direction}
        
        return self.search_stac(
            bbox=bbox,
            datetime_range=datetime_range,
            collections=["sentinel-1-grd"],
            limit=limit,
            query=query if query else None
        )
    
    def get_feature_info(self, feature: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract useful information from a STAC feature
        
        Args:
            feature: STAC feature from search results
            
        Returns:
            Simplified feature information
        """
        properties = feature.get("properties", {})
        
        return {
            "id": feature.get("id"),
            "datetime": properties.get("datetime"),
            "cloud_cover": properties.get("eo:cloud_cover"),
            "platform": properties.get("platform"),
            "instrument": properties.get("instruments", []),
            "bbox": feature.get("bbox"),
            "geometry": feature.get("geometry"),
            "assets": list(feature.get("assets", {}).keys())
        }


class ODataAPI:
    """
    Client for OData-based interface
    Similar to Copernicus data access protocols
    """
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        
    def query(
        self,
        collection: str,
        filters: Optional[Dict[str, Any]] = None,
        select: Optional[List[str]] = None,
        top: int = 100
    ) -> Dict[str, Any]:
        """
        Query OData endpoint
        
        Args:
            collection: Collection/entity name
            filters: OData filter expressions
            select: Fields to select
            top: Maximum number of results
            
        Returns:
            Query results
        """
        url = f"{self.base_url}/{collection}"
        params = {"$top": top}
        
        if filters:
            filter_expr = " and ".join([f"{k} eq '{v}'" for k, v in filters.items()])
            params["$filter"] = filter_expr
            
        if select:
            params["$select"] = ",".join(select)
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"OData query failed: {e}")
            return {"value": []}


class OpenSearchAPI:
    """
    Client for OpenSearch REST service
    Compatible with existing platforms
    """
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        
    def search(
        self,
        bbox: Optional[List[float]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        platform: Optional[str] = None,
        max_records: int = 10
    ) -> Dict[str, Any]:
        """
        Search using OpenSearch parameters
        
        Args:
            bbox: Bounding box [west, south, east, north]
            start_date: Start date
            end_date: End date
            platform: Platform name
            max_records: Maximum results
            
        Returns:
            Search results in GeoJSON format
        """
        params = {"maxRecords": max_records}
        
        if bbox:
            params["bbox"] = ",".join(map(str, bbox))
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        if platform:
            params["platform"] = platform
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"OpenSearch query failed: {e}")
            return {"features": []}


# Singleton instances
sentinel_hub_api = SentinelHubAPI()
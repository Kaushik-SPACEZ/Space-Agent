"""
Copernicus Data Space Ecosystem API Integration
For accessing Sentinel-1 and Sentinel-2 data for flood monitoring

Based on the APIs shown in the Copernicus documentation:
- OData API: Metadata search and data download
- STAC API: Earth observation community standard
- OpenSearch API: REST service for compatibility
"""

import os
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class CopernicusDataSpaceAPI:
    """
    Client for Copernicus Data Space Ecosystem
    Focuses on flood monitoring with Sentinel-1 SAR data
    """
    
    def __init__(self):
        # Copernicus Data Space endpoints (Updated to new STAC v1)
        self.odata_url = "https://catalogue.dataspace.copernicus.eu/odata/v1"
        self.stac_url = "https://stac.dataspace.copernicus.eu/v1"  # NEW STAC v1 endpoint
        self.auth_url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
        self.stac_browser_url = "https://browser.stac.dataspace.copernicus.eu"
        
        # Credentials from environment
        self.username = os.getenv("COPERNICUS_USERNAME")
        self.password = os.getenv("COPERNICUS_PASSWORD")
        self.access_token = None
        
    def authenticate(self) -> bool:
        """
        Authenticate with Copernicus Data Space
        Returns True if successful
        """
        if not self.username or not self.password:
            logger.warning("Copernicus credentials not configured")
            return False
            
        try:
            response = requests.post(
                self.auth_url,
                data={
                    "grant_type": "password",
                    "username": self.username,
                    "password": self.password,
                    "client_id": "cdse-public"
                },
                timeout=30
            )
            response.raise_for_status()
            self.access_token = response.json()["access_token"]
            logger.info("Successfully authenticated with Copernicus Data Space")
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
    
    def search_sentinel1_floods(
        self,
        bbox: List[float],
        start_date: str,
        end_date: str,
        product_type: str = "GRD",
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Search for Sentinel-1 SAR data for flood monitoring
        
        Args:
            bbox: Bounding box [west, south, east, north] in WGS84
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            product_type: "GRD" (Ground Range Detected) or "SLC" (Single Look Complex)
            limit: Maximum number of results
            
        Returns:
            Search results with Sentinel-1 scenes
        """
        try:
            # Build OData query for Sentinel-1
            # Format: POLYGON((lon lat, lon lat, ...))
            polygon = f"POLYGON(({bbox[0]} {bbox[1]}, {bbox[2]} {bbox[1]}, {bbox[2]} {bbox[3]}, {bbox[0]} {bbox[3]}, {bbox[0]} {bbox[1]}))"
            
            query = f"{self.odata_url}/Products?$filter="
            query += f"Collection/Name eq 'SENTINEL-1' and "
            query += f"Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'productType' and att/OData.CSC.StringAttribute/Value eq '{product_type}') and "
            query += f"ContentDate/Start ge {start_date}T00:00:00.000Z and "
            query += f"ContentDate/Start le {end_date}T23:59:59.999Z and "
            query += f"OData.CSC.Intersects(area=geography'SRID=4326;{polygon}')"
            query += f"&$top={limit}"
            query += "&$expand=Attributes"
            
            response = requests.get(query, headers=self._get_headers(), timeout=60)
            response.raise_for_status()
            
            results = response.json()
            return self._parse_odata_results(results)
            
        except Exception as e:
            logger.error(f"Sentinel-1 search failed: {e}")
            return {"features": [], "count": 0}
    
    def search_stac_floods(
        self,
        bbox: List[float],
        start_date: str,
        end_date: str,
        collections: List[str] = ["sentinel-1-grd"],
        limit: int = 10,
        additional_filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Search using STAC API v1 for flood monitoring data
        Uses the new Copernicus STAC endpoint with Filter Extension support
        
        Args:
            bbox: Bounding box [west, south, east, north]
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            collections: List of collection IDs (e.g., ["sentinel-1-grd"])
            limit: Maximum results
            additional_filters: Additional CQL2 filters (e.g., {"sar:instrument_mode": {"eq": "IW"}})
            
        Returns:
            STAC FeatureCollection
        """
        try:
            search_url = f"{self.stac_url}/search"
            
            payload = {
                "bbox": bbox,
                "datetime": f"{start_date}T00:00:00Z/{end_date}T23:59:59Z",
                "collections": collections,
                "limit": limit
            }
            
            # Add additional filters if provided (using Query Extension)
            if additional_filters:
                payload["query"] = additional_filters
            
            response = requests.post(
                search_url,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"STAC search failed: {e}")
            return {"type": "FeatureCollection", "features": []}
    
    def get_product_download_url(self, product_id: str) -> Optional[str]:
        """
        Get download URL for a specific product
        
        Args:
            product_id: Product ID from search results
            
        Returns:
            Download URL or None
        """
        try:
            query = f"{self.odata_url}/Products({product_id})/$value"
            return query
        except Exception as e:
            logger.error(f"Failed to get download URL: {e}")
            return None
    
    def _parse_odata_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Parse OData results into simplified format"""
        features = []
        
        for item in results.get("value", []):
            # Extract attributes
            attributes = {}
            for attr in item.get("Attributes", []):
                attr_name = attr.get("Name")
                attr_value = attr.get("Value")
                if attr_name and attr_value:
                    attributes[attr_name] = attr_value
            
            feature = {
                "id": item.get("Id"),
                "name": item.get("Name"),
                "product_type": attributes.get("productType"),
                "acquisition_date": item.get("ContentDate", {}).get("Start"),
                "orbit_direction": attributes.get("orbitDirection"),
                "polarization": attributes.get("polarisation"),
                "sensor_mode": attributes.get("sensorMode"),
                "geometry": item.get("GeoFootprint"),
                "size_mb": item.get("ContentLength", 0) / (1024 * 1024),
                "download_url": f"{self.odata_url}/Products({item.get('Id')})/$value",
                "metadata": item
            }
            features.append(feature)
        
        return {
            "features": features,
            "count": len(features),
            "total": results.get("@odata.count", len(features))
        }
    
    def get_collections(self) -> List[Dict[str, Any]]:
        """
        Get all available STAC collections
        
        Returns:
            List of STAC collections
        """
        try:
            collections_url = f"{self.stac_url}/collections"
            response = requests.get(collections_url, timeout=30)
            response.raise_for_status()
            return response.json().get("collections", [])
        except Exception as e:
            logger.error(f"Failed to fetch collections: {e}")
            return []
    
    def get_collection(self, collection_id: str) -> Optional[Dict[str, Any]]:
        """
        Get details for a specific collection
        
        Args:
            collection_id: Collection ID (e.g., "sentinel-1-grd", "sentinel-2-l2a")
            
        Returns:
            Collection details or None
        """
        try:
            collection_url = f"{self.stac_url}/collections/{collection_id}"
            response = requests.get(collection_url, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to fetch collection {collection_id}: {e}")
            return None
    
    def get_queryables(self, collection_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get queryable attributes for filtering
        
        Args:
            collection_id: Optional collection ID to get specific queryables
            
        Returns:
            Queryable attributes
        """
        try:
            if collection_id:
                url = f"{self.stac_url}/collections/{collection_id}/queryables"
            else:
                url = f"{self.stac_url}/queryables"
            
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to fetch queryables: {e}")
            return {}
    
    def search_with_cql2_filter(
        self,
        collections: List[str],
        cql2_filter: str,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Search using CQL2 filter (Filter Extension)
        
        Args:
            collections: List of collection IDs
            cql2_filter: CQL2 text filter expression
            limit: Maximum results
            
        Example:
            cql2_filter = "eo:cloud_cover <= 10 AND datetime >= TIMESTAMP('2024-01-01T00:00:00Z')"
            
        Returns:
            STAC FeatureCollection
        """
        try:
            search_url = f"{self.stac_url}/search"
            
            payload = {
                "collections": collections,
                "filter-lang": "cql2-text",
                "filter": cql2_filter,
                "limit": limit
            }
            
            response = requests.post(
                search_url,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"CQL2 filter search failed: {e}")
            return {"type": "FeatureCollection", "features": []}
    
    def get_indian_state_bbox(self, state: str) -> List[float]:
        """
        Get bounding box for Indian states (for flood monitoring)
        Returns [west, south, east, north]
        """
        state_boxes = {
            # Flood-prone states
            "Assam": [89.7, 24.0, 96.0, 28.0],
            "Bihar": [83.3, 24.3, 88.3, 27.5],
            "West Bengal": [85.8, 21.5, 89.9, 27.2],
            "Uttar Pradesh": [77.0, 23.9, 84.6, 30.4],
            "Kerala": [74.8, 8.2, 77.4, 12.8],
            "Tamil Nadu": [76.2, 8.0, 80.3, 13.6],
            "Karnataka": [74.0, 11.5, 78.6, 18.5],
            "Maharashtra": [72.6, 15.6, 80.9, 22.0],
            "Andhra Pradesh": [76.7, 12.6, 84.8, 19.9],
            "Odisha": [81.3, 17.8, 87.5, 22.6],
            "Gujarat": [68.2, 20.1, 74.5, 24.7],
            "Rajasthan": [69.5, 23.0, 78.3, 30.2],
            "Madhya Pradesh": [74.0, 21.1, 82.8, 26.9],
            "Chhattisgarh": [80.3, 17.8, 84.4, 24.1],
            "Jharkhand": [83.3, 21.9, 87.9, 25.3],
            "Punjab": [73.9, 29.5, 76.9, 32.6],
            "Haryana": [74.5, 27.7, 77.6, 30.9],
            "Uttarakhand": [77.6, 28.7, 81.0, 31.5],
            "Himachal Pradesh": [75.6, 30.4, 79.0, 33.2]
        }
        
        return state_boxes.get(state, [68.0, 8.0, 97.5, 35.5])  # Default: All India


# Singleton instance
copernicus_api = CopernicusDataSpaceAPI()
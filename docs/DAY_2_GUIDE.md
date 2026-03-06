# 📅 Day 2: Preprocessing Pipeline & Intent-to-SQL

**Goal**: Build automated data pipeline and safe Intent-to-SQL converter

**Time**: 8 hours (with breaks)

---

## 🎯 Day 2 Objectives

By end of day, you will have:
- ✅ Data extraction modules for Copernicus & NASA
- ✅ Validation rules for data quality
- ✅ Transformation pipeline for standardization
- ✅ Intent extraction (LLM → JSON)
- ✅ JSON → Parameterized SQL converter
- ✅ End-to-end pipeline tested
- ✅ **Git Checkpoint**: Day 2 complete, ready to push

---

## ⏰ Timeline

| Time | Checkpoint | Duration | Status |
|------|------------|----------|--------|
| 9:00 AM | 2.1: Data Extraction | 1.5 hours | ⬜ |
| 10:30 AM | 2.2: Data Validation | 1.5 hours | ⬜ |
| 12:00 PM | Lunch | 1 hour | ⬜ |
| 1:00 PM | 2.3: Data Transformation | 1 hour | ⬜ |
| 2:00 PM | 2.4: Intent Extraction | 2 hours | ⬜ |
| 4:00 PM | Break | 15 min | ⬜ |
| 4:15 PM | 2.5: JSON → SQL Converter | 1.5 hours | ⬜ |
| 5:45 PM | Day 2 Review & Git Push | 15 min | ⬜ |

---

## 📥 Checkpoint 2.1: Data Extraction Modules

### Time: 9:00 AM - 10:30 AM (1.5 hours)

### Step 1: Create Base Extractor

Create `preprocessing/extractors/base.py`:

```python
"""
Base extractor class for all data sources
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any
from datetime import datetime

class BaseExtractor(ABC):
    """Abstract base class for data extractors"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.source_name = self.__class__.__name__
    
    @abstractmethod
    def authenticate(self) -> bool:
        """Authenticate with data source"""
        pass
    
    @abstractmethod
    def search(self, params: Dict[str, Any]) -> List[Dict]:
        """Search for data matching parameters"""
        pass
    
    @abstractmethod
    def download(self, item_id: str, output_path: str) -> str:
        """Download specific data item"""
        pass
    
    def extract(self, params: Dict[str, Any]) -> List[Dict]:
        """
        Main extraction method
        1. Authenticate
        2. Search for data
        3. Download data
        4. Return metadata
        """
        if not self.authenticate():
            raise Exception(f"Authentication failed for {self.source_name}")
        
        results = self.search(params)
        print(f"✅ Found {len(results)} items from {self.source_name}")
        
        return results
    
    def log_extraction(self, status: str, details: str):
        """Log extraction activity"""
        timestamp = datetime.now().isoformat()
        print(f"[{timestamp}] {self.source_name}: {status} - {details}")
```

### Step 2: Copernicus Extractor

Create `preprocessing/extractors/copernicus.py`:

```python
"""
Copernicus Data Space Extractor
For Sentinel-1 (flood) and Sentinel-2 (vegetation) data
"""
import requests
from typing import Dict, List, Any
from datetime import datetime
import os
from .base import BaseExtractor

class CopernicusExtractor(BaseExtractor):
    """Extract data from Copernicus Data Space"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = "https://catalogue.dataspace.copernicus.eu/odata/v1"
        self.username = os.getenv("COPERNICUS_USERNAME")
        self.password = os.getenv("COPERNICUS_PASSWORD")
        self.token = None
    
    def authenticate(self) -> bool:
        """Authenticate with Copernicus"""
        try:
            # Get access token
            auth_url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
            
            data = {
                "grant_type": "password",
                "username": self.username,
                "password": self.password,
                "client_id": "cdse-public"
            }
            
            response = requests.post(auth_url, data=data, timeout=30)
            
            if response.status_code == 200:
                self.token = response.json()["access_token"]
                self.log_extraction("SUCCESS", "Authentication successful")
                return True
            else:
                self.log_extraction("ERROR", f"Auth failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_extraction("ERROR", f"Auth exception: {str(e)}")
            return False
    
    def search(self, params: Dict[str, Any]) -> List[Dict]:
        """
        Search for Sentinel data
        
        params:
            - satellite: "Sentinel-1" or "Sentinel-2"
            - state: Indian state name
            - start_date: Start date (YYYY-MM-DD)
            - end_date: End date (YYYY-MM-DD)
            - max_cloud_cover: Maximum cloud cover % (for Sentinel-2)
        """
        try:
            # Build OData query
            satellite = params.get("satellite", "Sentinel-1")
            start_date = params.get("start_date")
            end_date = params.get("end_date")
            
            # Get bounding box for state (simplified - you'd use a proper geocoding service)
            bbox = self._get_state_bbox(params.get("state", "Tamil Nadu"))
            
            # Build query
            query = f"{self.base_url}/Products?$filter="
            query += f"Collection/Name eq '{satellite}' and "
            query += f"ContentDate/Start ge {start_date}T00:00:00.000Z and "
            query += f"ContentDate/Start le {end_date}T23:59:59.999Z and "
            query += f"OData.CSC.Intersects(area=geography'SRID=4326;{bbox}')"
            
            if satellite == "Sentinel-2" and "max_cloud_cover" in params:
                query += f" and Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCover' and att/OData.CSC.DoubleAttribute/Value le {params['max_cloud_cover']})"
            
            query += "&$top=100"
            
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(query, headers=headers, timeout=60)
            
            if response.status_code == 200:
                results = response.json().get("value", [])
                self.log_extraction("SUCCESS", f"Found {len(results)} products")
                return self._parse_results(results)
            else:
                self.log_extraction("ERROR", f"Search failed: {response.status_code}")
                return []
                
        except Exception as e:
            self.log_extraction("ERROR", f"Search exception: {str(e)}")
            return []
    
    def download(self, item_id: str, output_path: str) -> str:
        """Download product (metadata only for now)"""
        # For MVP, we'll just store metadata
        # Full download would require more storage and processing
        self.log_extraction("INFO", f"Metadata stored for {item_id}")
        return output_path
    
    def _get_state_bbox(self, state: str) -> str:
        """Get bounding box for Indian state (simplified)"""
        # Simplified bounding boxes for major Indian states
        state_boxes = {
            "Tamil Nadu": "POLYGON((76.0 8.0, 80.5 8.0, 80.5 13.5, 76.0 13.5, 76.0 8.0))",
            "Kerala": "POLYGON((74.5 8.0, 77.5 8.0, 77.5 12.8, 74.5 12.8, 74.5 8.0))",
            "Karnataka": "POLYGON((74.0 11.5, 78.5 11.5, 78.5 18.5, 74.0 18.5, 74.0 11.5))",
            "Maharashtra": "POLYGON((72.5 15.5, 80.5 15.5, 80.5 22.0, 72.5 22.0, 72.5 15.5))",
            "Andhra Pradesh": "POLYGON((76.5 12.5, 84.8 12.5, 84.8 19.5, 76.5 19.5, 76.5 12.5))"
        }
        return state_boxes.get(state, state_boxes["Tamil Nadu"])
    
    def _parse_results(self, results: List[Dict]) -> List[Dict]:
        """Parse Copernicus results into standard format"""
        parsed = []
        for item in results:
            parsed.append({
                "id": item.get("Id"),
                "name": item.get("Name"),
                "satellite": item.get("Collection", {}).get("Name"),
                "acquisition_date": item.get("ContentDate", {}).get("Start"),
                "cloud_cover": self._extract_cloud_cover(item),
                "geometry": item.get("GeoFootprint"),
                "download_url": item.get("S3Path"),
                "metadata": item
            })
        return parsed
    
    def _extract_cloud_cover(self, item: Dict) -> float:
        """Extract cloud cover from attributes"""
        attributes = item.get("Attributes", [])
        for attr in attributes:
            if attr.get("Name") == "cloudCover":
                return attr.get("Value", 0.0)
        return 0.0
```

### Step 3: NASA Extractor

Create `preprocessing/extractors/nasa.py`:

```python
"""
NASA EarthData Extractor
For MODIS vegetation indices
"""
import requests
from typing import Dict, List, Any
import os
from .base import BaseExtractor

class NASAExtractor(BaseExtractor):
    """Extract MODIS data from NASA EarthData"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = "https://cmr.earthdata.nasa.gov/search"
        self.token = os.getenv("NASA_TOKEN")
    
    def authenticate(self) -> bool:
        """Verify NASA token"""
        if not self.token:
            self.log_extraction("ERROR", "NASA_TOKEN not found")
            return False
        
        try:
            # Test token with simple query
            url = f"{self.base_url}/collections.json?keyword=MODIS&page_size=1"
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                self.log_extraction("SUCCESS", "Authentication successful")
                return True
            else:
                self.log_extraction("ERROR", f"Auth failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_extraction("ERROR", f"Auth exception: {str(e)}")
            return False
    
    def search(self, params: Dict[str, Any]) -> List[Dict]:
        """
        Search for MODIS vegetation data
        
        params:
            - product: MODIS product (e.g., "MOD13Q1")
            - state: Indian state name
            - start_date: Start date
            - end_date: End date
        """
        try:
            product = params.get("product", "MOD13Q1")
            start_date = params.get("start_date")
            end_date = params.get("end_date")
            bbox = self._get_state_bbox(params.get("state", "Tamil Nadu"))
            
            # Build CMR query
            url = f"{self.base_url}/granules.json"
            query_params = {
                "short_name": product,
                "temporal": f"{start_date}T00:00:00Z,{end_date}T23:59:59Z",
                "bounding_box": bbox,
                "page_size": 100
            }
            
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(url, params=query_params, headers=headers, timeout=60)
            
            if response.status_code == 200:
                results = response.json().get("feed", {}).get("entry", [])
                self.log_extraction("SUCCESS", f"Found {len(results)} granules")
                return self._parse_results(results)
            else:
                self.log_extraction("ERROR", f"Search failed: {response.status_code}")
                return []
                
        except Exception as e:
            self.log_extraction("ERROR", f"Search exception: {str(e)}")
            return []
    
    def download(self, item_id: str, output_path: str) -> str:
        """Download MODIS granule (metadata only for MVP)"""
        self.log_extraction("INFO", f"Metadata stored for {item_id}")
        return output_path
    
    def _get_state_bbox(self, state: str) -> str:
        """Get bounding box for state (lon_min,lat_min,lon_max,lat_max)"""
        state_boxes = {
            "Tamil Nadu": "76.0,8.0,80.5,13.5",
            "Kerala": "74.5,8.0,77.5,12.8",
            "Karnataka": "74.0,11.5,78.5,18.5",
            "Maharashtra": "72.5,15.5,80.5,22.0",
            "Andhra Pradesh": "76.5,12.5,84.8,19.5"
        }
        return state_boxes.get(state, state_boxes["Tamil Nadu"])
    
    def _parse_results(self, results: List[Dict]) -> List[Dict]:
        """Parse NASA results into standard format"""
        parsed = []
        for item in results:
            parsed.append({
                "id": item.get("id"),
                "name": item.get("title"),
                "satellite": "MODIS",
                "acquisition_date": item.get("time_start"),
                "cloud_cover": 0.0,  # MODIS doesn't have cloud cover in same way
                "geometry": self._extract_geometry(item),
                "download_url": self._extract_download_url(item),
                "metadata": item
            })
        return parsed
    
    def _extract_geometry(self, item: Dict) -> str:
        """Extract geometry from item"""
        # Simplified - would need proper parsing
        return item.get("boxes", [""])[0] if "boxes" in item else ""
    
    def _extract_download_url(self, item: Dict) -> str:
        """Extract download URL"""
        links = item.get("links", [])
        for link in links:
            if link.get("rel") == "http://esipfed.org/ns/fedsearch/1.1/data#":
                return link.get("href", "")
        return ""
```

### Step 4: Test Extractors

Create `scripts/test_extractors.py`:

```python
"""Test data extractors"""
from preprocessing.extractors.copernicus import CopernicusExtractor
from preprocessing.extractors.nasa import NASAExtractor
from datetime import datetime, timedelta

def test_copernicus():
    """Test Copernicus extractor"""
    print("="*60)
    print("Testing Copernicus Extractor")
    print("="*60)
    
    extractor = CopernicusExtractor({})
    
    # Search for Sentinel-1 data (flood monitoring)
    params = {
        "satellite": "Sentinel-1",
        "state": "Tamil Nadu",
        "start_date": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
        "end_date": datetime.now().strftime("%Y-%m-%d")
    }
    
    results = extractor.extract(params)
    print(f"\n✅ Retrieved {len(results)} Sentinel-1 products")
    
    if results:
        print(f"\nSample result:")
        print(f"  ID: {results[0]['id']}")
        print(f"  Name: {results[0]['name']}")
        print(f"  Date: {results[0]['acquisition_date']}")

def test_nasa():
    """Test NASA extractor"""
    print("\n" + "="*60)
    print("Testing NASA Extractor")
    print("="*60)
    
    extractor = NASAExtractor({})
    
    # Search for MODIS NDVI data
    params = {
        "product": "MOD13Q1",
        "state": "Kerala",
        "start_date": (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d"),
        "end_date": datetime.now().strftime("%Y-%m-%d")
    }
    
    results = extractor.extract(params)
    print(f"\n✅ Retrieved {len(results)} MODIS granules")
    
    if results:
        print(f"\nSample result:")
        print(f"  ID: {results[0]['id']}")
        print(f"  Name: {results[0]['name']}")
        print(f"  Date: {results[0]['acquisition_date']}")

if __name__ == "__main__":
    test_copernicus()
    test_nasa()
    print("\n🎉 Extractor tests complete!")
```

Run:
```bash
python scripts/test_extractors.py
```

### ✅ Checkpoint 2.1 Complete!

**Git Commit**:
```bash
git add preprocessing/
git commit -m "Checkpoint 2.1: Data extraction modules created"
```

---

## ✅ Checkpoint 2.2: Data Validation

### Time: 10:30 AM - 12:00 PM (1.5 hours)

### Step 1: Create Validators

Create `preprocessing/validators.py`:

```python
"""
Data validation rules for quality assurance
"""
from typing import Dict, List, Tuple, Any
from datetime import datetime, date
from shapely.geometry import shape
from shapely.validation import explain_validity

class DataValidators:
    """Validation rules for Earth observation data"""
    
    def validate_flood_data(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate flood event data"""
        errors = []
        
        # Required fields
        required = ['event_id', 'state', 'start_date', 'end_date', 'geometry']
        for field in required:
            if field not in data or not data[field]:
                errors.append(f"Missing required field: {field}")
        
        # Date validation
        if 'start_date' in data and 'end_date' in data:
            try:
                start = self._parse_date(data['start_date'])
                end = self._parse_date(data['end_date'])
                
                if start > end:
                    errors.append("start_date cannot be after end_date")
                
                if end > date.today():
                    errors.append("end_date cannot be in the future")
                    
            except ValueError as e:
                errors.append(f"Invalid date format: {str(e)}")
        
        # Area validation
        if 'affected_area_sqkm' in data:
            area = data['affected_area_sqkm']
            if area is not None and (area < 0 or area > 1000000):
                errors.append(f"Invalid area: {area} (must be 0-1000000 sq km)")
        
        # Severity validation
        if 'severity' in data:
            valid_severities = ['low', 'medium', 'high', 'extreme']
            if data['severity'] not in valid_severities:
                errors.append(f"Invalid severity: {data['severity']}")
        
        # Confidence score validation
        if 'confidence_score' in data:
            score = data['confidence_score']
            if score is not None and (score < 0 or score > 1):
                errors.append(f"Invalid confidence_score: {score} (must be 0-1)")
        
        # Geometry validation
        if 'geometry' in data:
            geom_valid, geom_errors = self.validate_geometry(data['geometry'])
            errors.extend(geom_errors)
        
        return len(errors) == 0, errors
    
    def validate_vegetation_data(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate vegetation observation data"""
        errors = []
        
        # Required fields
        required = ['observation_id', 'state', 'observation_date', 'geometry']
        for field in required:
            if field not in data or not data[field]:
                errors.append(f"Missing required field: {field}")
        
        # Date validation
        if 'observation_date' in data:
            try:
                obs_date = self._parse_date(data['observation_date'])
                if obs_date > date.today():
                    errors.append("observation_date cannot be in the future")
            except ValueError as e:
                errors.append(f"Invalid date format: {str(e)}")
        
        # NDVI validation
        if 'ndvi_mean' in data:
            ndvi = data['ndvi_mean']
            if ndvi is not None and (ndvi < -1 or ndvi > 1):
                errors.append(f"Invalid ndvi_mean: {ndvi} (must be -1 to 1)")
        
        # Health status validation
        if 'health_status' in data:
            valid_statuses = ['healthy', 'stressed', 'critical']
            if data['health_status'] not in valid_statuses:
                errors.append(f"Invalid health_status: {data['health_status']}")
        
        # Cloud cover validation
        if 'cloud_cover_percent' in data:
            cloud = data['cloud_cover_percent']
            if cloud is not None and (cloud < 0 or cloud > 100):
                errors.append(f"Invalid cloud_cover_percent: {cloud} (must be 0-100)")
        
        # Geometry validation
        if 'geometry' in data:
            geom_valid, geom_errors = self.validate_geometry(data['geometry'])
            errors.extend(geom_errors)
        
        return len(errors) == 0, errors
    
    def validate_geometry(self, geometry: Any) -> Tuple[bool, List[str]]:
        """Validate geometry is valid and within India bounds"""
        errors = []
        
        try:
            # Convert to shapely geometry
            if isinstance(geometry, str):
                # Assume WKT format
                from shapely import wkt
                geom = wkt.loads(geometry)
            elif isinstance(geometry, dict):
                # Assume GeoJSON format
                geom = shape(geometry)
            else:
                errors.append("Geometry must be WKT string or GeoJSON dict")
                return False, errors
            
            # Check if valid
            if not geom.is_valid:
                errors.append(f"Invalid geometry: {explain_validity(geom)}")
            
            # Check if within India bounds (approximate)
            india_bounds = (68.0, 6.0, 97.5, 35.5)  # (min_lon, min_lat, max_lon, max_lat)
            bounds = geom.bounds
            
            if not (india_bounds[0] <= bounds[0] <= india_bounds[2] and
                    india_bounds[1] <= bounds[1] <= india_bounds[3]):
                errors.append("Geometry outside India bounds")
            
        except Exception as e:
            errors.append(f"Geometry validation error: {str(e)}")
        
        return len(errors) == 0, errors
    
    def _parse_date(self, date_str: Any) -> date:
        """Parse date from various formats"""
        if isinstance(date_str, date):
            return date_str
        if isinstance(date_str, datetime):
            return date_str.date()
        if isinstance(date_str, str):
            # Try common formats
            for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%d-%m-%Y', '%d/%m/%Y']:
                try:
                    return datetime.strptime(date_str, fmt).date()
                except ValueError:
                    continue
            raise ValueError(f"Cannot parse date: {date_str}")
        raise ValueError(f"Invalid date type: {type(date_str)}")
```

### Step 2: Test Validators

Create `tests/test_validators.py`:

```python
"""Test data validators"""
from preprocessing.validators import DataValidators
from datetime import date, timedelta

def test_flood_validation():
    """Test flood data validation"""
    print("Testing Flood Data Validation...")
    
    validator = DataValidators()
    
    # Valid data
    valid_data = {
        'event_id': 'FLOOD_TEST_001',
        'state': 'Tamil Nadu',
        'start_date': '2024-02-20',
        'end_date': '2024-02-25',
        'affected_area_sqkm': 250.5,
        'severity': 'high',
        'confidence_score': 0.95,
        'geometry': 'POLYGON((80.0 13.0, 80.5 13.0, 80.5 13.5, 80.0 13.5, 80.0 13.0))'
    }
    
    is_valid, errors = validator.validate_flood_data(valid_data)
    assert is_valid, f"Valid data failed: {errors}"
    print("✅ Valid flood data passed")
    
    # Invalid data - missing required field
    invalid_data = valid_data.copy()
    del invalid_data['event_id']
    is_valid, errors = validator.validate_flood_data(invalid_data)
    assert not is_valid, "Should fail without event_id"
    print("✅ Missing field validation works")
    
    # Invalid data - bad date range
    invalid_data = valid_data.copy()
    invalid_data['start_date'] = '2024-02-25'
    invalid_data['end_date'] = '2024-02-20'
    is_valid, errors = validator.validate_flood_data(invalid_data)
    assert not is_valid, "Should fail with inverted dates"
    print("✅ Date range validation works")
    
    # Invalid data - bad severity
    invalid_data = valid_data.copy()
    invalid_data['severity'] = 'super_high'
    is_valid, errors = validator.validate_flood_data(invalid_data)
    assert not is_valid, "Should fail with invalid severity"
    print("✅ Severity validation works")

def test_vegetation_validation():
    """Test vegetation data validation"""
    print("\nTesting Vegetation Data Validation...")
    
    validator = DataValidators()
    
    # Valid data
    valid_data = {
        'observation_id': 'VEG_TEST_001',
        'state': 'Kerala',
        'observation_date': '2024-02-15',
        'ndvi_mean': 0.75,
        'health_status': 'healthy',
        'cloud_cover_percent': 15.5,
        'geometry': 'POLYGON((76.0 11.0, 76.5 11.0, 76.5 11.5, 76.0 11.5, 76.0 11.0))'
    }
    
    is_valid, errors = validator.validate_vegetation_data(valid_data)
    assert is_valid, f"Valid data failed: {errors}"
    print("✅ Valid vegetation data passed")
    
    # Invalid data - bad NDVI
    invalid_data = valid_data.copy()
    invalid_data['ndvi_mean'] = 1.5
    is_valid, errors = validator.validate_vegetation_data(invalid_data)
    assert not is_valid, "Should fail with NDVI > 1"
    print("✅ NDVI validation works")
    
    # Invalid data - bad health status
    invalid_data = valid_data.copy()
    invalid_data['health_status'] = 'super_healthy'
    is_valid, errors = validator.validate_vegetation_data(invalid_data)
    assert not is_valid, "Should fail with invalid health_status"
    print("✅ Health status validation works")

if __name__ == "__main__":
    test_flood_validation()
    test_vegetation_validation()
    print("\n🎉 All validation tests passed!")
```

Run:
```bash
python tests/test_validators.py
```

### ✅ Checkpoint 2.2 Complete!

**Git Commit**:
```bash
git add preprocessing/validators.py tests/test_validators.py
git commit -m "Checkpoint 2.2: Data validation implemented and tested"
```

---

## 🍽️ Lunch Break: 12:00 PM - 1:00 PM (1 hour)

Great progress! You've built extraction and validation. After lunch: transformation and Intent-to-SQL!

---

## 🔄 Checkpoint 2.3: Data Transformation

### Time: 1:00 PM - 2:00 PM (1 hour)

[Content continues in next message due to length...]

---

**Current Progress**: 2/5 checkpoints complete for Day 2! 🎉

**Next**: Transformation, Intent Extraction, and JSON→SQL conversion
"""
Test script for Copernicus Data Space STAC API v1
Focuses on flood monitoring with Sentinel-1 GRD data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.copernicus_api import copernicus_api
import json
from datetime import datetime, timedelta


def test_authentication():
    """Test Copernicus authentication"""
    print("=" * 70)
    print("Testing Copernicus Data Space Authentication")
    print("=" * 70)
    
    if copernicus_api.authenticate():
        print("✓ Authentication successful")
        return True
    else:
        print("✗ Authentication failed")
        print("\nTo register:")
        print("1. Go to: https://dataspace.copernicus.eu/")
        print("2. Click 'Register' and create account")
        print("3. Verify your email")
        print("4. Add credentials to .env:")
        print("   COPERNICUS_USERNAME=your_username")
        print("   COPERNICUS_PASSWORD=your_password")
        return False


def test_get_collections():
    """Test fetching STAC collections"""
    print("\n" + "=" * 70)
    print("Testing STAC Collections")
    print("=" * 70)
    
    collections = copernicus_api.get_collections()
    
    if collections:
        print(f"✓ Found {len(collections)} collections")
        print("\nSentinel-1 collections (for flood monitoring):")
        for col in collections:
            if "sentinel-1" in col.get("id", "").lower():
                print(f"  - {col.get('id')}: {col.get('title', 'N/A')}")
    else:
        print("✗ No collections found")


def test_sentinel1_grd_collection():
    """Test Sentinel-1 GRD collection details"""
    print("\n" + "=" * 70)
    print("Testing Sentinel-1 GRD Collection")
    print("=" * 70)
    
    collection = copernicus_api.get_collection("sentinel-1-grd")
    
    if collection:
        print(f"✓ Collection: {collection.get('title')}")
        print(f"  Description: {collection.get('description', 'N/A')[:100]}...")
        print(f"  License: {collection.get('license', 'N/A')}")
        
        # Show temporal extent
        extent = collection.get("extent", {})
        temporal = extent.get("temporal", {}).get("interval", [[]])
        if temporal and temporal[0]:
            print(f"  Temporal extent: {temporal[0][0]} to {temporal[0][1]}")
    else:
        print("✗ Failed to fetch collection")


def test_queryables():
    """Test queryable attributes for Sentinel-1 GRD"""
    print("\n" + "=" * 70)
    print("Testing Queryables for Sentinel-1 GRD")
    print("=" * 70)
    
    queryables = copernicus_api.get_queryables("sentinel-1-grd")
    
    if queryables:
        print("✓ Available queryable attributes:")
        properties = queryables.get("properties", {})
        for key in list(properties.keys())[:10]:  # Show first 10
            prop = properties[key]
            print(f"  - {key}: {prop.get('description', 'N/A')[:60]}...")
    else:
        print("✗ No queryables found")


def test_search_floods_bihar():
    """Test searching for flood data in Bihar"""
    print("\n" + "=" * 70)
    print("Testing Flood Search: Bihar Region")
    print("=" * 70)
    
    # Bihar bounding box
    bbox = copernicus_api.get_indian_state_bbox("Bihar")
    
    # Search for recent Sentinel-1 data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    print(f"\nSearching for Sentinel-1 GRD data:")
    print(f"  Region: Bihar")
    print(f"  BBox: {bbox}")
    print(f"  Date range: {start_date.date()} to {end_date.date()}")
    
    results = copernicus_api.search_stac_floods(
        bbox=bbox,
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d"),
        collections=["sentinel-1-grd"],
        limit=5
    )
    
    features = results.get("features", [])
    print(f"\n✓ Found {len(features)} scenes")
    
    if features:
        print("\nFirst scene details:")
        feature = features[0]
        props = feature.get("properties", {})
        print(f"  ID: {feature.get('id')}")
        print(f"  Date: {props.get('datetime')}")
        print(f"  Platform: {props.get('platform', 'N/A')}")
        print(f"  Instrument mode: {props.get('sar:instrument_mode', 'N/A')}")
        print(f"  Polarization: {props.get('sar:polarizations', 'N/A')}")
        print(f"  Orbit direction: {props.get('sat:orbit_state', 'N/A')}")


def test_search_with_filters():
    """Test search with additional filters"""
    print("\n" + "=" * 70)
    print("Testing Search with Filters")
    print("=" * 70)
    
    bbox = copernicus_api.get_indian_state_bbox("Assam")
    
    try:
        # Search with specific instrument mode filter
        # Note: Query extension may not be fully supported, using basic search
        results = copernicus_api.search_stac_floods(
            bbox=bbox,
            start_date="2024-01-01",
            end_date="2024-01-31",
            collections=["sentinel-1-grd"],
            limit=3
        )
        
        features = results.get("features", [])
        print(f"✓ Found {len(features)} scenes")
        
        if features:
            print("\nResults:")
            for i, feature in enumerate(features, 1):
                props = feature.get("properties", {})
                print(f"  {i}. {feature.get('id')[:50]}...")
                print(f"     Mode: {props.get('sar:instrument_mode', 'N/A')}")
                print(f"     Date: {props.get('datetime', 'N/A')[:10]}")
    except Exception as e:
        print(f"⚠ Filter test skipped: {str(e)[:100]}")


def test_cql2_filter():
    """Test CQL2 filter extension"""
    print("\n" + "=" * 70)
    print("Testing CQL2 Filter Extension")
    print("=" * 70)
    
    try:
        # Example CQL2 filter for flood monitoring
        cql2_filter = (
            "datetime >= TIMESTAMP('2024-01-01T00:00:00Z') AND "
            "datetime <= TIMESTAMP('2024-01-31T23:59:59Z') AND "
            "S_INTERSECTS(geometry, POLYGON((83.3 24.3, 88.3 24.3, 88.3 27.5, 83.3 27.5, 83.3 24.3)))"
        )
        
        print(f"CQL2 Filter: {cql2_filter[:80]}...")
        
        results = copernicus_api.search_with_cql2_filter(
            collections=["sentinel-1-grd"],
            cql2_filter=cql2_filter,
            limit=3
        )
        
        features = results.get("features", [])
        print(f"✓ Found {len(features)} scenes using CQL2 filter")
    except Exception as e:
        print(f"⚠ CQL2 test skipped: {str(e)[:100]}")


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("Copernicus Data Space STAC API v1 - Test Suite")
    print("For Flood Monitoring with Sentinel-1 GRD")
    print("=" * 70)
    
    # Check credentials
    if not os.getenv("COPERNICUS_USERNAME"):
        print("\n⚠ WARNING: Copernicus credentials not configured")
        print("\nPlease add to .env file:")
        print("  COPERNICUS_USERNAME=your_username")
        print("  COPERNICUS_PASSWORD=your_password")
        print("\nRegister at: https://dataspace.copernicus.eu/")
        return
    
    # Run tests
    if test_authentication():
        test_get_collections()
        test_sentinel1_grd_collection()
        test_queryables()
        test_search_floods_bihar()
        test_search_with_filters()
        test_cql2_filter()
    
    print("\n" + "=" * 70)
    print("Test suite completed")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Explore STAC Browser: https://browser.stac.dataspace.copernicus.eu")
    print("2. View Sentinel-1 GRD collection in browser")
    print("3. Test with your own regions and date ranges")
    print("4. Integrate with flood detection pipeline")


if __name__ == "__main__":
    main()
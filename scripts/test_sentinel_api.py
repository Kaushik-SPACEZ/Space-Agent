"""
Test script for Sentinel Hub Catalog API integration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.sentinel_hub_api import SentinelHubAPI, sentinel_hub_api
import json


def test_authentication():
    """Test API authentication"""
    print("Testing Sentinel Hub authentication...")
    api = SentinelHubAPI()
    
    if api.authenticate():
        print("✓ Authentication successful")
        return True
    else:
        print("✗ Authentication failed - check credentials in .env")
        return False


def test_get_collections():
    """Test fetching available collections"""
    print("\nTesting collection retrieval...")
    
    collections = sentinel_hub_api.get_collections()
    
    if collections:
        print(f"✓ Found {len(collections)} collections")
        print("\nAvailable collections:")
        for col in collections[:5]:  # Show first 5
            print(f"  - {col.get('id')}: {col.get('title', 'N/A')}")
    else:
        print("✗ No collections found")


def test_sentinel2_search():
    """Test searching for Sentinel-2 data"""
    print("\nTesting Sentinel-2 search...")
    
    # Example: Search for data over a region in India
    bbox = [77.0, 28.0, 78.0, 29.0]  # Delhi region
    start_date = "2024-01-01"
    end_date = "2024-01-31"
    
    results = sentinel_hub_api.search_sentinel2(
        bbox=bbox,
        start_date=start_date,
        end_date=end_date,
        max_cloud_cover=20.0,
        limit=5
    )
    
    features = results.get("features", [])
    
    if features:
        print(f"✓ Found {len(features)} Sentinel-2 scenes")
        print("\nFirst result:")
        info = sentinel_hub_api.get_feature_info(features[0])
        print(json.dumps(info, indent=2))
    else:
        print("✗ No results found")


def test_stac_search():
    """Test generic STAC search"""
    print("\nTesting generic STAC search...")
    
    bbox = [77.0, 28.0, 78.0, 29.0]
    datetime_range = "2024-01-01/2024-01-31"
    
    results = sentinel_hub_api.search_stac(
        bbox=bbox,
        datetime_range=datetime_range,
        collections=["sentinel-2-l2a"],
        limit=3
    )
    
    print(f"✓ Search completed")
    print(f"  Features returned: {len(results.get('features', []))}")
    print(f"  Context: {results.get('context', {})}")


def main():
    """Run all tests"""
    print("=" * 60)
    print("Sentinel Hub Catalog API Test Suite")
    print("=" * 60)
    
    # Check if credentials are configured
    if not os.getenv("SENTINEL_HUB_CLIENT_ID"):
        print("\n⚠ WARNING: Sentinel Hub credentials not configured")
        print("Add SENTINEL_HUB_CLIENT_ID and SENTINEL_HUB_CLIENT_SECRET to .env")
        print("\nTo get credentials:")
        print("1. Sign up at https://www.sentinel-hub.com/")
        print("2. Create an OAuth client in your dashboard")
        print("3. Add credentials to .env file")
        return
    
    # Run tests
    if test_authentication():
        test_get_collections()
        test_sentinel2_search()
        test_stac_search()
    
    print("\n" + "=" * 60)
    print("Test suite completed")
    print("=" * 60)


if __name__ == "__main__":
    main()
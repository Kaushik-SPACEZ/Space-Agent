"""
Example: Querying Satellite Data using Sentinel Hub Catalog API

This example demonstrates how to search for and retrieve satellite data
using the STAC-based Sentinel Hub Catalog API.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.sentinel_hub_api import sentinel_hub_api
import json
from datetime import datetime, timedelta


def example_flood_monitoring():
    """
    Example: Search for satellite data for flood monitoring
    """
    print("=" * 60)
    print("Example: Flood Monitoring with Sentinel-1 SAR Data")
    print("=" * 60)
    
    # Define area of interest (e.g., flood-prone region)
    bbox = [85.0, 25.0, 88.0, 27.0]  # Example: Bihar, India
    
    # Search for recent Sentinel-1 data (SAR works through clouds)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    print(f"\nSearching for Sentinel-1 data...")
    print(f"Area: {bbox}")
    print(f"Date range: {start_date.date()} to {end_date.date()}")
    
    results = sentinel_hub_api.search_sentinel1(
        bbox=bbox,
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d"),
        limit=5
    )
    
    features = results.get("features", [])
    print(f"\nFound {len(features)} scenes")
    
    if features:
        print("\nScene details:")
        for i, feature in enumerate(features, 1):
            info = sentinel_hub_api.get_feature_info(feature)
            print(f"\n{i}. Scene ID: {info['id']}")
            print(f"   Date: {info['datetime']}")
            print(f"   Platform: {info['platform']}")
            print(f"   Available assets: {', '.join(info['assets'][:3])}...")


def example_vegetation_monitoring():
    """
    Example: Search for satellite data for vegetation monitoring
    """
    print("\n" + "=" * 60)
    print("Example: Vegetation Monitoring with Sentinel-2 Optical Data")
    print("=" * 60)
    
    # Define agricultural region
    bbox = [75.0, 15.0, 77.0, 17.0]  # Example: Karnataka, India
    
    # Search for cloud-free Sentinel-2 data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=60)
    
    print(f"\nSearching for Sentinel-2 data...")
    print(f"Area: {bbox}")
    print(f"Date range: {start_date.date()} to {end_date.date()}")
    print(f"Max cloud cover: 10%")
    
    results = sentinel_hub_api.search_sentinel2(
        bbox=bbox,
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d"),
        max_cloud_cover=10.0,
        limit=5
    )
    
    features = results.get("features", [])
    print(f"\nFound {len(features)} scenes")
    
    if features:
        print("\nScene details:")
        for i, feature in enumerate(features, 1):
            info = sentinel_hub_api.get_feature_info(feature)
            print(f"\n{i}. Scene ID: {info['id']}")
            print(f"   Date: {info['datetime']}")
            print(f"   Cloud cover: {info['cloud_cover']}%")
            print(f"   Platform: {info['platform']}")


def example_browse_collections():
    """
    Example: Browse available satellite data collections
    """
    print("\n" + "=" * 60)
    print("Example: Browse Available Collections")
    print("=" * 60)
    
    print("\nFetching available collections...")
    collections = sentinel_hub_api.get_collections()
    
    if collections:
        print(f"\nFound {len(collections)} collections:")
        for col in collections:
            print(f"\n- {col.get('id')}")
            print(f"  Title: {col.get('title', 'N/A')}")
            print(f"  Description: {col.get('description', 'N/A')[:100]}...")
    else:
        print("No collections available (check authentication)")


def example_custom_stac_query():
    """
    Example: Custom STAC query with advanced filters
    """
    print("\n" + "=" * 60)
    print("Example: Custom STAC Query")
    print("=" * 60)
    
    # Define search parameters
    bbox = [77.0, 28.0, 78.0, 29.0]  # Delhi region
    datetime_range = "2024-01-01/2024-01-31"
    
    # Custom query with multiple filters
    query = {
        "eo:cloud_cover": {"lte": 15},
        "platform": {"eq": "sentinel-2b"}
    }
    
    print(f"\nSearching with custom filters...")
    print(f"Area: {bbox}")
    print(f"Date range: {datetime_range}")
    print(f"Filters: {json.dumps(query, indent=2)}")
    
    results = sentinel_hub_api.search_stac(
        bbox=bbox,
        datetime_range=datetime_range,
        collections=["sentinel-2-l2a"],
        limit=3,
        query=query
    )
    
    features = results.get("features", [])
    print(f"\nFound {len(features)} matching scenes")


def main():
    """Run all examples"""
    print("\n" + "=" * 70)
    print("Sentinel Hub Catalog API - Usage Examples")
    print("=" * 70)
    
    # Check authentication
    if not sentinel_hub_api.authenticate():
        print("\n⚠ ERROR: Authentication failed")
        print("\nPlease configure Sentinel Hub credentials:")
        print("1. Sign up at https://www.sentinel-hub.com/")
        print("2. Create an OAuth client")
        print("3. Add credentials to .env file:")
        print("   SENTINEL_HUB_CLIENT_ID=your_client_id")
        print("   SENTINEL_HUB_CLIENT_SECRET=your_client_secret")
        return
    
    print("\n✓ Authentication successful\n")
    
    # Run examples
    try:
        example_browse_collections()
        example_flood_monitoring()
        example_vegetation_monitoring()
        example_custom_stac_query()
    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
    
    print("\n" + "=" * 70)
    print("Examples completed")
    print("=" * 70)


if __name__ == "__main__":
    main()
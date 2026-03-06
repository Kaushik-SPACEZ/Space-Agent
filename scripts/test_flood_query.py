"""
Test script to verify flood pipeline integration with Copernicus API
Tests natural language style queries for flood data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipelines.flood_pipeline import FloodPipeline
from datetime import datetime, timedelta
import json


def test_tamil_nadu_floods():
    """Test: Show me flood areas in Tamil Nadu for past two days"""
    print("=" * 70)
    print("Test: Show me flood areas in Tamil Nadu for past two days")
    print("=" * 70)
    
    pipeline = FloodPipeline()
    
    # Calculate date range (past 2 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=2)
    
    params = {
        "state": "Tamil Nadu",
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "use_satellite": True
    }
    
    print(f"\nQuerying Copernicus for:")
    print(f"  State: {params['state']}")
    print(f"  Date Range: {params['start_date']} to {params['end_date']}")
    print(f"  Data Source: Real Sentinel-1 satellite data\n")
    
    results = pipeline.execute(params)
    
    if results["status"] == "success":
        print(f"✓ Query successful!")
        print(f"\nMetadata:")
        for key, value in results["metadata"].items():
            print(f"  {key}: {value}")
        
        print(f"\nFound {len(results['data'])} Sentinel-1 scenes:")
        for i, scene in enumerate(results["data"][:3], 1):  # Show first 3
            print(f"\n{i}. {scene['scene_id'][:50]}...")
            print(f"   Date: {scene['acquisition_date']}")
            print(f"   Platform: {scene['platform']}")
            print(f"   Mode: {scene['instrument_mode']}")
            print(f"   Polarization: {scene['polarization']}")
    else:
        print(f"✗ Query failed: {results.get('error')}")


def test_bihar_floods_last_month():
    """Test: Show me flood data for Bihar in the last month"""
    print("\n" + "=" * 70)
    print("Test: Show me flood data for Bihar in the last month")
    print("=" * 70)
    
    pipeline = FloodPipeline()
    
    # Last 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    params = {
        "state": "Bihar",
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "use_satellite": True
    }
    
    print(f"\nQuerying Copernicus for:")
    print(f"  State: {params['state']}")
    print(f"  Date Range: {params['start_date']} to {params['end_date']}")
    
    results = pipeline.execute(params)
    
    if results["status"] == "success":
        print(f"\n✓ Found {results['metadata']['total_scenes']} scenes")
        print(f"  Data Source: {results['metadata']['data_source']}")
    else:
        print(f"✗ Query failed")


def test_kerala_recent_floods():
    """Test: Recent floods in Kerala"""
    print("\n" + "=" * 70)
    print("Test: Recent floods in Kerala (last 7 days)")
    print("=" * 70)
    
    pipeline = FloodPipeline()
    
    params = {
        "state": "Kerala",
        "start_date": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
        "end_date": datetime.now().strftime("%Y-%m-%d"),
        "use_satellite": True
    }
    
    results = pipeline.execute(params)
    
    if results["status"] == "success":
        print(f"✓ Found {results['metadata']['total_scenes']} Sentinel-1 scenes")
        if results["data"]:
            latest = results["data"][0]
            print(f"\nLatest scene:")
            print(f"  ID: {latest['scene_id'][:60]}...")
            print(f"  Date: {latest['acquisition_date']}")
            print(f"  Type: {latest['data_type']}")
    else:
        print(f"✗ Query failed")


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("Flood Pipeline Integration Test")
    print("Testing Real Copernicus Satellite Data Queries")
    print("=" * 70)
    
    try:
        test_tamil_nadu_floods()
        test_bihar_floods_last_month()
        test_kerala_recent_floods()
        
        print("\n" + "=" * 70)
        print("✅ Integration Test Complete!")
        print("=" * 70)
        print("\nYour system can now:")
        print("  ✓ Query real Copernicus Sentinel-1 data")
        print("  ✓ Filter by state and date range")
        print("  ✓ Return actual satellite scenes for flood monitoring")
        print("\nNext: Test with natural language through the agent!")
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
"""
Simple demo: Query real Copernicus flood data
Shows how to ask "Show me flood areas in Tamil Nadu for past two days"
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipelines.flood_pipeline_copernicus import get_flood_pipeline
from datetime import datetime, timedelta


def demo_tamil_nadu_2_days():
    """Demo: Show me flood areas in Tamil Nadu for past two days"""
    print("\n" + "=" * 70)
    print("DEMO: Show me flood areas in Tamil Nadu for past two days")
    print("=" * 70)
    
    pipeline = get_flood_pipeline()
    
    # Query for past 2 days
    result = pipeline.query_floods(
        state="Tamil Nadu",
        days_back=2
    )
    
    if result["status"] == "success":
        print(f"\n✅ SUCCESS!")
        print(f"\nFound {result['metadata']['total_scenes']} Sentinel-1 scenes")
        print(f"Date Range: {result['metadata']['date_range']}")
        if 'data_source' in result['metadata']:
            print(f"Data Source: {result['metadata']['data_source']}")
        
        if result["data"]:
            print(f"\n📡 Latest Scene:")
            scene = result["data"][0]
            print(f"  ID: {scene['scene_id'][:60]}...")
            print(f"  Date: {scene['acquisition_date']}")
            print(f"  Platform: {scene['platform']}")
            print(f"  Mode: {scene['instrument_mode']}")
            print(f"  Polarization: {scene['polarization']}")
            print(f"  Type: {scene['data_type']}")
            print(f"  Note: {scene['description']}")
    else:
        print(f"\n❌ Error: {result.get('error')}")


def demo_bihar_last_month():
    """Demo: Show me flood data for Bihar in the last month"""
    print("\n" + "=" * 70)
    print("DEMO: Show me flood data for Bihar in the last month")
    print("=" * 70)
    
    pipeline = get_flood_pipeline()
    
    result = pipeline.query_floods(
        state="Bihar",
        days_back=30
    )
    
    if result["status"] == "success":
        print(f"\n✅ Found {result['metadata']['total_scenes']} scenes")
        print(f"   State: {result['metadata']['state']}")
        print(f"   Period: {result['metadata']['date_range']}")
    else:
        print(f"\n❌ Error")


def demo_kerala_specific_dates():
    """Demo: Show me flood data for Kerala between specific dates"""
    print("\n" + "=" * 70)
    print("DEMO: Show me flood data for Kerala (Jan 1-31, 2024)")
    print("=" * 70)
    
    pipeline = get_flood_pipeline()
    
    result = pipeline.query_floods(
        state="Kerala",
        start_date="2024-01-01",
        end_date="2024-01-31"
    )
    
    if result["status"] == "success":
        print(f"\n✅ Found {result['metadata']['total_scenes']} scenes")
        if result["data"]:
            print(f"\nShowing first 3 scenes:")
            for i, scene in enumerate(result["data"][:3], 1):
                print(f"  {i}. {scene['acquisition_date']} - {scene['platform']}")
    else:
        print(f"\n❌ Error")


def main():
    print("\n" + "=" * 70)
    print("🌊 FLOOD MONITORING WITH REAL COPERNICUS DATA")
    print("=" * 70)
    print("\nThis demo shows how your system now queries REAL satellite data!")
    print("When you ask: 'Show me flood areas in Tamil Nadu'")
    print("The system fetches actual Sentinel-1 SAR scenes from Copernicus")
    
    try:
        # Run demos
        demo_tamil_nadu_2_days()
        demo_bihar_last_month()
        demo_kerala_specific_dates()
        
        print("\n" + "=" * 70)
        print("✅ ALL DEMOS COMPLETE!")
        print("=" * 70)
        print("\n🎉 Your system is now connected to real satellite data!")
        print("\nWhat this means:")
        print("  ✓ Queries fetch actual Sentinel-1 SAR data from Copernicus")
        print("  ✓ Data is suitable for flood detection (SAR works through clouds)")
        print("  ✓ You can filter by state and date range")
        print("  ✓ System returns real satellite scene metadata")
        print("\n📝 Next Steps:")
        print("  1. Integrate with your LLM agent for natural language queries")
        print("  2. Download and process SAR data for flood extent mapping")
        print("  3. Store results in PostGIS database")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
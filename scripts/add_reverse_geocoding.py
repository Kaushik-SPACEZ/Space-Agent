"""
Add reverse geocoding to flood data
Converts latitude/longitude to district names using geopy
"""

import csv
import time
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

def get_district_from_coords(lat: float, lon: float, geolocator, retry_count: int = 3) -> str:
    """
    Get district name from coordinates using reverse geocoding
    
    Args:
        lat: Latitude
        lon: Longitude
        geolocator: Nominatim geolocator instance
        retry_count: Number of retries on failure
        
    Returns:
        District name or empty string
    """
    for attempt in range(retry_count):
        try:
            location = geolocator.reverse(f"{lat}, {lon}", language='en', timeout=10)
            
            if location and location.raw.get('address'):
                address = location.raw['address']
                
                # Try different keys for district
                district = (
                    address.get('county') or 
                    address.get('state_district') or
                    address.get('district') or
                    address.get('suburb') or
                    address.get('city') or
                    ""
                )
                
                return district
            
            return ""
            
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            if attempt < retry_count - 1:
                print(f"    Retry {attempt + 1}/{retry_count} for ({lat}, {lon})")
                time.sleep(2)  # Wait before retry
            else:
                print(f"    Failed to geocode ({lat}, {lon}): {e}")
                return ""
        except Exception as e:
            print(f"    Error geocoding ({lat}, {lon}): {e}")
            return ""
    
    return ""


def process_flood_data(input_file: str, output_file: str):
    """
    Process flood data and add district information
    
    Args:
        input_file: Input CSV file path
        output_file: Output CSV file path
    """
    print("\n" + "=" * 60)
    print("REVERSE GEOCODING - Adding District Information")
    print("=" * 60)
    
    # Initialize geolocator
    print("\nInitializing geocoder...")
    geolocator = Nominatim(user_agent="flood_monitoring_app")
    print("✓ Geocoder initialized")
    
    # Read input data
    print(f"\nReading data from {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        events = list(reader)
    print(f"✓ Read {len(events)} events")
    
    # Process each event
    print(f"\nProcessing events (this may take a while)...")
    processed = 0
    failed = 0
    
    for i, event in enumerate(events, 1):
        lat = float(event['latitude'])
        lon = float(event['longitude'])
        
        if i % 10 == 0:
            print(f"  Processing event {i}/{len(events)}...")
        
        # Get district
        district = get_district_from_coords(lat, lon, geolocator)
        event['district'] = district
        
        if district:
            processed += 1
        else:
            failed += 1
        
        # Rate limiting - Nominatim allows 1 request per second
        time.sleep(1.1)
    
    print(f"\n✓ Processed {processed} events successfully")
    if failed > 0:
        print(f"⚠ Failed to geocode {failed} events")
    
    # Save updated data
    print(f"\nSaving updated data to {output_file}...")
    fieldnames = list(events[0].keys())
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(events)
    
    print(f"✓ Saved {len(events)} events to {output_file}")
    
    # Print sample results
    print("\n" + "=" * 60)
    print("SAMPLE RESULTS (First 5 events)")
    print("=" * 60)
    for event in events[:5]:
        print(f"\n{event['uei']}:")
        print(f"  State: {event['state']}")
        print(f"  District: {event['district'] or 'N/A'}")
        print(f"  Coordinates: ({event['latitude']}, {event['longitude']})")


def main():
    """Main function"""
    input_file = "data/sample_flood_events.csv"
    output_file = "data/sample_flood_events_with_districts.csv"
    
    print("\n⚠ NOTE: This process will take approximately 5-6 minutes")
    print("(Nominatim API allows 1 request per second)")
    print("\nPress Ctrl+C to cancel if needed\n")
    
    try:
        process_flood_data(input_file, output_file)
        
        print("\n" + "=" * 60)
        print("✓ Reverse geocoding complete!")
        print("=" * 60)
        print(f"\nOutput file: {output_file}")
        print("\nNext steps:")
        print("1. Review the output file")
        print("2. Load data into PostgreSQL")
        print("3. Test natural language queries")
        
    except KeyboardInterrupt:
        print("\n\n⚠ Process cancelled by user")
    except Exception as e:
        print(f"\n\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
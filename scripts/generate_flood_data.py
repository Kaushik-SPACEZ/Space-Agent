"""
Generate realistic sample flood data for Indian states
Creates 250 flood events with realistic coordinates, dates, and details
"""

import csv
import random
from datetime import datetime, timedelta
from typing import List, Dict

# Indian states with their approximate coordinate ranges
INDIAN_STATES = {
    "Tamil Nadu": {"lat": (8.0, 13.5), "lon": (76.2, 80.3)},
    "Kerala": {"lat": (8.2, 12.8), "lon": (74.8, 77.4)},
    "Karnataka": {"lat": (11.5, 18.5), "lon": (74.0, 78.6)},
    "Andhra Pradesh": {"lat": (12.6, 19.9), "lon": (76.7, 84.8)},
    "Maharashtra": {"lat": (15.6, 22.0), "lon": (72.6, 80.9)},
    "Gujarat": {"lat": (20.1, 24.7), "lon": (68.2, 74.5)},
    "Rajasthan": {"lat": (23.0, 30.2), "lon": (69.5, 78.3)},
    "Madhya Pradesh": {"lat": (21.1, 26.9), "lon": (74.0, 82.8)},
    "Uttar Pradesh": {"lat": (23.9, 30.4), "lon": (77.0, 84.6)},
    "Bihar": {"lat": (24.3, 27.5), "lon": (83.3, 88.3)},
    "West Bengal": {"lat": (21.5, 27.2), "lon": (85.8, 89.9)},
    "Odisha": {"lat": (17.8, 22.6), "lon": (81.3, 87.5)},
    "Assam": {"lat": (24.0, 28.0), "lon": (89.7, 96.0)},
    "Jharkhand": {"lat": (21.9, 25.3), "lon": (83.3, 87.9)},
    "Chhattisgarh": {"lat": (17.8, 24.1), "lon": (80.3, 84.4)},
    "Punjab": {"lat": (29.5, 32.6), "lon": (73.9, 76.9)},
    "Haryana": {"lat": (27.7, 30.9), "lon": (74.5, 77.6)},
    "Uttarakhand": {"lat": (28.7, 31.5), "lon": (77.6, 81.0)},
    "Himachal Pradesh": {"lat": (30.4, 33.2), "lon": (75.6, 79.0)}
}

# Flood causes
FLOOD_CAUSES = [
    "Heavy Monsoon Rainfall",
    "Cyclone",
    "Dam Release",
    "River Overflow",
    "Cloud Burst",
    "Glacial Lake Outburst",
    "Urban Flooding",
    "Coastal Storm Surge",
    "Flash Flood",
    "Prolonged Rainfall"
]

# Severity levels
SEVERITY_LEVELS = ["Low", "Moderate", "High", "Severe", "Catastrophic"]

# Event sources
EVENT_SOURCES = [
    "Sentinel-1 SAR",
    "Sentinel-2 Optical",
    "MODIS",
    "Landsat-8",
    "Ground Reports",
    "News Reports"
]


def generate_random_date(start_year: int = 2020, end_year: int = 2024) -> datetime:
    """Generate random date between start and end year"""
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    delta = end - start
    random_days = random.randint(0, delta.days)
    return start + timedelta(days=random_days)


def generate_flood_event(event_id: int) -> Dict:
    """Generate a single realistic flood event"""
    
    # Select random state
    state = random.choice(list(INDIAN_STATES.keys()))
    coords = INDIAN_STATES[state]
    
    # Generate coordinates within state bounds
    latitude = round(random.uniform(coords["lat"][0], coords["lat"][1]), 6)
    longitude = round(random.uniform(coords["lon"][0], coords["lon"][1]), 6)
    
    # Generate dates
    start_date = generate_random_date()
    duration = random.randint(1, 30)  # 1-30 days
    end_date = start_date + timedelta(days=duration)
    
    # Generate severity (weighted towards moderate)
    severity = random.choices(
        SEVERITY_LEVELS,
        weights=[15, 35, 30, 15, 5],  # More moderate floods
        k=1
    )[0]
    
    # Area affected based on severity
    if severity == "Low":
        area = round(random.uniform(1, 50), 2)
    elif severity == "Moderate":
        area = round(random.uniform(50, 200), 2)
    elif severity == "High":
        area = round(random.uniform(200, 500), 2)
    elif severity == "Severe":
        area = round(random.uniform(500, 1500), 2)
    else:  # Catastrophic
        area = round(random.uniform(1500, 5000), 2)
    
    # Select cause (monsoon more common)
    cause = random.choices(
        FLOOD_CAUSES,
        weights=[30, 10, 8, 15, 5, 2, 12, 8, 5, 5],
        k=1
    )[0]
    
    # Generate description
    descriptions = [
        f"Flood event in {state} caused by {cause.lower()}",
        f"Severe flooding reported in {state} region",
        f"Water logging and flooding in {state} due to {cause.lower()}",
        f"Flood situation in {state} affecting multiple areas",
        f"Emergency declared in {state} due to flooding"
    ]
    description = random.choice(descriptions)
    
    # Event source
    source = random.choice(EVENT_SOURCES)
    
    return {
        "uei": f"FLOOD-IND-{event_id:04d}",
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "duration_days": duration,
        "latitude": latitude,
        "longitude": longitude,
        "state": state,
        "district": "",  # Will be filled by reverse geocoding
        "severity": severity,
        "area_affected_sqkm": area,
        "main_cause": cause,
        "description": description,
        "event_source": source
    }


def generate_dataset(num_events: int = 250) -> List[Dict]:
    """Generate complete dataset"""
    print(f"Generating {num_events} flood events...")
    
    events = []
    for i in range(1, num_events + 1):
        event = generate_flood_event(i)
        events.append(event)
        
        if i % 50 == 0:
            print(f"  Generated {i} events...")
    
    print(f"✓ Generated {num_events} flood events")
    return events


def save_to_csv(events: List[Dict], filename: str = "data/sample_flood_events.csv"):
    """Save events to CSV file"""
    print(f"\nSaving to {filename}...")
    
    fieldnames = [
        "uei", "start_date", "end_date", "duration_days",
        "latitude", "longitude", "state", "district",
        "severity", "area_affected_sqkm", "main_cause",
        "description", "event_source"
    ]
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(events)
    
    print(f"✓ Saved {len(events)} events to {filename}")


def print_statistics(events: List[Dict]):
    """Print dataset statistics"""
    print("\n" + "=" * 60)
    print("DATASET STATISTICS")
    print("=" * 60)
    
    # Count by state
    state_counts = {}
    for event in events:
        state = event["state"]
        state_counts[state] = state_counts.get(state, 0) + 1
    
    print(f"\nTotal Events: {len(events)}")
    print(f"\nEvents by State:")
    for state, count in sorted(state_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {state}: {count}")
    
    # Count by severity
    severity_counts = {}
    for event in events:
        severity = event["severity"]
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    print(f"\nEvents by Severity:")
    for severity in SEVERITY_LEVELS:
        count = severity_counts.get(severity, 0)
        print(f"  {severity}: {count}")
    
    # Date range
    dates = [datetime.strptime(e["start_date"], "%Y-%m-%d") for e in events]
    print(f"\nDate Range:")
    print(f"  Earliest: {min(dates).strftime('%Y-%m-%d')}")
    print(f"  Latest: {max(dates).strftime('%Y-%m-%d')}")
    
    # Area statistics
    areas = [e["area_affected_sqkm"] for e in events]
    print(f"\nArea Affected (sq km):")
    print(f"  Min: {min(areas):.2f}")
    print(f"  Max: {max(areas):.2f}")
    print(f"  Average: {sum(areas)/len(areas):.2f}")


def main():
    """Main function"""
    print("\n" + "=" * 60)
    print("INDIAN FLOOD DATA GENERATOR")
    print("=" * 60)
    
    # Generate 250 events
    events = generate_dataset(250)
    
    # Save to CSV
    save_to_csv(events)
    
    # Print statistics
    print_statistics(events)
    
    print("\n" + "=" * 60)
    print("✓ Dataset generation complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Run reverse geocoding to fill district names")
    print("2. Load data into PostgreSQL")
    print("3. Test natural language queries")


if __name__ == "__main__":
    main()
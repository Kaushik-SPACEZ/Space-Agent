"""
Load flood data from CSV into PostgreSQL database
Handles both files with and without district information
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import csv
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def connect_to_database():
    """Connect to PostgreSQL database"""
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            database=os.getenv("DB_NAME", "earth_obs"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD")
        )
        return conn
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return None


def create_schema(conn):
    """Create database schema"""
    print("\nCreating database schema...")
    
    try:
        with open("database/flood_schema_v2.sql", 'r') as f:
            schema_sql = f.read()
        
        cursor = conn.cursor()
        cursor.execute(schema_sql)
        conn.commit()
        cursor.close()
        
        print("✓ Schema created successfully")
        return True
        
    except Exception as e:
        print(f"✗ Schema creation failed: {e}")
        conn.rollback()
        return False


def load_csv_data(csv_file: str):
    """Load data from CSV file"""
    print(f"\nReading data from {csv_file}...")
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            events = list(reader)
        
        print(f"✓ Read {len(events)} events from CSV")
        return events
        
    except Exception as e:
        print(f"✗ Failed to read CSV: {e}")
        return []


def insert_flood_events(conn, events):
    """Insert flood events into database"""
    print(f"\nInserting {len(events)} events into database...")
    
    try:
        cursor = conn.cursor()
        
        # Prepare data for insertion
        insert_query = """
            INSERT INTO flood_events (
                uei, start_date, end_date, duration_days,
                latitude, longitude, state, district,
                severity, area_affected_sqkm, main_cause,
                description, event_source, geometry
            ) VALUES %s
            ON CONFLICT (uei) DO UPDATE SET
                start_date = EXCLUDED.start_date,
                end_date = EXCLUDED.end_date,
                duration_days = EXCLUDED.duration_days,
                latitude = EXCLUDED.latitude,
                longitude = EXCLUDED.longitude,
                state = EXCLUDED.state,
                district = EXCLUDED.district,
                severity = EXCLUDED.severity,
                area_affected_sqkm = EXCLUDED.area_affected_sqkm,
                main_cause = EXCLUDED.main_cause,
                description = EXCLUDED.description,
                event_source = EXCLUDED.event_source,
                geometry = EXCLUDED.geometry,
                updated_at = CURRENT_TIMESTAMP
        """
        
        # Prepare values
        values = []
        for event in events:
            values.append((
                event['uei'],
                event['start_date'],
                event['end_date'] if event['end_date'] else None,
                int(event['duration_days']) if event['duration_days'] else None,
                float(event['latitude']),
                float(event['longitude']),
                event['state'],
                event.get('district', ''),  # May not exist in all files
                event['severity'],
                float(event['area_affected_sqkm']) if event['area_affected_sqkm'] else None,
                event['main_cause'],
                event['description'],
                event['event_source'],
                f"POINT({event['longitude']} {event['latitude']})"
            ))
        
        # Execute batch insert
        execute_values(cursor, insert_query, values)
        conn.commit()
        
        print(f"✓ Inserted {len(events)} events successfully")
        
        cursor.close()
        return True
        
    except Exception as e:
        print(f"✗ Insert failed: {e}")
        conn.rollback()
        import traceback
        traceback.print_exc()
        return False


def verify_data(conn):
    """Verify loaded data"""
    print("\nVerifying loaded data...")
    
    try:
        cursor = conn.cursor()
        
        # Count total events
        cursor.execute("SELECT COUNT(*) FROM flood_events")
        total = cursor.fetchone()[0]
        print(f"  Total events: {total}")
        
        # Count by state (top 5)
        cursor.execute("""
            SELECT state, COUNT(*) as count 
            FROM flood_events 
            GROUP BY state 
            ORDER BY count DESC 
            LIMIT 5
        """)
        print(f"\n  Top 5 states by event count:")
        for state, count in cursor.fetchall():
            print(f"    {state}: {count}")
        
        # Count by severity
        cursor.execute("""
            SELECT severity, COUNT(*) as count 
            FROM flood_events 
            GROUP BY severity 
            ORDER BY 
                CASE severity
                    WHEN 'Low' THEN 1
                    WHEN 'Moderate' THEN 2
                    WHEN 'High' THEN 3
                    WHEN 'Severe' THEN 4
                    WHEN 'Catastrophic' THEN 5
                END
        """)
        print(f"\n  Events by severity:")
        for severity, count in cursor.fetchall():
            print(f"    {severity}: {count}")
        
        # Date range
        cursor.execute("""
            SELECT 
                MIN(start_date) as earliest,
                MAX(start_date) as latest
            FROM flood_events
        """)
        earliest, latest = cursor.fetchone()
        print(f"\n  Date range:")
        print(f"    Earliest: {earliest}")
        print(f"    Latest: {latest}")
        
        cursor.close()
        print("\n✓ Data verification complete")
        return True
        
    except Exception as e:
        print(f"✗ Verification failed: {e}")
        return False


def main():
    """Main function"""
    print("\n" + "=" * 60)
    print("LOAD FLOOD DATA INTO POSTGRESQL")
    print("=" * 60)
    
    # Check which CSV file to use
    csv_with_districts = "data/sample_flood_events_with_districts.csv"
    csv_without_districts = "data/sample_flood_events.csv"
    
    if os.path.exists(csv_with_districts):
        csv_file = csv_with_districts
        print(f"\n✓ Using file with district information")
    else:
        csv_file = csv_without_districts
        print(f"\n⚠ Using file without district information")
        print(f"  (Run add_reverse_geocoding.py to add districts)")
    
    # Connect to database
    print("\nConnecting to database...")
    conn = connect_to_database()
    
    if not conn:
        print("\n✗ Failed to connect to database")
        print("\nPlease check:")
        print("1. PostgreSQL is running")
        print("2. Database 'earth_obs' exists")
        print("3. Credentials in .env file are correct")
        return
    
    print("✓ Connected to database")
    
    try:
        # Create schema
        if not create_schema(conn):
            return
        
        # Load CSV data
        events = load_csv_data(csv_file)
        if not events:
            return
        
        # Insert data
        if not insert_flood_events(conn, events):
            return
        
        # Verify data
        verify_data(conn)
        
        print("\n" + "=" * 60)
        print("✓ DATA LOADING COMPLETE!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Test queries: SELECT * FROM flood_events LIMIT 5;")
        print("2. Try views: SELECT * FROM recent_floods;")
        print("3. Build natural language query system")
        
    finally:
        conn.close()
        print("\n✓ Database connection closed")


if __name__ == "__main__":
    main()
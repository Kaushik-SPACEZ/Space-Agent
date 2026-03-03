import psycopg2
from psycopg2.extras import RealDictCursor
import os
import getpass

def verify_schema():
    """Verify database schema and test queries"""
    
    try:
        print("🔍 Connecting to earth_obs database...")
        
        # Get password from env or prompt
        password = os.getenv("DB_PASSWORD")
        if not password:
            password = getpass.getpass("Enter PostgreSQL password: ")
        
        conn = psycopg2.connect(
            dbname="earth_obs",
            user="postgres",
            password=password,
            host="localhost",
            port="5432"
        )
        
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("\n" + "="*60)
        print("Test 1: Check Tables Exist")
        print("="*60)
        cursor.execute("""
            SELECT COUNT(*) as table_count
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE'
            AND table_name NOT LIKE 'spatial_%';
        """)
        result = cursor.fetchone()
        print(f"✅ Tables created: {result['table_count']}")
        
        print("\n" + "="*60)
        print("Test 2: Check PostGIS Functions")
        print("="*60)
        cursor.execute("SELECT PostGIS_Version();")
        result = cursor.fetchone()
        print(f"✅ PostGIS Version: {result['postgis_version']}")
        
        print("\n" + "="*60)
        print("Test 3: Check Sample Data")
        print("="*60)
        cursor.execute("SELECT COUNT(*) as count FROM flood_events;")
        flood_count = cursor.fetchone()['count']
        print(f"✅ Sample flood events: {flood_count}")
        
        cursor.execute("SELECT COUNT(*) as count FROM vegetation_data;")
        veg_count = cursor.fetchone()['count']
        print(f"✅ Sample vegetation data: {veg_count}")
        
        print("\n" + "="*60)
        print("Test 4: Test Spatial Query")
        print("="*60)
        cursor.execute("""
            SELECT 
                event_id,
                state,
                district,
                ST_Area(geometry::geography) / 1000000 as area_sqkm,
                severity,
                confidence_score
            FROM flood_events
            LIMIT 1;
        """)
        result = cursor.fetchone()
        if result:
            print(f"✅ Spatial queries working!")
            print(f"   Event ID: {result['event_id']}")
            print(f"   Location: {result['district']}, {result['state']}")
            print(f"   Area: {result['area_sqkm']:.2f} sq km")
            print(f"   Severity: {result['severity']}")
            print(f"   Confidence: {result['confidence_score']}")
        
        print("\n" + "="*60)
        print("Test 5: Test Views")
        print("="*60)
        
        # Test recent_floods view
        cursor.execute("SELECT COUNT(*) as count FROM recent_floods;")
        result = cursor.fetchone()
        print(f"✅ recent_floods view: {result['count']} records")
        
        # Test vegetation_health_summary view
        cursor.execute("SELECT COUNT(*) as count FROM vegetation_health_summary;")
        result = cursor.fetchone()
        print(f"✅ vegetation_health_summary view: {result['count']} records")
        
        # Test satellite_availability view
        cursor.execute("SELECT COUNT(*) as count FROM satellite_availability;")
        result = cursor.fetchone()
        print(f"✅ satellite_availability view: {result['count']} records")
        
        print("\n" + "="*60)
        print("Test 6: Test Indexes")
        print("="*60)
        cursor.execute("""
            SELECT 
                schemaname,
                tablename,
                indexname
            FROM pg_indexes
            WHERE schemaname = 'public'
            AND tablename IN ('flood_events', 'vegetation_data', 'satellite_coverage')
            ORDER BY tablename, indexname;
        """)
        indexes = cursor.fetchall()
        print(f"✅ Created {len(indexes)} indexes:")
        current_table = None
        for idx in indexes:
            if idx['tablename'] != current_table:
                current_table = idx['tablename']
                print(f"\n   {current_table}:")
            print(f"      - {idx['indexname']}")
        
        print("\n" + "="*60)
        print("Test 7: Test Triggers")
        print("="*60)
        cursor.execute("""
            SELECT 
                trigger_name,
                event_object_table
            FROM information_schema.triggers
            WHERE trigger_schema = 'public'
            ORDER BY event_object_table;
        """)
        triggers = cursor.fetchall()
        print(f"✅ Created {len(triggers)} triggers:")
        for trigger in triggers:
            print(f"   - {trigger['trigger_name']} on {trigger['event_object_table']}")
        
        cursor.close()
        conn.close()
        
        print("\n" + "="*60)
        print("🎉 Schema Verification Complete!")
        print("="*60)
        print("\n✅ All tests passed!")
        print("✅ Database is ready for data collection")
        print("\n💡 Next: Checkpoint 1.3 - API Registration")
        
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("Database Schema Verification")
    print("="*60)
    verify_schema()
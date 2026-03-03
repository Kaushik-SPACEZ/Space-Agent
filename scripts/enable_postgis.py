import psycopg2
import getpass

def enable_postgis():
    """Enable PostGIS extension in earth_obs database"""
    
    try:
        print("🔍 Connecting to earth_obs database...")
        
        # Get password
        password = getpass.getpass("Enter PostgreSQL password: ")
        
        # Connect to earth_obs database
        conn = psycopg2.connect(
            dbname="earth_obs",
            user="postgres",
            password=password,
            host="localhost",
            port="5432"
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("📦 Enabling PostGIS extension...")
        
        # Enable PostGIS
        cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
        print("✅ PostGIS extension enabled")
        
        # Enable PostGIS Topology (optional but recommended)
        cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis_topology;")
        print("✅ PostGIS Topology extension enabled")
        
        # Verify PostGIS installation
        cursor.execute("SELECT PostGIS_Version();")
        result = cursor.fetchone()
        print(f"\n✅ PostGIS Version: {result[0]}")
        
        cursor.execute("SELECT PostGIS_Full_Version();")
        result = cursor.fetchone()
        print(f"✅ Full Version Info:\n{result[0][:200]}...")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 PostGIS enabled successfully!")
        print("\n💡 Next step: Create database schema")
        return True
        
    except Exception as e:
        print(f"❌ Error enabling PostGIS: {e}")
        print("\n💡 Make sure PostGIS is installed via Stack Builder")
        return False

if __name__ == "__main__":
    print("="*60)
    print("Enable PostGIS Extension")
    print("="*60)
    enable_postgis()
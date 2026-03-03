import psycopg2
from psycopg2.extras import RealDictCursor
import os

def test_connection():
    """Test database connection and create database if needed"""
    
    # First, try to connect to postgres database to create earth_obs
    try:
        print("🔍 Checking if earth_obs database exists...")
        
        # Connect to default postgres database
        conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password=input("Enter PostgreSQL password: "),
            host="localhost",
            port="5432"
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if earth_obs database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname='earth_obs'")
        exists = cursor.fetchone()
        
        if not exists:
            print("📦 Creating earth_obs database...")
            cursor.execute("CREATE DATABASE earth_obs")
            print("✅ Database 'earth_obs' created successfully!")
        else:
            print("✅ Database 'earth_obs' already exists")
        
        cursor.close()
        conn.close()
        
        # Now connect to earth_obs database
        print("\n🔍 Testing connection to earth_obs database...")
        conn = psycopg2.connect(
            dbname="earth_obs",
            user="postgres",
            password=os.getenv("DB_PASSWORD", input("Enter PostgreSQL password again: ")),
            host="localhost",
            port="5432"
        )
        
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Test basic query
        cursor.execute("SELECT version();")
        result = cursor.fetchone()
        print(f"✅ Connected to PostgreSQL!")
        print(f"   Version: {result['version'][:50]}...")
        
        # Check if PostGIS is installed
        try:
            cursor.execute("SELECT PostGIS_Version();")
            result = cursor.fetchone()
            print(f"✅ PostGIS is installed: {result['postgis_version']}")
        except:
            print("⚠️  PostGIS not yet enabled (will enable in next step)")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 Database connection test successful!")
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ Connection failed: {e}")
        print("\n💡 Make sure:")
        print("   1. PostgreSQL is running")
        print("   2. You're using the correct password")
        print("   3. PostgreSQL is listening on localhost:5432")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("PostgreSQL Connection Test")
    print("="*60)
    test_connection()
import psycopg2
import os
import getpass

def init_database():
    """Initialize database schema"""
    
    try:
        print("🔍 Connecting to earth_obs database...")
        
        # Get password from env or prompt
        password = os.getenv("DB_PASSWORD")
        if not password:
            password = getpass.getpass("Enter PostgreSQL password: ")
        
        # Database connection
        conn = psycopg2.connect(
            dbname="earth_obs",
            user="postgres",
            password=password,
            host="localhost",
            port="5432"
        )
        
        # Read schema file
        print("📖 Reading schema file...")
        with open('database/schema.sql', 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # Execute schema
        print("🔨 Creating database schema...")
        cursor = conn.cursor()
        cursor.execute(schema_sql)
        conn.commit()
        print("✅ Database schema created successfully!")
        
        # Verify tables
        print("\n🔍 Verifying tables...")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        print(f"\n📊 Created {len(tables)} tables:")
        for table in tables:
            print(f"   ✓ {table[0]}")
        
        # Verify views
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.views 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        views = cursor.fetchall()
        print(f"\n📊 Created {len(views)} views:")
        for view in views:
            print(f"   ✓ {view[0]}")
        
        # Check sample data
        cursor.execute("SELECT COUNT(*) FROM flood_events;")
        flood_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM vegetation_data;")
        veg_count = cursor.fetchone()[0]
        
        print(f"\n📦 Sample data loaded:")
        print(f"   ✓ Flood events: {flood_count}")
        print(f"   ✓ Vegetation data: {veg_count}")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 Database initialization complete!")
        print("\n💡 Next step: Run verify_schema.py to test queries")
        return True
            
    except FileNotFoundError:
        print("❌ Error: database/schema.sql not found")
        print("   Make sure you're running from the project root directory")
        return False
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        if conn:
            conn.rollback()
        return False
    except Exception as e:
        print(f"❌ Error creating schema: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    print("="*60)
    print("Database Schema Initialization")
    print("="*60)
    init_database()
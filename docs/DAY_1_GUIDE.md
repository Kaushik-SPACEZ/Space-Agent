what # 📅 Day 1: Data Collection & Database Setup

**Goal**: Set up PostgreSQL + PostGIS database with 100+ real satellite records

**Time**: 8 hours (with breaks)

---

## 🎯 Day 1 Objectives

By end of day, you will have:
- ✅ PostgreSQL + PostGIS installed and running
- ✅ Database schema created with spatial indexes
- ✅ Registered for Copernicus and NASA APIs
- ✅ Downloaded 100+ real flood/vegetation records
- ✅ Data loaded into database
- ✅ Tested spatial queries
- ✅ **Git Checkpoint**: Day 1 complete, ready to push

---

## ⏰ Timeline

| Time | Checkpoint | Duration | Status |
|------|------------|----------|--------|
| 9:00 AM | 1.1: PostgreSQL Setup | 1 hour | ⬜ |
| 10:00 AM | 1.2: Database Schema | 1 hour | ⬜ |
| 11:00 AM | Break | 15 min | ⬜ |
| 11:15 AM | 1.3: API Registration | 1.5 hours | ⬜ |
| 12:45 PM | Lunch | 1 hour | ⬜ |
| 1:45 PM | 1.4: Data Collection | 2.5 hours | ⬜ |
| 4:15 PM | Break | 15 min | ⬜ |
| 4:30 PM | 1.5: Data Loading | 1 hour | ⬜ |
| 5:30 PM | Day 1 Review & Git Push | 30 min | ⬜ |

---

## 🚀 Checkpoint 1.1: PostgreSQL + PostGIS Setup

### Time: 9:00 AM - 10:00 AM (1 hour)

### Step 1: Download PostgreSQL

1. **Go to**: https://www.postgresql.org/download/windows/
2. **Download**: PostgreSQL 15.x or 16.x installer
3. **Run installer**:
   - Installation directory: `C:\Program Files\PostgreSQL\15`
   - Port: `5432` (default)
   - **IMPORTANT**: Remember your postgres password!
   - Install Stack Builder: ✅ Yes

### Step 2: Install PostGIS

1. **After PostgreSQL installs**, Stack Builder will open
2. **Select**: Your PostgreSQL installation
3. **Choose**: Spatial Extensions → PostGIS 3.3+
4. **Install** with all dependencies

### Step 3: Verify Installation

```bash
# Open Command Prompt or PowerShell
# Check PostgreSQL is running
pg_isready -U postgres

# Should output: "accepting connections"
```

### Step 4: Create Database

```bash
# Create database
createdb -U postgres earth_obs

# You'll be prompted for postgres password
```

### Step 5: Enable PostGIS

```bash
# Enable PostGIS extension
psql -U postgres -d earth_obs -c "CREATE EXTENSION postgis;"
psql -U postgres -d earth_obs -c "CREATE EXTENSION postgis_topology;"

# Verify PostGIS
psql -U postgres -d earth_obs -c "SELECT PostGIS_Version();"
```

### Step 6: Test Connection with Python

Create `scripts/test_db_connection.py`:

```python
import psycopg2
from psycopg2.extras import RealDictCursor

def test_connection():
    try:
        # Connect to database
        conn = psycopg2.connect(
            dbname="earth_obs",
            user="postgres",
            password="YOUR_PASSWORD",  # Replace with your password
            host="localhost",
            port="5432"
        )
        
        # Test query
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT PostGIS_Version();")
        result = cursor.fetchone()
        
        print("✅ Database connection successful!")
        print(f"✅ PostGIS version: {result['postgis_version']}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()
```

Run test:
```bash
python scripts/test_db_connection.py
```

### ✅ Checkpoint 1.1 Complete!

**Git Commit**:
```bash
git add scripts/test_db_connection.py
git commit -m "Checkpoint 1.1: PostgreSQL + PostGIS setup complete"
```

---

## 🗄️ Checkpoint 1.2: Database Schema Creation

### Time: 10:00 AM - 11:00 AM (1 hour)

### Step 1: Create Schema SQL File

Create `database/schema.sql`:

```sql
-- ============================================
-- Earth Observation Database Schema
-- ============================================

-- Enable PostGIS (if not already enabled)
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- ============================================
-- Table: flood_events
-- ============================================
CREATE TABLE IF NOT EXISTS flood_events (
    id SERIAL PRIMARY KEY,
    event_id VARCHAR(50) UNIQUE NOT NULL,
    state VARCHAR(100) NOT NULL,
    district VARCHAR(100),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    affected_area_sqkm DECIMAL(10,2),
    severity VARCHAR(20) CHECK (severity IN ('low', 'medium', 'high', 'extreme')),
    satellite_source VARCHAR(50),
    resolution_m INTEGER,
    confidence_score DECIMAL(3,2) CHECK (confidence_score BETWEEN 0 AND 1),
    geometry GEOMETRY(MultiPolygon, 4326),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for flood_events
CREATE INDEX idx_flood_state ON flood_events(state);
CREATE INDEX idx_flood_dates ON flood_events(start_date, end_date);
CREATE INDEX idx_flood_severity ON flood_events(severity);
CREATE INDEX idx_flood_geometry ON flood_events USING GIST(geometry);
CREATE INDEX idx_flood_created ON flood_events(created_at);

-- ============================================
-- Table: vegetation_data
-- ============================================
CREATE TABLE IF NOT EXISTS vegetation_data (
    id SERIAL PRIMARY KEY,
    observation_id VARCHAR(50) UNIQUE NOT NULL,
    state VARCHAR(100) NOT NULL,
    district VARCHAR(100),
    observation_date DATE NOT NULL,
    ndvi_mean DECIMAL(4,3) CHECK (ndvi_mean BETWEEN -1 AND 1),
    ndvi_std DECIMAL(4,3),
    evi_mean DECIMAL(4,3),
    crop_type VARCHAR(50),
    health_status VARCHAR(20) CHECK (health_status IN ('healthy', 'stressed', 'critical')),
    satellite_source VARCHAR(50),
    resolution_m INTEGER,
    cloud_cover_percent DECIMAL(5,2) CHECK (cloud_cover_percent BETWEEN 0 AND 100),
    geometry GEOMETRY(MultiPolygon, 4326),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for vegetation_data
CREATE INDEX idx_veg_state ON vegetation_data(state);
CREATE INDEX idx_veg_date ON vegetation_data(observation_date);
CREATE INDEX idx_veg_health ON vegetation_data(health_status);
CREATE INDEX idx_veg_geometry ON vegetation_data USING GIST(geometry);
CREATE INDEX idx_veg_created ON vegetation_data(created_at);

-- ============================================
-- Table: satellite_coverage
-- ============================================
CREATE TABLE IF NOT EXISTS satellite_coverage (
    id SERIAL PRIMARY KEY,
    satellite_name VARCHAR(50) NOT NULL,
    sensor_type VARCHAR(50),
    acquisition_date TIMESTAMP NOT NULL,
    state VARCHAR(100),
    district VARCHAR(100),
    cloud_cover_percent DECIMAL(5,2) CHECK (cloud_cover_percent BETWEEN 0 AND 100),
    processing_level VARCHAR(20),
    data_available BOOLEAN DEFAULT TRUE,
    download_url TEXT,
    geometry GEOMETRY(Polygon, 4326),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for satellite_coverage
CREATE INDEX idx_sat_name ON satellite_coverage(satellite_name);
CREATE INDEX idx_sat_date ON satellite_coverage(acquisition_date);
CREATE INDEX idx_sat_state ON satellite_coverage(state);
CREATE INDEX idx_sat_geometry ON satellite_coverage USING GIST(geometry);

-- ============================================
-- Table: data_quality_log
-- ============================================
CREATE TABLE IF NOT EXISTS data_quality_log (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(50) NOT NULL,
    record_id INTEGER,
    quality_check VARCHAR(100) NOT NULL,
    status VARCHAR(20) CHECK (status IN ('passed', 'failed', 'warning')),
    details TEXT,
    checked_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_quality_table ON data_quality_log(table_name);
CREATE INDEX idx_quality_status ON data_quality_log(status);
CREATE INDEX idx_quality_date ON data_quality_log(checked_at);

-- ============================================
-- Views for Common Queries
-- ============================================

-- Recent flood events (last 30 days)
CREATE OR REPLACE VIEW recent_floods AS
SELECT 
    state,
    district,
    COUNT(*) as event_count,
    SUM(affected_area_sqkm) as total_area_sqkm,
    MAX(end_date) as latest_event,
    AVG(confidence_score) as avg_confidence
FROM flood_events
WHERE end_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY state, district
ORDER BY total_area_sqkm DESC;

-- Vegetation health summary (last 90 days)
CREATE OR REPLACE VIEW vegetation_health_summary AS
SELECT 
    state,
    district,
    DATE_TRUNC('week', observation_date) as week,
    AVG(ndvi_mean) as avg_ndvi,
    COUNT(*) as observation_count,
    COUNT(CASE WHEN health_status = 'stressed' THEN 1 END) as stressed_count,
    COUNT(CASE WHEN health_status = 'critical' THEN 1 END) as critical_count
FROM vegetation_data
WHERE observation_date >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY state, district, DATE_TRUNC('week', observation_date)
ORDER BY week DESC, state;

-- Satellite availability summary
CREATE OR REPLACE VIEW satellite_availability AS
SELECT 
    satellite_name,
    state,
    DATE_TRUNC('month', acquisition_date) as month,
    COUNT(*) as scene_count,
    AVG(cloud_cover_percent) as avg_cloud_cover,
    COUNT(CASE WHEN data_available THEN 1 END) as available_count
FROM satellite_coverage
WHERE acquisition_date >= CURRENT_DATE - INTERVAL '6 months'
GROUP BY satellite_name, state, DATE_TRUNC('month', acquisition_date)
ORDER BY month DESC, satellite_name;

-- ============================================
-- Functions
-- ============================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_flood_events_updated_at BEFORE UPDATE ON flood_events
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_vegetation_data_updated_at BEFORE UPDATE ON vegetation_data
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- Sample Data for Testing
-- ============================================

-- Insert sample flood event
INSERT INTO flood_events (
    event_id, state, district, start_date, end_date,
    affected_area_sqkm, severity, satellite_source,
    confidence_score, geometry
) VALUES (
    'FLOOD_TEST_001',
    'Tamil Nadu',
    'Chennai',
    '2024-02-20',
    '2024-02-25',
    250.5,
    'high',
    'Sentinel-1',
    0.95,
    ST_GeomFromText('MULTIPOLYGON(((80.2 13.0, 80.3 13.0, 80.3 13.1, 80.2 13.1, 80.2 13.0)))', 4326)
) ON CONFLICT (event_id) DO NOTHING;

-- Insert sample vegetation data
INSERT INTO vegetation_data (
    observation_id, state, district, observation_date,
    ndvi_mean, health_status, satellite_source, geometry
) VALUES (
    'VEG_TEST_001',
    'Kerala',
    'Wayanad',
    '2024-02-15',
    0.75,
    'healthy',
    'Sentinel-2',
    ST_GeomFromText('MULTIPOLYGON(((76.0 11.6, 76.1 11.6, 76.1 11.7, 76.0 11.7, 76.0 11.6)))', 4326)
) ON CONFLICT (observation_id) DO NOTHING;

-- ============================================
-- Grant Permissions (if needed)
-- ============================================

-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO your_user;

-- ============================================
-- Schema Creation Complete
-- ============================================
```

### Step 2: Run Schema Creation

Create `scripts/init_database.py`:

```python
import psycopg2
import os

def init_database():
    """Initialize database schema"""
    
    # Database connection
    conn = psycopg2.connect(
        dbname="earth_obs",
        user="postgres",
        password=os.getenv("DB_PASSWORD", "YOUR_PASSWORD"),
        host="localhost",
        port="5432"
    )
    
    # Read schema file
    with open('database/schema.sql', 'r') as f:
        schema_sql = f.read()
    
    # Execute schema
    cursor = conn.cursor()
    try:
        cursor.execute(schema_sql)
        conn.commit()
        print("✅ Database schema created successfully!")
        
        # Verify tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        print(f"\n📊 Created {len(tables)} tables:")
        for table in tables:
            print(f"   - {table[0]}")
            
    except Exception as e:
        conn.rollback()
        print(f"❌ Error creating schema: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    init_database()
```

Run:
```bash
python scripts/init_database.py
```

### Step 3: Verify Schema

Create `scripts/verify_schema.py`:

```python
import psycopg2
from psycopg2.extras import RealDictCursor

def verify_schema():
    """Verify database schema and test queries"""
    
    conn = psycopg2.connect(
        dbname="earth_obs",
        user="postgres",
        password="YOUR_PASSWORD",
        host="localhost"
    )
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Test 1: Check tables exist
    cursor.execute("""
        SELECT COUNT(*) as table_count
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_type = 'BASE TABLE';
    """)
    result = cursor.fetchone()
    print(f"✅ Tables created: {result['table_count']}")
    
    # Test 2: Check PostGIS functions
    cursor.execute("SELECT PostGIS_Full_Version();")
    print("✅ PostGIS working")
    
    # Test 3: Check sample data
    cursor.execute("SELECT COUNT(*) FROM flood_events;")
    flood_count = cursor.fetchone()['count']
    print(f"✅ Sample flood events: {flood_count}")
    
    cursor.execute("SELECT COUNT(*) FROM vegetation_data;")
    veg_count = cursor.fetchone()['count']
    print(f"✅ Sample vegetation data: {veg_count}")
    
    # Test 4: Test spatial query
    cursor.execute("""
        SELECT 
            event_id,
            state,
            ST_Area(geometry::geography) / 1000000 as area_sqkm
        FROM flood_events
        LIMIT 1;
    """)
    result = cursor.fetchone()
    if result:
        print(f"✅ Spatial queries working: {result['event_id']}")
    
    cursor.close()
    conn.close()
    
    print("\n🎉 Schema verification complete!")

if __name__ == "__main__":
    verify_schema()
```

Run:
```bash
python scripts/verify_schema.py
```

### ✅ Checkpoint 1.2 Complete!

**Git Commit**:
```bash
git add database/schema.sql scripts/init_database.py scripts/verify_schema.py
git commit -m "Checkpoint 1.2: Database schema created and verified"
```

---

## ☕ Break: 11:00 AM - 11:15 AM (15 minutes)

Take a break! You've completed the database setup. Next up: API registration.

---

## 🔑 Checkpoint 1.3: Data Source Registration

### Time: 11:15 AM - 12:45 PM (1.5 hours)

### Step 1: Register for Copernicus Data Space

1. **Go to**: https://dataspace.copernicus.eu/
2. **Click**: "Register" (top right)
3. **Fill in details**:
   - Email
   - Username
   - Password
   - Accept terms
4. **Verify email**
5. **Login** and go to "API Keys"
6. **Create API Key**
7. **Save credentials**

### Step 2: Register for NASA EarthData

1. **Go to**: https://urs.earthdata.nasa.gov/users/new
2. **Register** with:
   - Email
   - Username
   - Password
3. **Verify email**
4. **Login** and go to "Applications" → "Generate Token"
5. **Save token**

### Step 3: Update .env File

```bash
# Database
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/earth_obs

# Groq API (already configured)
OPENAI_API_KEY=your_groq_api_key_here
OPENAI_MODEL=llama-3.3-70b-versatile

# Copernicus
COPERNICUS_USERNAME=your_username
COPERNICUS_PASSWORD=your_password

# NASA EarthData
NASA_TOKEN=your_token_here
```

### Step 4: Test API Access

Create `scripts/test_api_access.py`:

```python
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def test_copernicus():
    """Test Copernicus API access"""
    print("Testing Copernicus API...")
    
    # Test endpoint (example)
    url = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products?$top=1"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print("✅ Copernicus API accessible")
            return True
        else:
            print(f"⚠️  Copernicus API returned: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Copernicus API error: {e}")
        return False

def test_nasa():
    """Test NASA EarthData API access"""
    print("Testing NASA EarthData API...")
    
    token = os.getenv("NASA_TOKEN")
    if not token:
        print("❌ NASA_TOKEN not found in .env")
        return False
    
    # Test endpoint
    url = "https://cmr.earthdata.nasa.gov/search/collections.json?keyword=MODIS"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            print("✅ NASA EarthData API accessible")
            return True
        else:
            print(f"⚠️  NASA API returned: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ NASA API error: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing API Access...\n")
    
    copernicus_ok = test_copernicus()
    nasa_ok = test_nasa()
    
    print("\n" + "="*50)
    if copernicus_ok and nasa_ok:
        print("🎉 All APIs accessible!")
    else:
        print("⚠️  Some APIs not accessible - check credentials")
```

Run:
```bash
python scripts/test_api_access.py
```

### ✅ Checkpoint 1.3 Complete!

**Git Commit**:
```bash
git add .env scripts/test_api_access.py
git commit -m "Checkpoint 1.3: Data source APIs registered and tested"
```

---

## 🍽️ Lunch Break: 12:45 PM - 1:45 PM (1 hour)

Great progress! You've set up the database and registered for APIs. After lunch, we'll collect real data!

---

## 📥 Checkpoint 1.4: Sample Data Collection

### Time: 1:45 PM - 4:15 PM (2.5 hours)

This is where we download real satellite data! We'll create scripts to collect flood and vegetation data.

### Coming in next message...

---

**Current Progress**: 3/5 checkpoints complete! 🎉

**Next**: Data collection scripts and loading data into database.
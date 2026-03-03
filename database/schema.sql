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
CREATE INDEX IF NOT EXISTS idx_flood_state ON flood_events(state);
CREATE INDEX IF NOT EXISTS idx_flood_dates ON flood_events(start_date, end_date);
CREATE INDEX IF NOT EXISTS idx_flood_severity ON flood_events(severity);
CREATE INDEX IF NOT EXISTS idx_flood_geometry ON flood_events USING GIST(geometry);
CREATE INDEX IF NOT EXISTS idx_flood_created ON flood_events(created_at);

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
CREATE INDEX IF NOT EXISTS idx_veg_state ON vegetation_data(state);
CREATE INDEX IF NOT EXISTS idx_veg_date ON vegetation_data(observation_date);
CREATE INDEX IF NOT EXISTS idx_veg_health ON vegetation_data(health_status);
CREATE INDEX IF NOT EXISTS idx_veg_geometry ON vegetation_data USING GIST(geometry);
CREATE INDEX IF NOT EXISTS idx_veg_created ON vegetation_data(created_at);

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
CREATE INDEX IF NOT EXISTS idx_sat_name ON satellite_coverage(satellite_name);
CREATE INDEX IF NOT EXISTS idx_sat_date ON satellite_coverage(acquisition_date);
CREATE INDEX IF NOT EXISTS idx_sat_state ON satellite_coverage(state);
CREATE INDEX IF NOT EXISTS idx_sat_geometry ON satellite_coverage USING GIST(geometry);

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

CREATE INDEX IF NOT EXISTS idx_quality_table ON data_quality_log(table_name);
CREATE INDEX IF NOT EXISTS idx_quality_status ON data_quality_log(status);
CREATE INDEX IF NOT EXISTS idx_quality_date ON data_quality_log(checked_at);

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
DROP TRIGGER IF EXISTS update_flood_events_updated_at ON flood_events;
CREATE TRIGGER update_flood_events_updated_at BEFORE UPDATE ON flood_events
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_vegetation_data_updated_at ON vegetation_data;
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
-- Schema Creation Complete
-- ============================================
-- Flood Events Schema V2 - Simplified for MVP
-- Essential columns only, optimized for natural language queries

-- Drop existing table if it exists
DROP TABLE IF EXISTS flood_events CASCADE;

-- Create flood_events table
CREATE TABLE flood_events (
    -- Primary identifier
    uei VARCHAR(50) PRIMARY KEY,
    
    -- Temporal information
    start_date DATE NOT NULL,
    end_date DATE,
    duration_days INTEGER,
    
    -- Spatial information
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    state VARCHAR(100),
    district VARCHAR(100),
    geometry GEOMETRY(Point, 4326),
    
    -- Flood characteristics
    severity VARCHAR(50),
    area_affected_sqkm DECIMAL(10, 2),
    main_cause TEXT,
    description TEXT,
    
    -- Metadata
    event_source VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for common query patterns
CREATE INDEX idx_flood_state ON flood_events(state);
CREATE INDEX idx_flood_district ON flood_events(district);
CREATE INDEX idx_flood_start_date ON flood_events(start_date);
CREATE INDEX idx_flood_end_date ON flood_events(end_date);
CREATE INDEX idx_flood_severity ON flood_events(severity);
CREATE INDEX idx_flood_area ON flood_events(area_affected_sqkm);

-- Create spatial index for geometry queries
CREATE INDEX idx_flood_geometry ON flood_events USING GIST(geometry);

-- Create composite indexes for common query combinations
CREATE INDEX idx_flood_state_date ON flood_events(state, start_date);
CREATE INDEX idx_flood_state_severity ON flood_events(state, severity);
CREATE INDEX idx_flood_date_severity ON flood_events(start_date, severity);

-- Create trigger to auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_flood_events_updated_at 
    BEFORE UPDATE ON flood_events
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create useful views for common queries

-- View: Recent floods (last 30 days)
CREATE OR REPLACE VIEW recent_floods AS
SELECT 
    uei,
    state,
    district,
    start_date,
    end_date,
    severity,
    area_affected_sqkm,
    main_cause,
    description
FROM flood_events
WHERE start_date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY start_date DESC;

-- View: Severe floods (High, Severe, Catastrophic)
CREATE OR REPLACE VIEW severe_floods AS
SELECT 
    uei,
    state,
    district,
    start_date,
    severity,
    area_affected_sqkm,
    main_cause
FROM flood_events
WHERE severity IN ('High', 'Severe', 'Catastrophic')
ORDER BY start_date DESC;

-- View: Floods by state summary
CREATE OR REPLACE VIEW floods_by_state AS
SELECT 
    state,
    COUNT(*) as total_events,
    SUM(area_affected_sqkm) as total_area_affected,
    AVG(area_affected_sqkm) as avg_area_affected,
    MIN(start_date) as earliest_flood,
    MAX(start_date) as latest_flood
FROM flood_events
GROUP BY state
ORDER BY total_events DESC;

-- View: Floods by year
CREATE OR REPLACE VIEW floods_by_year AS
SELECT 
    EXTRACT(YEAR FROM start_date) as year,
    COUNT(*) as total_events,
    SUM(area_affected_sqkm) as total_area_affected,
    AVG(duration_days) as avg_duration_days
FROM flood_events
GROUP BY EXTRACT(YEAR FROM start_date)
ORDER BY year DESC;

-- Grant permissions (adjust as needed)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON flood_events TO your_user;
-- GRANT SELECT ON recent_floods, severe_floods, floods_by_state, floods_by_year TO your_user;

-- Print success message
DO $$
BEGIN
    RAISE NOTICE 'Flood Events Schema V2 created successfully!';
    RAISE NOTICE 'Tables: flood_events';
    RAISE NOTICE 'Views: recent_floods, severe_floods, floods_by_state, floods_by_year';
    RAISE NOTICE 'Indexes: 10 indexes created for optimized queries';
END $$;
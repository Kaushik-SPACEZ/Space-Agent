# 🌍 Earth Observation Agent V2.0 - Database-Driven Architecture

**Multi-Pipeline Natural Language Spatial Intelligence Engine**

> Transform natural language queries into SQL, query real Earth observation databases, and return structured geospatial insights.

---

## 🎯 Project Vision

Build a production-ready Earth Observation Agent that:
- Accepts natural language queries about Earth events
- Converts queries to SQL using LLM (Text-to-SQL)
- Queries PostgreSQL + PostGIS database with real satellite data
- Returns structured, validated geospatial results
- Supports multiple data types: floods, vegetation, satellite coverage

---

## 🏗️ Architecture V2.0

```
┌─────────────────────────────────────────────────────────────┐
│                    USER QUERY                                │
│          "Show flood in Tamil Nadu past 2 weeks"            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              LLM (Intent Extraction)                         │
│  • Groq API (llama-3.3-70b-versatile)                      │
│  • Extracts structured JSON from natural language           │
│  • Returns: domain, event_type, location, dates            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│           Backend (JSON → Parameterized SQL)                │
│  • Converts JSON to safe SQL queries                        │
│  • Uses parameterized queries (SQL injection safe)          │
│  • Query templates with placeholders                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              PostgreSQL + PostGIS Database                   │
│  ┌──────────────┬──────────────┬──────────────┐            │
│  │ flood_events │ vegetation   │ satellites   │            │
│  │ (Sentinel-1) │ (NDVI data)  │ (metadata)   │            │
│  └──────────────┴──────────────┴──────────────┘            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              PREPROCESSING PIPELINE                          │
│  • Data Ingestion (Copernicus, NASA APIs)                  │
│  • Validation & Quality Checks                              │
│  • Transformation & Standardization                         │
│  • Automated Updates (Daily/Weekly)                         │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Data Sources

### 1. Flood Data
- **Copernicus Emergency Management Service (CEMS)**
  - Coverage: Global, event-based
  - Format: GeoJSON, Shapefiles
  - Access: Free (registration required)
  - URL: https://emergency.copernicus.eu/

- **Sentinel-1 SAR**
  - Coverage: Global, 12-day revisit
  - Format: GeoTIFF
  - Processing: Flood detection algorithms
  - URL: https://scihub.copernicus.eu/

### 2. Vegetation/Crop Data
- **Sentinel-2 Multispectral**
  - Coverage: Global, 5-day revisit
  - Format: GeoTIFF
  - Indices: NDVI, EVI
  - Resolution: 10m-60m

- **MODIS Vegetation Indices**
  - Coverage: Global, daily
  - Format: HDF, GeoTIFF
  - Products: MOD13Q1
  - Resolution: 250m

### 3. Satellite Metadata
- **Copernicus Data Space**
  - STAC API for metadata
  - All Sentinel missions
  - Query by location, time, cloud cover

---

## 🗄️ Database Schema

### Core Tables

```sql
-- Flood Events
CREATE TABLE flood_events (
    id SERIAL PRIMARY KEY,
    event_id VARCHAR(50) UNIQUE,
    state VARCHAR(100),
    district VARCHAR(100),
    start_date DATE,
    end_date DATE,
    affected_area_sqkm DECIMAL(10,2),
    severity VARCHAR(20),
    satellite_source VARCHAR(50),
    confidence_score DECIMAL(3,2),
    geometry GEOMETRY(MultiPolygon, 4326),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Vegetation Data
CREATE TABLE vegetation_data (
    id SERIAL PRIMARY KEY,
    observation_id VARCHAR(50) UNIQUE,
    state VARCHAR(100),
    district VARCHAR(100),
    observation_date DATE,
    ndvi_mean DECIMAL(4,3),
    health_status VARCHAR(20),
    satellite_source VARCHAR(50),
    geometry GEOMETRY(MultiPolygon, 4326),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Satellite Coverage
CREATE TABLE satellite_coverage (
    id SERIAL PRIMARY KEY,
    satellite_name VARCHAR(50),
    acquisition_date TIMESTAMP,
    state VARCHAR(100),
    cloud_cover_percent DECIMAL(5,2),
    data_available BOOLEAN,
    geometry GEOMETRY(Polygon, 4326),
    metadata JSONB
);
```

---

## 🚀 3-Day Implementation Sprint

### Day 1: Data Collection & Database Setup
**Checkpoint 1: Database with Sample Data**

- [x] Set up PostgreSQL + PostGIS
- [x] Create database schema
- [x] Register for data source APIs
- [x] Download sample datasets
- [x] Load initial data (100+ records)
- [x] Test spatial queries

**Deliverable**: Working database with real data

---

### Day 2: Preprocessing Pipeline & Text-to-SQL
**Checkpoint 2: Automated Data Pipeline**

- [ ] Build data extraction scripts
- [ ] Implement validation rules
- [ ] Create transformation logic
- [ ] Build Text-to-SQL converter
- [ ] Test SQL generation

**Deliverable**: Pipeline that ingests and processes data

---

### Day 3: API Integration & Testing
**Checkpoint 3: Complete Working System**

- [ ] Update API endpoints
- [ ] Integrate Text-to-SQL with database
- [ ] End-to-end testing
- [ ] Performance optimization
- [ ] Documentation

**Deliverable**: Production-ready API

---

## 🛠️ Tech Stack

### Backend
- **FastAPI**: REST API framework
- **PostgreSQL 15+**: Relational database
- **PostGIS 3.3+**: Spatial extensions
- **SQLAlchemy**: ORM
- **GeoAlchemy2**: Spatial ORM extensions

### Data Processing
- **Pandas**: Data manipulation
- **GeoPandas**: Geospatial data
- **GDAL/Rasterio**: Raster processing
- **Shapely**: Geometry operations

### AI/ML
- **Groq API**: LLM for Text-to-SQL
- **Model**: llama-3.3-70b-versatile
- **OpenAI SDK**: API client

### Automation
- **APScheduler**: Task scheduling
- **Python-dotenv**: Environment management

---

## 📦 Installation

### Prerequisites
```bash
# Install PostgreSQL + PostGIS
# Windows: Download from https://www.postgresql.org/download/windows/
# Include PostGIS in Stack Builder

# Install Python dependencies
pip install -r requirements.txt
```

### Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Configure .env
DATABASE_URL=postgresql://user:password@localhost:5432/earth_obs
OPENAI_API_KEY=your_groq_api_key
OPENAI_MODEL=llama-3.3-70b-versatile
```

### Database Initialization
```bash
# Create database
createdb earth_obs

# Enable PostGIS
psql -d earth_obs -c "CREATE EXTENSION postgis;"

# Run migrations
python scripts/init_database.py
```

---

## 🔥 Architecture Flow Example

### User Query → JSON → Parameterized SQL → Results

**Step 1: User Query**
```
"Show flood in Tamil Nadu past 2 weeks"
```

**Step 2: LLM Extracts Structured Intent (JSON)**
```json
{
  "domain": "earth",
  "event_type": "flood",
  "state": "Tamil Nadu",
  "start_date": "2026-02-15",
  "end_date": "2026-03-01"
}
```

**Step 3: Backend Converts to Parameterized SQL**
```python
# Safe parameterized query
query = """
    SELECT 
        event_id,
        state,
        district,
        start_date,
        end_date,
        affected_area_sqkm,
        severity,
        ST_AsGeoJSON(geometry) as geometry
    FROM flood_events
    WHERE state = %s
    AND start_date >= %s
    AND end_date <= %s
    ORDER BY start_date DESC
"""

# Execute with parameters (SQL injection safe!)
params = (intent['state'], intent['start_date'], intent['end_date'])
results = db.execute(query, params)
```

**Step 4: LLM Formats Final Explanation**
```json
{
  "query": "Show flood in Tamil Nadu past 2 weeks",
  "intent_extracted": {
    "event_type": "flood",
    "state": "Tamil Nadu",
    "date_range": "2026-02-15 to 2026-03-01"
  },
  "results": {
    "total_events": 3,
    "events": [...]
  },
  "explanation": "Found 3 flood events in Tamil Nadu between Feb 15 and Mar 1, 2026. Total affected area: 450.5 sq km."
}
```

### ✅ Why This Approach is Safe & Professional

1. **SQL Injection Prevention**: Parameterized queries with `%s` placeholders
2. **Controlled Execution**: Backend controls SQL generation, not LLM
3. **Validation**: Intent JSON is validated before SQL generation
4. **Auditable**: All queries logged with parameters
5. **Testable**: Easy to unit test SQL templates

---

## 🎯 Usage

### Start the API Server
```bash
python main.py
```

### Example Queries

**Flood Query:**
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Show flood events in Tamil Nadu past 2 weeks"}'
```

**Vegetation Query:**
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Crop stress in Kerala during January 2024"}'
```

**Satellite Availability:**
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Available Sentinel-2 data for Maharashtra in March 2024"}'
```

---

## 📊 Response Format

```json
{
  "query": "Show flood in Tamil Nadu past 2 weeks",
  "sql_generated": "SELECT * FROM flood_events WHERE...",
  "results": {
    "total_events": 3,
    "total_area_affected_sqkm": 450.5,
    "events": [
      {
        "event_id": "FLOOD_TN_2024_001",
        "state": "Tamil Nadu",
        "district": "Chennai",
        "start_date": "2024-02-20",
        "end_date": "2024-02-25",
        "affected_area_sqkm": 250.3,
        "severity": "high",
        "satellite_source": "Sentinel-1",
        "geometry": {...}
      }
    ]
  },
  "metadata": {
    "query_time_ms": 145,
    "data_sources": ["Sentinel-1", "CEMS"],
    "confidence": 0.95
  }
}
```

---

## 🔄 Data Pipeline

### Automated Updates

```python
# Daily: Flood events
# Weekly: Vegetation indices
# Monthly: Satellite metadata

# Run scheduler
python scripts/run_scheduler.py
```

### Manual Data Ingestion

```python
# Ingest flood data
python scripts/ingest_flood_data.py --source copernicus --date-range 2024-01-01:2024-03-01

# Ingest vegetation data
python scripts/ingest_vegetation_data.py --source sentinel2 --state "Tamil Nadu"
```

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Test database connection
python tests/test_database.py

# Test Text-to-SQL
python tests/test_text_to_sql.py

# Test API endpoints
python tests/test_api.py
```

---

## 📈 Performance Metrics

### Target Metrics
- Query Response Time: < 2 seconds
- Text-to-SQL Accuracy: > 90%
- Data Freshness: < 24 hours
- API Throughput: 100+ requests/minute
- Database Size: 10GB+ (scalable)

### Monitoring
- Database query performance
- API response times
- Data ingestion success rates
- LLM API usage and costs

---

## 🔐 Security

- SQL injection prevention (parameterized queries)
- API rate limiting
- Input validation and sanitization
- Database access controls
- Environment variable protection

---

## 📚 Documentation

- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **Database Schema**: `docs/database_schema.md`
- **Data Sources**: `docs/data_sources.md`
- **Deployment Guide**: `docs/deployment.md`

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📝 Changelog

### V2.0.0 (Current)
- ✅ Database-driven architecture
- ✅ Text-to-SQL conversion
- ✅ Real satellite data integration
- ✅ Automated data pipeline
- ✅ PostGIS spatial queries

### V1.0.0 (Previous)
- CSV-based data storage
- LLM parameter extraction
- Basic pipeline routing
- Sample datasets

---

## 🎯 Roadmap

### Phase 1 (Week 1-2) ✅
- Database setup
- Sample data ingestion
- Basic Text-to-SQL

### Phase 2 (Week 3-4)
- Full data pipeline
- Multiple data sources
- Advanced spatial queries

### Phase 3 (Week 5-6)
- Performance optimization
- Caching layer
- Real-time updates

### Phase 4 (Week 7-8)
- Production deployment
- Monitoring & alerts
- User documentation

---

## 📞 Support

- **Issues**: https://github.com/KaushikSAP/Space-Agent/issues
- **Discussions**: https://github.com/KaushikSAP/Space-Agent/discussions
- **Email**: support@earthobservationagent.com

---

## 📄 License

MIT License - see LICENSE file for details

---

## 🙏 Acknowledgments

- **Copernicus Programme**: For free satellite data
- **NASA EarthData**: For MODIS products
- **Groq**: For free LLM API
- **PostGIS**: For spatial database capabilities

---

**Built with ❤️ for Earth Observation and Spatial Intelligence**

*Last Updated: March 3, 2026*
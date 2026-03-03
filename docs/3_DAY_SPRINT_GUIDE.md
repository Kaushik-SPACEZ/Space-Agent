# 🚀 3-Day Sprint Guide: Earth Observation Agent V2.0

**Goal**: Transform from CSV-based to database-driven architecture with real satellite data

---

## 📅 Day 1: Data Collection & Database Setup

### Morning Session (4 hours)

#### Checkpoint 1.1: PostgreSQL + PostGIS Setup ✅
**Time**: 1 hour

1. **Install PostgreSQL**
   ```bash
   # Download PostgreSQL 15+ from:
   # https://www.postgresql.org/download/windows/
   
   # During installation:
   # - Remember your postgres password
   # - Default port: 5432
   # - Include Stack Builder
   ```

2. **Install PostGIS**
   ```bash
   # In Stack Builder:
   # - Select your PostgreSQL installation
   # - Choose PostGIS 3.3+
   # - Install with all dependencies
   ```

3. **Create Database**
   ```bash
   # Open pgAdmin or command line
   createdb -U postgres earth_obs
   
   # Enable PostGIS extension
   psql -U postgres -d earth_obs -c "CREATE EXTENSION postgis;"
   psql -U postgres -d earth_obs -c "CREATE EXTENSION postgis_topology;"
   ```

4. **Test Connection**
   ```python
   # Test script
   python scripts/test_db_connection.py
   ```

**Git Checkpoint**: `git commit -m "Day 1.1: PostgreSQL + PostGIS setup complete"`

---

#### Checkpoint 1.2: Database Schema Creation ✅
**Time**: 1 hour

1. **Create Schema SQL File**
   - File: `database/schema.sql`
   - Tables: flood_events, vegetation_data, satellite_coverage
   - Indexes: Spatial + temporal indexes
   - Views: Common query patterns

2. **Run Schema Creation**
   ```bash
   python scripts/init_database.py
   ```

3. **Verify Schema**
   ```bash
   python scripts/verify_schema.py
   ```

**Git Checkpoint**: `git commit -m "Day 1.2: Database schema created and verified"`

---

### Afternoon Session (4 hours)

#### Checkpoint 1.3: Data Source Registration ✅
**Time**: 1.5 hours

1. **Register for Copernicus**
   - URL: https://dataspace.copernicus.eu/
   - Create account (free)
   - Get API credentials
   - Test API access

2. **Register for NASA EarthData**
   - URL: https://urs.earthdata.nasa.gov/
   - Create account (free)
   - Get API token
   - Test API access

3. **Save Credentials**
   ```bash
   # Add to .env
   COPERNICUS_USERNAME=your_username
   COPERNICUS_PASSWORD=your_password
   NASA_TOKEN=your_token
   ```

**Git Checkpoint**: `git commit -m "Day 1.3: Data source APIs registered"`

---

#### Checkpoint 1.4: Sample Data Collection ✅
**Time**: 2.5 hours

1. **Download Flood Data**
   ```bash
   # Run data collection script
   python scripts/collect_flood_data.py --state "Tamil Nadu" --days 90
   ```

2. **Download Vegetation Data**
   ```bash
   python scripts/collect_vegetation_data.py --state "Kerala" --days 90
   ```

3. **Verify Downloaded Data**
   ```bash
   # Check data directory
   ls -la data/raw/floods/
   ls -la data/raw/vegetation/
   ```

**Git Checkpoint**: `git commit -m "Day 1.4: Sample data collected (100+ records)"`

---

#### Checkpoint 1.5: Data Loading ✅
**Time**: 1 hour (Evening)

1. **Load Flood Data**
   ```bash
   python scripts/load_flood_data.py
   ```

2. **Load Vegetation Data**
   ```bash
   python scripts/load_vegetation_data.py
   ```

3. **Verify Data in Database**
   ```bash
   python scripts/verify_data_load.py
   ```

4. **Test Spatial Queries**
   ```bash
   python scripts/test_spatial_queries.py
   ```

**Git Checkpoint**: `git commit -m "Day 1.5: Data loaded into database - DAY 1 COMPLETE"`

**Day 1 Deliverable**: ✅ Working PostgreSQL database with 100+ real satellite records

---

## 📅 Day 2: Preprocessing Pipeline & Text-to-SQL

### Morning Session (4 hours)

#### Checkpoint 2.1: Data Extraction Module ✅
**Time**: 1.5 hours

1. **Create Base Extractor**
   - File: `preprocessing/extractors/base.py`
   - Abstract class for all extractors

2. **Copernicus Extractor**
   - File: `preprocessing/extractors/copernicus.py`
   - Flood data extraction
   - API authentication

3. **NASA Extractor**
   - File: `preprocessing/extractors/nasa.py`
   - MODIS NDVI extraction
   - Token-based auth

**Git Checkpoint**: `git commit -m "Day 2.1: Data extraction modules created"`

---

#### Checkpoint 2.2: Data Validation ✅
**Time**: 1.5 hours

1. **Create Validators**
   - File: `preprocessing/validators.py`
   - Required fields check
   - Value range validation
   - Geometry validation
   - Temporal consistency

2. **Test Validators**
   ```bash
   python tests/test_validators.py
   ```

**Git Checkpoint**: `git commit -m "Day 2.2: Data validation implemented"`

---

#### Checkpoint 2.3: Data Transformation ✅
**Time**: 1 hour

1. **Create Transformers**
   - File: `preprocessing/transformers.py`
   - Standardize formats
   - Calculate derived fields
   - Normalize geometries

2. **Test Transformations**
   ```bash
   python tests/test_transformers.py
   ```

**Git Checkpoint**: `git commit -m "Day 2.3: Data transformation pipeline ready"`

---

### Afternoon Session (4 hours)

#### Checkpoint 2.4: Text-to-SQL Converter ✅
**Time**: 2 hours

1. **Create SQL Templates**
   - File: `services/sql_templates.py`
   - Flood queries
   - Vegetation queries
   - Satellite queries

2. **Build Text-to-SQL Service**
   - File: `services/text_to_sql.py`
   - LLM-based SQL generation
   - Query validation
   - SQL sanitization

3. **Test SQL Generation**
   ```bash
   python tests/test_text_to_sql.py
   ```

**Git Checkpoint**: `git commit -m "Day 2.4: Text-to-SQL converter working"`

---

#### Checkpoint 2.5: Complete Pipeline Integration ✅
**Time**: 2 hours

1. **Create Pipeline Orchestrator**
   - File: `preprocessing/pipeline.py`
   - Extract → Validate → Transform → Load

2. **Test End-to-End Pipeline**
   ```bash
   python scripts/test_pipeline.py
   ```

3. **Run Full Pipeline**
   ```bash
   python scripts/run_pipeline.py --source all --days 30
   ```

**Git Checkpoint**: `git commit -m "Day 2.5: Complete pipeline integrated - DAY 2 COMPLETE"`

**Day 2 Deliverable**: ✅ Automated data pipeline + Text-to-SQL working

---

## 📅 Day 3: API Integration & Testing

### Morning Session (4 hours)

#### Checkpoint 3.1: Database Connection Layer ✅
**Time**: 1 hour

1. **Create Database Manager**
   - File: `database/manager.py`
   - Connection pooling
   - Query execution
   - Transaction management

2. **Test Database Operations**
   ```bash
   python tests/test_database_manager.py
   ```

**Git Checkpoint**: `git commit -m "Day 3.1: Database manager implemented"`

---

#### Checkpoint 3.2: Update API Endpoints ✅
**Time**: 2 hours

1. **Update Query Endpoint**
   - File: `main.py`
   - Integrate Text-to-SQL
   - Execute SQL queries
   - Format responses

2. **Add New Endpoints**
   - `/query/sql` - Direct SQL execution (admin)
   - `/data/stats` - Database statistics
   - `/data/sources` - Available data sources

3. **Test API**
   ```bash
   python tests/test_api_v2.py
   ```

**Git Checkpoint**: `git commit -m "Day 3.2: API endpoints updated"`

---

#### Checkpoint 3.3: End-to-End Testing ✅
**Time**: 1 hour

1. **Test Complete Flow**
   ```bash
   # Start server
   python main.py
   
   # Run test suite
   python tests/test_end_to_end.py
   ```

2. **Test Various Queries**
   - Flood queries
   - Vegetation queries
   - Satellite availability
   - Complex spatial queries

**Git Checkpoint**: `git commit -m "Day 3.3: End-to-end testing complete"`

---

### Afternoon Session (4 hours)

#### Checkpoint 3.4: Performance Optimization ✅
**Time**: 1.5 hours

1. **Add Query Caching**
   - File: `services/cache.py`
   - Redis or in-memory cache
   - Cache invalidation

2. **Optimize Database Queries**
   - Add missing indexes
   - Query plan analysis
   - Connection pooling

3. **Load Testing**
   ```bash
   python tests/load_test.py
   ```

**Git Checkpoint**: `git commit -m "Day 3.4: Performance optimized"`

---

#### Checkpoint 3.5: Documentation & Deployment ✅
**Time**: 2.5 hours

1. **Update Documentation**
   - API documentation
   - Database schema docs
   - Deployment guide
   - User guide

2. **Create Deployment Scripts**
   - Docker configuration
   - Environment setup
   - Database migrations

3. **Final Testing**
   ```bash
   python tests/test_all.py
   ```

4. **Deploy to Production**
   ```bash
   python scripts/deploy.py
   ```

**Git Checkpoint**: `git commit -m "Day 3.5: Documentation complete - DAY 3 COMPLETE"`

**Day 3 Deliverable**: ✅ Production-ready API with full documentation

---

## 🎯 Success Criteria

### Day 1 ✅
- [ ] PostgreSQL + PostGIS installed
- [ ] Database schema created
- [ ] 100+ records loaded
- [ ] Spatial queries working

### Day 2 ✅
- [ ] Data extraction working
- [ ] Validation rules implemented
- [ ] Text-to-SQL generating queries
- [ ] Pipeline runs end-to-end

### Day 3 ✅
- [ ] API integrated with database
- [ ] All endpoints working
- [ ] Performance optimized
- [ ] Documentation complete

---

## 📊 Daily Metrics

### Day 1 Metrics
- Database records: 100+
- Data sources connected: 2+
- Spatial queries tested: 10+

### Day 2 Metrics
- Pipeline success rate: >95%
- Text-to-SQL accuracy: >90%
- Data validation pass rate: >98%

### Day 3 Metrics
- API response time: <2s
- Query success rate: >95%
- Test coverage: >80%

---

## 🚨 Troubleshooting

### Common Issues

**PostgreSQL Connection Failed**
```bash
# Check if PostgreSQL is running
pg_isready -U postgres

# Restart PostgreSQL service
# Windows: Services → PostgreSQL → Restart
```

**PostGIS Extension Error**
```bash
# Reinstall PostGIS
# Use Stack Builder or manual installation
```

**API Authentication Failed**
```bash
# Verify credentials in .env
# Test API access separately
python scripts/test_api_access.py
```

**Data Download Slow**
```bash
# Use smaller date ranges
# Download in parallel
# Check network connection
```

---

## 📝 Git Workflow

### Daily Commits
```bash
# Start of day
git checkout -b day-1-data-collection

# After each checkpoint
git add .
git commit -m "Checkpoint X.Y: Description"

# End of day
git push origin day-1-data-collection
# Create PR for review
```

### Branch Strategy
- `main` - Production code
- `day-1-data-collection` - Day 1 work
- `day-2-pipeline` - Day 2 work
- `day-3-integration` - Day 3 work

---

## 🎉 Final Deliverable

After 3 days, you will have:

✅ **Database**: PostgreSQL + PostGIS with real satellite data
✅ **Pipeline**: Automated data ingestion and processing
✅ **API**: Text-to-SQL powered REST API
✅ **Tests**: Comprehensive test suite
✅ **Docs**: Complete documentation
✅ **Deployment**: Production-ready system

**Ready to deploy and scale!** 🚀

---

*Let's start with Day 1, Checkpoint 1.1!*
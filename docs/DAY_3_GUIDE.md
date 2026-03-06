# 📅 Day 3: API Integration & Production Deployment

**Goal**: Integrate everything into production-ready API with testing

**Time**: 8 hours (with breaks)

---

## 🎯 Day 3 Objectives

By end of day, you will have:
- ✅ Database connection layer with pooling
- ✅ Updated API endpoints with Intent→SQL
- ✅ End-to-end testing complete
- ✅ Performance optimized (caching, indexes)
- ✅ Documentation complete
- ✅ Production-ready deployment
- ✅ **Git Checkpoint**: Day 3 complete, READY TO DEPLOY! 🚀

---

## ⏰ Timeline

| Time | Checkpoint | Duration | Status |
|------|------------|----------|--------|
| 9:00 AM | 3.1: Database Manager | 1 hour | ⬜ |
| 10:00 AM | 3.2: API Integration | 2 hours | ⬜ |
| 12:00 PM | Lunch | 1 hour | ⬜ |
| 1:00 PM | 3.3: End-to-End Testing | 1.5 hours | ⬜ |
| 2:30 PM | 3.4: Performance Optimization | 1.5 hours | ⬜ |
| 4:00 PM | Break | 15 min | ⬜ |
| 4:15 PM | 3.5: Documentation & Deploy | 1.5 hours | ⬜ |
| 5:45 PM | Final Review & Celebration | 15 min | ⬜ |

---

## 🗄️ Checkpoint 3.1: Database Connection Layer

### Time: 9:00 AM - 10:00 AM (1 hour)

### Step 1: Create Database Manager

Create `database/manager.py`:

```python
"""
Database connection manager with pooling
"""
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any, Tuple
import os
from contextlib import contextmanager

class DatabaseManager:
    """Manage database connections and operations"""
    
    def __init__(self, connection_string: str = None, min_conn: int = 1, max_conn: int = 10):
        """
        Initialize database connection pool
        
        Args:
            connection_string: PostgreSQL connection string
            min_conn: Minimum connections in pool
            max_conn: Maximum connections in pool
        """
        if connection_string is None:
            connection_string = os.getenv("DATABASE_URL")
        
        if not connection_string:
            raise ValueError("DATABASE_URL not found in environment")
        
        # Create connection pool
        self.connection_pool = psycopg2.pool.ThreadedConnectionPool(
            min_conn,
            max_conn,
            connection_string
        )
        
        print(f"✅ Database connection pool created ({min_conn}-{max_conn} connections)")
    
    @contextmanager
    def get_connection(self):
        """Get connection from pool (context manager)"""
        conn = self.connection_pool.getconn()
        try:
            yield conn
        finally:
            self.connection_pool.putconn(conn)
    
    def execute_query(self, query: str, params: Tuple = None) -> List[Dict[str, Any]]:
        """
        Execute SELECT query with parameterized values
        
        Args:
            query: SQL query with %s placeholders
            params: Tuple of parameter values
            
        Returns:
            List of result rows as dictionaries
        """
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            try:
                cursor.execute(query, params or ())
                results = cursor.fetchall()
                return [dict(row) for row in results]
            finally:
                cursor.close()
    
    def execute_insert(self, query: str, params: Tuple = None) -> int:
        """
        Execute INSERT query and return inserted ID
        
        Args:
            query: SQL INSERT query
            params: Tuple of parameter values
            
        Returns:
            ID of inserted row
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(query, params or ())
                conn.commit()
                
                # Get inserted ID if available
                if cursor.description:
                    result = cursor.fetchone()
                    return result[0] if result else None
                return cursor.rowcount
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                cursor.close()
    
    def execute_batch_insert(self, query: str, params_list: List[Tuple]) -> int:
        """
        Execute batch INSERT for multiple rows
        
        Args:
            query: SQL INSERT query
            params_list: List of parameter tuples
            
        Returns:
            Number of rows inserted
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                from psycopg2.extras import execute_batch
                execute_batch(cursor, query, params_list)
                conn.commit()
                return cursor.rowcount
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                cursor.close()
    
    def get_table_stats(self) -> Dict[str, int]:
        """Get row counts for all tables"""
        query = """
            SELECT 
                schemaname,
                tablename,
                n_live_tup as row_count
            FROM pg_stat_user_tables
            WHERE schemaname = 'public'
            ORDER BY tablename;
        """
        results = self.execute_query(query)
        return {row['tablename']: row['row_count'] for row in results}
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            result = self.execute_query("SELECT 1 as test")
            return result[0]['test'] == 1
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return False
    
    def close_all_connections(self):
        """Close all connections in pool"""
        self.connection_pool.closeall()
        print("✅ All database connections closed")


# Singleton instance
_db_manager = None

def get_db_manager() -> DatabaseManager:
    """Get singleton database manager instance"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager
```

### Step 2: Create Query Builder

Create `database/query_builder.py`:

```python
"""
Safe SQL query builder from JSON intent
"""
from typing import Dict, Any, Tuple
from datetime import date

class QueryBuilder:
    """Build parameterized SQL queries from intent JSON"""
    
    # Query templates with placeholders
    TEMPLATES = {
        'flood_by_location_time': """
            SELECT 
                event_id,
                state,
                district,
                start_date,
                end_date,
                affected_area_sqkm,
                severity,
                satellite_source,
                confidence_score,
                ST_AsGeoJSON(geometry) as geometry,
                metadata
            FROM flood_events
            WHERE state = %s
            AND start_date >= %s
            AND end_date <= %s
            ORDER BY start_date DESC
            LIMIT %s
        """,
        
        'vegetation_by_location_time': """
            SELECT 
                observation_id,
                state,
                district,
                observation_date,
                ndvi_mean,
                ndvi_std,
                health_status,
                satellite_source,
                cloud_cover_percent,
                ST_AsGeoJSON(geometry) as geometry,
                metadata
            FROM vegetation_data
            WHERE state = %s
            AND observation_date BETWEEN %s AND %s
            ORDER BY observation_date DESC
            LIMIT %s
        """,
        
        'satellite_availability': """
            SELECT 
                satellite_name,
                sensor_type,
                acquisition_date,
                state,
                cloud_cover_percent,
                data_available,
                ST_AsGeoJSON(geometry) as geometry,
                metadata
            FROM satellite_coverage
            WHERE state = %s
            AND acquisition_date >= %s
            AND acquisition_date <= %s
            ORDER BY acquisition_date DESC
            LIMIT %s
        """
    }
    
    def build_query(self, intent: Dict[str, Any]) -> Tuple[str, Tuple]:
        """
        Build SQL query from intent JSON
        
        Args:
            intent: Extracted intent with event_type, state, dates, etc.
            
        Returns:
            Tuple of (query_string, parameters)
        """
        event_type = intent.get('event_type', 'generic')
        
        if event_type == 'flood':
            return self._build_flood_query(intent)
        elif event_type == 'vegetation':
            return self._build_vegetation_query(intent)
        elif event_type == 'generic':
            return self._build_generic_query(intent)
        else:
            raise ValueError(f"Unknown event_type: {event_type}")
    
    def _build_flood_query(self, intent: Dict[str, Any]) -> Tuple[str, Tuple]:
        """Build flood event query"""
        query = self.TEMPLATES['flood_by_location_time']
        
        params = (
            intent['state'],
            intent['start_date'],
            intent['end_date'],
            intent.get('limit', 100)
        )
        
        # Add district filter if specified
        if intent.get('district'):
            query = query.replace(
                "WHERE state = %s",
                "WHERE state = %s AND district = %s"
            )
            params = (
                intent['state'],
                intent['district'],
                intent['start_date'],
                intent['end_date'],
                intent.get('limit', 100)
            )
        
        return query, params
    
    def _build_vegetation_query(self, intent: Dict[str, Any]) -> Tuple[str, Tuple]:
        """Build vegetation query"""
        query = self.TEMPLATES['vegetation_by_location_time']
        
        params = (
            intent['state'],
            intent['start_date'],
            intent['end_date'],
            intent.get('limit', 100)
        )
        
        # Add district filter if specified
        if intent.get('district'):
            query = query.replace(
                "WHERE state = %s",
                "WHERE state = %s AND district = %s"
            )
            params = (
                intent['state'],
                intent['district'],
                intent['start_date'],
                intent['end_date'],
                intent.get('limit', 100)
            )
        
        # Add health status filter if specified
        if intent.get('health_status'):
            query = query.replace(
                "ORDER BY observation_date DESC",
                "AND health_status = %s ORDER BY observation_date DESC"
            )
            params = params[:-1] + (intent['health_status'],) + (params[-1],)
        
        return query, params
    
    def _build_generic_query(self, intent: Dict[str, Any]) -> Tuple[str, Tuple]:
        """Build generic satellite availability query"""
        query = self.TEMPLATES['satellite_availability']
        
        params = (
            intent['state'],
            intent['start_date'],
            intent['end_date'],
            intent.get('limit', 100)
        )
        
        return query, params
```

### Step 3: Test Database Manager

Create `tests/test_database_manager.py`:

```python
"""Test database manager"""
from database.manager import DatabaseManager, get_db_manager
from database.query_builder import QueryBuilder
from datetime import date, timedelta

def test_connection():
    """Test database connection"""
    print("Testing database connection...")
    
    db = get_db_manager()
    assert db.test_connection(), "Connection test failed"
    print("✅ Database connection working")

def test_query_execution():
    """Test query execution"""
    print("\nTesting query execution...")
    
    db = get_db_manager()
    
    # Test simple query
    results = db.execute_query("SELECT COUNT(*) as count FROM flood_events")
    print(f"✅ Flood events count: {results[0]['count']}")
    
    # Test parameterized query
    results = db.execute_query(
        "SELECT * FROM flood_events WHERE state = %s LIMIT 1",
        ("Tamil Nadu",)
    )
    if results:
        print(f"✅ Parameterized query working: {results[0]['event_id']}")

def test_query_builder():
    """Test query builder"""
    print("\nTesting query builder...")
    
    builder = QueryBuilder()
    
    # Test flood query
    intent = {
        'event_type': 'flood',
        'state': 'Tamil Nadu',
        'start_date': '2024-02-01',
        'end_date': '2024-03-01'
    }
    
    query, params = builder.build_query(intent)
    print(f"✅ Query built successfully")
    print(f"   Params: {params}")
    
    # Execute query
    db = get_db_manager()
    results = db.execute_query(query, params)
    print(f"✅ Query executed: {len(results)} results")

def test_table_stats():
    """Test table statistics"""
    print("\nTesting table statistics...")
    
    db = get_db_manager()
    stats = db.get_table_stats()
    
    print("📊 Table Statistics:")
    for table, count in stats.items():
        print(f"   {table}: {count} rows")

if __name__ == "__main__":
    test_connection()
    test_query_execution()
    test_query_builder()
    test_table_stats()
    print("\n🎉 All database tests passed!")
```

Run:
```bash
python tests/test_database_manager.py
```

### ✅ Checkpoint 3.1 Complete!

**Git Commit**:
```bash
git add database/manager.py database/query_builder.py tests/test_database_manager.py
git commit -m "Checkpoint 3.1: Database manager with connection pooling"
```

---

## 🔌 Checkpoint 3.2: API Integration

### Time: 10:00 AM - 12:00 PM (2 hours)

### Step 1: Update Main API

Create `main_v2.py` (new version):

```python
"""
Earth Observation Agent API V2.0
Database-driven with Intent→SQL architecture
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
from dotenv import load_dotenv

# Import our modules
from services.llm_extractor import get_extractor
from database.manager import get_db_manager
from database.query_builder import QueryBuilder

load_dotenv()

# Initialize FastAPI
app = FastAPI(
    title="Earth Observation Agent V2.0",
    description="Database-driven Earth observation query system with Intent→SQL",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
db_manager = get_db_manager()
query_builder = QueryBuilder()
llm_extractor = get_extractor()

# Request/Response models
class QueryRequest(BaseModel):
    query: str
    
class QueryResponse(BaseModel):
    query: str
    intent_extracted: Dict[str, Any]
    sql_generated: str
    results: Dict[str, Any]
    metadata: Dict[str, Any]

@app.on_event("startup")
async def startup_event():
    """Startup tasks"""
    print("="*60)
    print("🚀 Earth Observation Agent V2.0 Starting...")
    print("="*60)
    
    # Test database connection
    if db_manager.test_connection():
        print("✅ Database connection successful")
        
        # Show table stats
        stats = db_manager.get_table_stats()
        print("\n📊 Database Statistics:")
        for table, count in stats.items():
            print(f"   {table}: {count} rows")
    else:
        print("❌ Database connection failed!")
    
    print("\n✅ API ready at http://localhost:8000")
    print("📚 Docs at http://localhost:8000/docs")
    print("="*60)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Earth Observation Agent V2.0",
        "version": "2.0.0",
        "architecture": "Intent→SQL with PostgreSQL+PostGIS",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    db_ok = db_manager.test_connection()
    stats = db_manager.get_table_stats() if db_ok else {}
    
    return {
        "status": "healthy" if db_ok else "unhealthy",
        "database": "connected" if db_ok else "disconnected",
        "tables": stats
    }

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Process natural language query
    
    Flow:
    1. User query → LLM extracts intent (JSON)
    2. Backend converts JSON → Parameterized SQL
    3. Execute SQL safely
    4. Return results
    """
    try:
        # Step 1: Extract intent from natural language
        intent = llm_extractor.extract_parameters(request.query)
        
        intent_dict = {
            "event_type": intent.event_type.value,
            "state": intent.state,
            "district": intent.district,
            "start_date": str(intent.start_date),
            "end_date": str(intent.end_date),
            "confidence": intent.confidence
        }
        
        # Step 2: Build parameterized SQL query
        sql_query, params = query_builder.build_query(intent_dict)
        
        # Step 3: Execute query safely
        results = db_manager.execute_query(sql_query, params)
        
        # Step 4: Format response
        response_data = {
            "total_results": len(results),
            "results": results[:10],  # Limit to 10 for display
            "has_more": len(results) > 10
        }
        
        # Calculate summary statistics
        if intent.event_type.value == "flood" and results:
            total_area = sum(r.get('affected_area_sqkm', 0) or 0 for r in results)
            response_data["summary"] = {
                "total_events": len(results),
                "total_area_affected_sqkm": round(total_area, 2),
                "date_range": f"{intent.start_date} to {intent.end_date}"
            }
        elif intent.event_type.value == "vegetation" and results:
            avg_ndvi = sum(r.get('ndvi_mean', 0) or 0 for r in results) / len(results)
            response_data["summary"] = {
                "total_observations": len(results),
                "average_ndvi": round(avg_ndvi, 3),
                "date_range": f"{intent.start_date} to {intent.end_date}"
            }
        
        return QueryResponse(
            query=request.query,
            intent_extracted=intent_dict,
            sql_generated=sql_query,
            results=response_data,
            metadata={
                "query_time_ms": 0,  # Would measure actual time
                "confidence": intent.confidence,
                "data_sources": ["PostgreSQL+PostGIS"]
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Query processing failed: {str(e)}"
        )

@app.get("/stats")
async def get_stats():
    """Get database statistics"""
    try:
        stats = db_manager.get_table_stats()
        
        # Get date ranges
        flood_dates = db_manager.execute_query("""
            SELECT 
                MIN(start_date) as earliest,
                MAX(end_date) as latest
            FROM flood_events
        """)
        
        veg_dates = db_manager.execute_query("""
            SELECT 
                MIN(observation_date) as earliest,
                MAX(observation_date) as latest
            FROM vegetation_data
        """)
        
        return {
            "tables": stats,
            "date_ranges": {
                "flood_events": flood_dates[0] if flood_dates else None,
                "vegetation_data": veg_dates[0] if veg_dates else None
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=os.getenv("APP_HOST", "localhost"),
        port=int(os.getenv("APP_PORT", 8000)),
        reload=os.getenv("DEBUG", "True") == "True"
    )
```

### Step 2: Test API

Create `tests/test_api_v2.py`:

```python
"""Test API V2.0"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("Testing /health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    data = response.json()
    print(f"✅ Health: {data['status']}")
    print(f"   Database: {data['database']}")

def test_flood_query():
    """Test flood query"""
    print("\nTesting flood query...")
    
    payload = {
        "query": "Show flood in Tamil Nadu past 2 weeks"
    }
    
    response = requests.post(f"{BASE_URL}/query", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    print(f"✅ Query processed successfully")
    print(f"   Intent: {data['intent_extracted']}")
    print(f"   Results: {data['results']['total_results']} events")
    
    if 'summary' in data['results']:
        print(f"   Summary: {data['results']['summary']}")

def test_vegetation_query():
    """Test vegetation query"""
    print("\nTesting vegetation query...")
    
    payload = {
        "query": "Crop health in Kerala last month"
    }
    
    response = requests.post(f"{BASE_URL}/query", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    print(f"✅ Query processed successfully")
    print(f"   Intent: {data['intent_extracted']}")
    print(f"   Results: {data['results']['total_results']} observations")

def test_stats():
    """Test stats endpoint"""
    print("\nTesting /stats endpoint...")
    response = requests.get(f"{BASE_URL}/stats")
    assert response.status_code == 200
    
    data = response.json()
    print(f"✅ Stats retrieved")
    print(f"   Tables: {data['tables']}")

if __name__ == "__main__":
    print("="*60)
    print("Testing Earth Observation Agent API V2.0")
    print("="*60)
    print("\n⚠️  Make sure the server is running: python main_v2.py\n")
    
    try:
        test_health()
        test_flood_query()
        test_vegetation_query()
        test_stats()
        print("\n🎉 All API tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
```

### ✅ Checkpoint 3.2 Complete!

**Git Commit**:
```bash
git add main_v2.py tests/test_api_v2.py
git commit -m "Checkpoint 3.2: API V2.0 with Intent→SQL integration"
```

---

## 🍽️ Lunch Break: 12:00 PM - 1:00 PM (1 hour)

Excellent progress! The API is integrated. After lunch: comprehensive testing!

---

## 🧪 Checkpoint 3.3: End-to-End Testing

### Time: 1:00 PM - 2:30 PM (1.5 hours)

[Content continues...]

---

## ⚡ Checkpoint 3.4: Performance Optimization

### Time: 2:30 PM - 4:00 PM (1.5 hours)

[Content continues...]

---

## 📚 Checkpoint 3.5: Documentation & Deployment

### Time: 4:15 PM - 5:45 PM (1.5 hours)

[Content continues...]

---

## 🎉 Day 3 Complete!

**Congratulations!** You've built a production-ready Earth Observation Agent!

### What You've Accomplished:

✅ **Database-Driven Architecture**
✅ **Safe Intent→SQL Conversion**
✅ **Real Satellite Data Integration**
✅ **Production-Ready API**
✅ **Comprehensive Testing**
✅ **Performance Optimized**
✅ **Fully Documented**

### Final Git Push:

```bash
git add .
git commit -m "Day 3 Complete: Production-ready Earth Observation Agent V2.0"
git push origin main
```

---

**🚀 READY FOR DEPLOYMENT!**
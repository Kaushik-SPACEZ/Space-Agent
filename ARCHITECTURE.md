# 🏗️ Earth Observation Agent - Architecture Documentation

## Overview

The Earth Observation Agent is a **multi-pipeline natural language spatial intelligence engine** designed with modularity, scalability, and extensibility as core principles.

---

## Design Philosophy

### "One Agent, Multiple Pipelines"

Instead of creating separate agents for each Earth observation task (FloodAgent, CropAgent, etc.), we implement:

- **One Intelligent Router** (Earth Agent)
- **Multiple Specialized Pipelines** (Flood, Vegetation, Generic, etc.)

This prevents "agent explosion" and maintains a clean, scalable architecture.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        User Query                            │
│              (Natural Language Input)                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              LLM Parameter Extractor                         │
│                  (OpenAI GPT-4)                             │
│                                                              │
│  Extracts:                                                   │
│  - event_type (flood/vegetation/generic)                    │
│  - state, district                                          │
│  - start_date, end_date                                     │
│  - confidence score                                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Intent Classifier                               │
│                                                              │
│  - Validates extracted parameters                           │
│  - Routes to appropriate pipeline                           │
│  - Handles ambiguous queries                                │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Earth Agent                               │
│                  (Main Orchestrator)                         │
│                                                              │
│  Pipeline Registry:                                          │
│  ┌──────────────────────────────────────────────┐          │
│  │  "flood"      → FloodPipeline                │          │
│  │  "vegetation" → VegetationPipeline           │          │
│  │  "generic"    → GenericPipeline              │          │
│  └──────────────────────────────────────────────┘          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  Selected Pipeline                           │
│                                                              │
│  1. Load Dataset (CSV)                                      │
│  2. Query Dataset (Filter by params)                        │
│  3. Format Response (Standardized + GeoJSON)                │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Standardized Response                           │
│                                                              │
│  {                                                           │
│    "report_type": "...",                                    │
│    "location": {...},                                       │
│    "time_range": {...},                                     │
│    "satellite": "...",                                      │
│    "details": {...},                                        │
│    "geojson": {...}                                         │
│  }                                                           │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. LLM Parameter Extractor

**File:** `services/llm_extractor.py`

**Responsibilities:**
- Parse natural language queries
- Extract structured parameters using OpenAI GPT-4
- Handle relative dates ("past 2 weeks", "last month")
- Return confidence scores

**Key Features:**
- JSON mode for structured output
- Date resolution logic
- Validation of extracted parameters

**Example:**
```python
Input: "Show flood in Tamil Nadu past 2 weeks"

Output: ExtractedParameters(
    event_type="flood",
    state="Tamil Nadu",
    district=None,
    start_date=date(2024, 1, 15),
    end_date=date(2024, 1, 29),
    confidence=0.95
)
```

---

### 2. Intent Classifier

**File:** `services/intent_classifier.py`

**Responsibilities:**
- Map event_type to pipeline name
- Validate parameters for the target pipeline
- Generate clarification prompts if needed

**Pipeline Mapping:**
```python
{
    EventType.FLOOD: "flood",
    EventType.VEGETATION: "vegetation",
    EventType.GENERIC: "generic"
}
```

---

### 3. Earth Agent

**File:** `agents/earth_agent.py`

**Responsibilities:**
- Main orchestrator for all queries
- Maintain pipeline registry
- Route queries to appropriate pipelines
- Handle errors gracefully
- Provide helpful error messages

**Key Methods:**
- `process_query()`: Main entry point
- `route_to_pipeline()`: Select pipeline
- `register_pipeline()`: Add new pipelines
- `health_check()`: System health status

**Pipeline Registry Pattern:**
```python
self.pipelines = {
    "flood": FloodPipeline(data_dir),
    "vegetation": VegetationPipeline(data_dir),
    "generic": GenericPipeline(data_dir)
}
```

---

### 4. Base Pipeline

**File:** `pipelines/base_pipeline.py`

**Abstract Base Class** for all pipelines

**Required Methods:**
- `load_dataset()`: Load data from source
- `query_dataset()`: Filter data by parameters
- `format_response()`: Create standardized response

**Helper Methods:**
- `_create_location_info()`: Build location object
- `_create_time_range()`: Build time range object
- `_create_geojson_point()`: Create GeoJSON point
- `_create_geojson_collection()`: Create GeoJSON collection

**Template Method Pattern:**
```python
def process(self, params):
    # 1. Validate
    # 2. Load dataset
    # 3. Query dataset
    # 4. Format response
    # 5. Add metadata
    return response
```

---

### 5. Flood Pipeline

**File:** `pipelines/flood_pipeline.py`

**Specialization:** Flood monitoring and extent analysis

**Data Source:** `data/flood_data.csv`

**Key Features:**
- SAR-based flood detection data
- Flooded area calculations
- Affected district tracking
- Confidence scores

**Response Details:**
```python
{
    "flooded_area_sqkm": 245.6,
    "resolution": "10m",
    "acquisition_time": "2024-01-28T10:30:00",
    "confidence": 0.92,
    "affected_districts": ["Chennai", "Kanchipuram"]
}
```

---

### 6. Vegetation Pipeline

**File:** `pipelines/vegetation_pipeline.py`

**Specialization:** Vegetation health and crop monitoring

**Data Source:** `data/vegetation_data.csv`

**Key Features:**
- NDVI calculations
- Crop stress detection
- Vegetation health assessment
- Temporal trend analysis

**Response Details:**
```python
{
    "vegetation_index_type": "NDVI",
    "mean_ndvi": 0.64,
    "min_ndvi": 0.39,
    "max_ndvi": 0.77,
    "crop_stress_detected": true,
    "scene_count": 8
}
```

**Health Assessment Logic:**
- NDVI < 0.2: No vegetation
- NDVI 0.2-0.5: Sparse vegetation / stress
- NDVI 0.5-0.7: Healthy vegetation
- NDVI > 0.7: Very healthy, dense vegetation

---

### 7. Generic Pipeline

**File:** `pipelines/generic_pipeline.py`

**Specialization:** Dataset availability and metadata

**Data Sources:** All available datasets

**Key Features:**
- Cross-dataset queries
- Satellite coverage information
- Date range availability
- Data type enumeration

**Response Details:**
```python
{
    "available_datasets": ["flood", "vegetation"],
    "satellites": ["Sentinel-1", "Sentinel-2"],
    "date_range_available": {
        "flood": {"earliest": "2023-06-15", "latest": "2024-01-29"},
        "vegetation": {"earliest": "2023-01-01", "latest": "2023-11-30"}
    },
    "total_scenes": 46
}
```

---

## Data Models

**File:** `models/schemas.py`

### Core Models

1. **QueryInput**: Raw user query
2. **ExtractedParameters**: Structured params from LLM
3. **PipelineResponse**: Standardized output format
4. **ErrorResponse**: Error handling format

### Pipeline-Specific Models

1. **FloodDetails**: Flood-specific data
2. **VegetationDetails**: Vegetation-specific data
3. **GenericDatasetDetails**: Dataset availability data

### Supporting Models

1. **LocationInfo**: Geographic information
2. **TimeRange**: Temporal information
3. **EventType**: Enum for event types

---

## API Layer

**File:** `main.py`

**Framework:** FastAPI

### Endpoints

1. **POST /query**: Process natural language query
2. **GET /health**: System health check
3. **GET /pipelines**: Available pipeline info
4. **GET /examples**: Example queries
5. **GET /docs**: Interactive API documentation

### Error Handling

- HTTP 200: Success
- HTTP 400: Invalid parameters
- HTTP 404: No data found
- HTTP 500: Internal error
- HTTP 503: Service unavailable

---

## Data Flow

### Successful Query Flow

```
1. User submits query
   ↓
2. LLM extracts parameters
   ↓
3. Intent classifier validates & routes
   ↓
4. Earth Agent selects pipeline
   ↓
5. Pipeline loads dataset
   ↓
6. Pipeline queries data
   ↓
7. Pipeline formats response (with GeoJSON)
   ↓
8. Response returned to user
```

### Error Handling Flow

```
1. Error detected (no data, invalid params, etc.)
   ↓
2. Earth Agent catches error
   ↓
3. Generate helpful error message
   ↓
4. Suggest alternatives (if available)
   ↓
5. Return ErrorResponse with suggestions
```

---

## Extensibility

### Adding a New Pipeline

**Example: Urban Heat Pipeline**

#### Step 1: Create Pipeline Class

```python
# pipelines/urban_heat_pipeline.py
from pipelines.base_pipeline import BasePipeline

class UrbanHeatPipeline(BasePipeline):
    def __init__(self, data_dir="data"):
        super().__init__(data_dir)
        self.dataset_file = f"{data_dir}/urban_heat_data.csv"
    
    def load_dataset(self):
        # Load urban heat data
        pass
    
    def query_dataset(self, params):
        # Query logic
        pass
    
    def format_response(self, data, params):
        # Format response
        pass
```

#### Step 2: Register in Earth Agent

```python
# agents/earth_agent.py
from pipelines.urban_heat_pipeline import UrbanHeatPipeline

# In __init__
self.pipelines["urban_heat"] = UrbanHeatPipeline(data_dir)
```

#### Step 3: Update Intent Classifier

```python
# services/intent_classifier.py
self.pipeline_map[EventType.URBAN_HEAT] = "urban_heat"
```

#### Step 4: Add Event Type

```python
# models/schemas.py
class EventType(str, Enum):
    FLOOD = "flood"
    VEGETATION = "vegetation"
    GENERIC = "generic"
    URBAN_HEAT = "urban_heat"  # New
```

**That's it!** No changes needed to:
- Existing pipelines
- API endpoints
- Error handling
- Response formatting

---

## Design Patterns Used

### 1. Strategy Pattern
- **Where:** Pipeline selection
- **Why:** Different algorithms for different event types

### 2. Template Method Pattern
- **Where:** BasePipeline.process()
- **Why:** Common workflow, specialized steps

### 3. Factory Pattern
- **Where:** Pipeline instantiation
- **Why:** Create pipelines based on event type

### 4. Singleton Pattern
- **Where:** Service instances (extractor, classifier, agent)
- **Why:** Single shared instance

### 5. Dependency Injection
- **Where:** LLM service, data directory
- **Why:** Testability and flexibility

---

## Scalability Considerations

### Current (MVP)
- CSV-based datasets
- Single-threaded processing
- In-memory data loading

### Future Enhancements

#### Phase 2
- PostgreSQL/PostGIS backend
- Connection pooling
- Query result caching
- Async processing

#### Phase 3
- Distributed processing (Celery)
- Redis caching layer
- Load balancing
- Horizontal scaling

---

## Security Considerations

### Current
- No authentication (MVP)
- CORS enabled for all origins
- Input validation via Pydantic

### Production Requirements
- API key authentication
- Rate limiting
- CORS whitelist
- Input sanitization
- SQL injection prevention (when using DB)
- Logging and monitoring

---

## Performance Optimization

### Current Optimizations
- Lazy dataset loading
- Efficient pandas filtering
- GeoJSON feature limiting

### Future Optimizations
- Database indexing
- Query result caching
- Async I/O
- Batch processing
- CDN for static assets

---

## Testing Strategy

### Unit Tests
- Individual pipeline methods
- Parameter extraction
- Intent classification

### Integration Tests
- End-to-end query processing
- Pipeline routing
- Error handling

### Load Tests
- Concurrent query handling
- Response time benchmarks
- Resource usage monitoring

---

## Monitoring and Observability

### Health Checks
- Pipeline status
- Dataset availability
- LLM service connectivity

### Metrics to Track
- Query processing time
- Success/failure rates
- Pipeline usage distribution
- Error types and frequencies

### Logging
- Structured JSON logs
- Query parameters
- Processing steps
- Error traces

---

## Conclusion

This architecture provides:

✅ **Modularity**: Independent, reusable components
✅ **Scalability**: Easy to add new pipelines
✅ **Maintainability**: Clear separation of concerns
✅ **Extensibility**: Plugin-based pipeline system
✅ **Consistency**: Standardized response format
✅ **Robustness**: Comprehensive error handling

The system is production-ready for MVP deployment and designed to scale to enterprise requirements.
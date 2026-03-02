# 🌍 Earth Observation Agent

**Multi-Pipeline Natural Language Spatial Intelligence Engine**

A modular, scalable AI-powered system for processing Earth observation queries through natural language. The system intelligently routes queries to specialized pipelines for flood monitoring, vegetation analysis, and generic dataset queries.

---

## 🎯 Features

- **Natural Language Processing**: Query Earth observation data using plain English
- **Multi-Pipeline Architecture**: Specialized pipelines for different Earth observation tasks
- **GeoJSON Support**: Spatial data returned in standard GeoJSON format
- **Relative Date Support**: Use expressions like "past 2 weeks", "last month"
- **Indian State Focus**: Optimized for Indian geographic regions
- **RESTful API**: FastAPI-based API with automatic documentation
- **Extensible Design**: Easy to add new pipelines without modifying existing code

---

## 🏗️ Architecture

```
User Query (Natural Language)
    ↓
LLM Parameter Extractor (OpenAI GPT-4)
    ↓
Intent Classifier
    ↓
Earth Agent (Router)
    ↓
┌─────────────────────────────────────┐
│  Flood Pipeline                     │
│  Vegetation Pipeline                │
│  Generic Dataset Pipeline           │
└─────────────────────────────────────┘
    ↓
Structured Dataset Query (CSV)
    ↓
Response Generator (with GeoJSON)
    ↓
Standardized JSON Output
```

---

## 📦 Installation

### Prerequisites

- Python 3.10 or higher
- OpenAI API key

### Setup

1. **Clone the repository**
```bash
cd earth_agent_project
```

2. **Create virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
# Copy example env file
copy .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=your_api_key_here
```

---

## 🚀 Quick Start

### Start the API Server

```bash
python main.py
```

The API will be available at: `http://localhost:8000`

### Interactive API Documentation

Visit: `http://localhost:8000/docs`

---

## 📝 Usage Examples

### Example 1: Flood Query

**Query:**
```json
POST /query
{
  "query": "Show flood in Tamil Nadu past 2 weeks"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "report_type": "flood_monitoring",
    "location": {
      "state": "Tamil Nadu",
      "district": "Chennai",
      "coordinates": {"lat": 13.0827, "lon": 80.2707}
    },
    "time_range": {
      "start": "2024-01-15",
      "end": "2024-01-29",
      "duration_days": 14
    },
    "satellite": "Sentinel-1",
    "details": {
      "flooded_area_sqkm": 245.6,
      "resolution": "10m",
      "acquisition_time": "2024-01-28T10:30:00",
      "confidence": 0.92
    },
    "geojson": {
      "type": "FeatureCollection",
      "features": [...]
    }
  }
}
```

### Example 2: Vegetation Query

**Query:**
```json
POST /query
{
  "query": "Crop stress in Coimbatore during January 2023"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "report_type": "vegetation_monitoring",
    "location": {
      "state": "Tamil Nadu",
      "district": "Coimbatore"
    },
    "details": {
      "vegetation_index_type": "NDVI",
      "mean_ndvi": 0.64,
      "crop_stress_detected": true,
      "scene_count": 8
    }
  }
}
```

### Example 3: Generic Dataset Query

**Query:**
```json
POST /query
{
  "query": "Available EO datasets for Andhra Pradesh in October 2023"
}
```

---

## 🔌 API Endpoints

### POST `/query`
Process natural language Earth observation query

**Request Body:**
```json
{
  "query": "string"
}
```

**Response:** Standardized pipeline response with GeoJSON

---

### GET `/health`
Check system health status

**Response:**
```json
{
  "agent_status": "healthy",
  "timestamp": "2024-01-29T10:30:00",
  "pipelines": {
    "flood": {"status": "healthy"},
    "vegetation": {"status": "healthy"},
    "generic": {"status": "healthy"}
  }
}
```

---

### GET `/pipelines`
Get information about available pipelines

---

### GET `/examples`
Get example queries for each pipeline type

---

## 🧩 Supported Query Types

### Flood Monitoring
- "Show flood in [state] past [time period]"
- "Flood extent in [district] after [event]"
- "Flooding in [location] during [date range]"

### Vegetation/Crop Monitoring
- "Crop stress in [location] during [time period]"
- "NDVI values for [location] [time period]"
- "Vegetation data in [state] in [year]"
- "Crop health in [location] past [time period]"

### Generic Dataset Queries
- "Available EO datasets for [location] in [time period]"
- "Satellite coverage for [state]"
- "What data is available for [location]?"

---

## 📊 Data Sources

The MVP uses pre-processed CSV datasets:

- **flood_data.csv**: Flood extent data from Sentinel-1 SAR
- **vegetation_data.csv**: NDVI data from Sentinel-2 optical imagery

### Dataset Fields

**Flood Data:**
- state, district, start_date, end_date
- flooded_area_sqkm, satellite, resolution
- acquisition_time, confidence
- latitude, longitude

**Vegetation Data:**
- state, district, start_date, end_date
- mean_ndvi, min_ndvi, max_ndvi
- satellite, resolution, scene_count
- crop_stress_detected
- latitude, longitude

---

## 🔧 Configuration

### Environment Variables

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4-turbo-preview

# Application Configuration
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=True

# Data Configuration
DATA_DIR=data
```

---

## 🧪 Testing

### Manual Testing with cURL

```bash
# Test flood query
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Show flood in Tamil Nadu past 2 weeks"}'

# Test vegetation query
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Crop stress in Punjab last month"}'

# Health check
curl "http://localhost:8000/health"
```

### Using Python

```python
import requests

# Query the API
response = requests.post(
    "http://localhost:8000/query",
    json={"query": "Show flood in Kerala past month"}
)

result = response.json()
print(result)
```

---

## 🚀 Adding New Pipelines

The architecture is designed for easy extensibility. To add a new pipeline:

### 1. Create Pipeline Class

```python
# pipelines/urban_heat_pipeline.py
from pipelines.base_pipeline import BasePipeline

class UrbanHeatPipeline(BasePipeline):
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

### 2. Register Pipeline

```python
# In agents/earth_agent.py
from pipelines.urban_heat_pipeline import UrbanHeatPipeline

# Add to __init__
self.pipelines["urban_heat"] = UrbanHeatPipeline(data_dir)
```

### 3. Update Intent Classifier

```python
# In services/intent_classifier.py
self.pipeline_map[EventType.URBAN_HEAT] = "urban_heat"
```

That's it! No changes needed to existing pipelines or API endpoints.

---

## 📈 Future Enhancements

### Phase 2 (Planned)
- [ ] PostgreSQL/PostGIS backend
- [ ] Real-time satellite API integration (Sentinel Hub, Google Earth Engine)
- [ ] ML models for image processing
- [ ] Drought monitoring pipeline
- [ ] Air quality pipeline
- [ ] Urban heat island pipeline

### Phase 3 (Future)
- [ ] Web-based map visualization
- [ ] User authentication and API keys
- [ ] Query history and caching
- [ ] Batch processing support
- [ ] WebSocket support for real-time updates

---

## 🏛️ Project Structure

```
earth_agent_project/
│
├── main.py                 # FastAPI application
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── README.md              # This file
│
├── agents/
│   └── earth_agent.py     # Main orchestrator
│
├── pipelines/
│   ├── base_pipeline.py   # Abstract base class
│   ├── flood_pipeline.py  # Flood monitoring
│   ├── vegetation_pipeline.py  # Vegetation/crop monitoring
│   └── generic_pipeline.py     # Generic dataset queries
│
├── services/
│   ├── llm_extractor.py   # LLM parameter extraction
│   └── intent_classifier.py    # Intent classification
│
├── models/
│   └── schemas.py         # Pydantic data models
│
└── data/
    ├── flood_data.csv     # Flood dataset
    └── vegetation_data.csv # Vegetation dataset
```

---

## 🤝 Contributing

This is an MVP project. Contributions are welcome!

### Areas for Contribution
- Additional pipelines (drought, air quality, etc.)
- ML model integration
- Database backend
- Visualization tools
- Documentation improvements

---

## 📄 License

MIT License - Feel free to use and modify

---

## 🙏 Acknowledgments

- **Sentinel-1 & Sentinel-2**: ESA Copernicus Programme
- **OpenAI**: GPT-4 for natural language processing
- **FastAPI**: Modern Python web framework

---

## 📞 Support

For issues and questions:
- Check `/docs` endpoint for API documentation
- Review example queries in `/examples` endpoint
- Ensure OpenAI API key is configured correctly

---

## 🎯 Design Philosophy

> "One Agent, Multiple Pipelines"

This architecture prevents agent explosion by using a single intelligent router (Earth Agent) that delegates to specialized processing pipelines. This approach:

- ✅ Scales easily (add pipelines, not agents)
- ✅ Maintains consistency (standardized response format)
- ✅ Simplifies maintenance (modular design)
- ✅ Enables reuse (shared base classes and utilities)

---

**Built with ❤️ for Earth Observation Intelligence**
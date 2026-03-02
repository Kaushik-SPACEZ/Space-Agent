# 🚀 Quick Start Guide - Earth Observation Agent

Get up and running in 5 minutes!

---

## Prerequisites

- Python 3.10 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

---

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy the example environment file
copy .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-key-here
```

### 3. Verify Setup

```bash
python setup.py
```

You should see:
```
✅ SETUP COMPLETE!
```

---

## Start the Server

```bash
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

---

## Test the API

### Option 1: Web Browser

Visit: **http://localhost:8000/docs**

This opens the interactive API documentation where you can test queries directly.

### Option 2: cURL

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"Show flood in Tamil Nadu past 2 weeks\"}"
```

### Option 3: Python Script

```python
import requests

response = requests.post(
    "http://localhost:8000/query",
    json={"query": "Show flood in Tamil Nadu past 2 weeks"}
)

print(response.json())
```

### Option 4: Test Suite

```bash
python test_queries.py
```

---

## Example Queries

### Flood Monitoring

```
"Show flood in Tamil Nadu past 2 weeks"
"Flood extent in Chennai after cyclone"
"Flooding in Kerala during August 2023"
```

### Vegetation Monitoring

```
"Crop stress in Coimbatore during January 2023"
"NDVI values for Punjab rice fields last month"
"Vegetation data in Kerala in 2022"
```

### Dataset Availability

```
"Available EO datasets for Andhra Pradesh in October 2023"
"What satellite data is available for Karnataka?"
"Show me all datasets for Gujarat in 2023"
```

---

## Understanding the Response

### Successful Response

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
    },
    "metadata": {
      "processing_time_ms": 234,
      "pipeline": "flood",
      "records_found": 1
    }
  }
}
```

### Error Response

```json
{
  "success": false,
  "error": {
    "error": "No data found for XYZ State between 2024-01-15 and 2024-01-29",
    "error_type": "no_data_found",
    "suggestion": "Try querying data for one of these available date ranges",
    "available_options": [
      "2023-06-15 to 2023-06-30",
      "2023-12-01 to 2023-12-15"
    ]
  }
}
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/query` | POST | Process natural language query |
| `/health` | GET | System health check |
| `/pipelines` | GET | Available pipeline info |
| `/examples` | GET | Example queries |
| `/docs` | GET | Interactive API docs |

---

## Supported Indian States

The system currently has data for:

- Tamil Nadu
- Kerala
- Karnataka
- Andhra Pradesh
- Maharashtra
- Gujarat
- West Bengal
- Odisha
- Bihar
- Uttar Pradesh
- Rajasthan
- Punjab
- Haryana
- Telangana
- Madhya Pradesh

---

## Troubleshooting

### Issue: "OpenAI API key not found"

**Solution:** Make sure you've created `.env` file and added your API key:
```bash
OPENAI_API_KEY=sk-your-key-here
```

### Issue: "No module named 'fastapi'"

**Solution:** Install dependencies:
```bash
pip install -r requirements.txt
```

### Issue: "Port 8000 already in use"

**Solution:** Change port in `.env`:
```bash
APP_PORT=8001
```

### Issue: "No data found"

**Solution:** Check available date ranges:
```bash
curl "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"Available datasets for Tamil Nadu\"}"
```

---

## Next Steps

1. **Explore the API**: Visit http://localhost:8000/docs
2. **Read the Architecture**: See `ARCHITECTURE.md`
3. **Run Tests**: Execute `python test_queries.py`
4. **Add Custom Data**: Add your own CSV files to `data/` directory
5. **Create New Pipeline**: Follow the guide in `ARCHITECTURE.md`

---

## Support

- **API Documentation**: http://localhost:8000/docs
- **Example Queries**: http://localhost:8000/examples
- **Health Check**: http://localhost:8000/health

---

## What's Next?

### Immediate
- Test with your own queries
- Explore the GeoJSON responses
- Check the interactive documentation

### Short Term
- Add more data to CSV files
- Customize for your region
- Integrate with your applications

### Long Term
- Add new pipelines (drought, air quality, etc.)
- Connect to real satellite APIs
- Build visualization dashboard

---

**Happy Querying! 🌍🛰️**
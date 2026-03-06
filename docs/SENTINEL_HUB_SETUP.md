# Sentinel Hub Catalog API Setup Guide

This guide explains how to set up and use the Sentinel Hub Catalog API integration for accessing satellite data.

## Overview

The Sentinel Hub Catalog API provides access to:
- **Sentinel-1**: SAR (Synthetic Aperture Radar) data - works through clouds
- **Sentinel-2**: Optical multispectral data - high resolution imagery
- **Sentinel-3**: Ocean and land monitoring data
- **Landsat**: Long-term Earth observation data
- **MODIS**: Daily global coverage data

The API implements the **STAC (SpatioTemporal Asset Catalog)** specification, which is the standard for geospatial data discovery.

## Getting Started

### 1. Create a Sentinel Hub Account

1. Go to [https://www.sentinel-hub.com/](https://www.sentinel-hub.com/)
2. Click "Sign Up" and create a free account
3. Verify your email address

### 2. Create OAuth Credentials

1. Log in to your Sentinel Hub dashboard
2. Navigate to "User Settings" → "OAuth clients"
3. Click "Create new OAuth client"
4. Give it a name (e.g., "Earth Observation Agent")
5. Copy the **Client ID** and **Client Secret**

### 3. Configure Environment Variables

Add your credentials to the `.env` file:

```bash
SENTINEL_HUB_CLIENT_ID=your_client_id_here
SENTINEL_HUB_CLIENT_SECRET=your_client_secret_here
```

## Usage Examples

### Basic Authentication

```python
from services.sentinel_hub_api import sentinel_hub_api

# Authenticate (happens automatically on first use)
if sentinel_hub_api.authenticate():
    print("Authentication successful!")
```

### Search for Sentinel-2 Data

```python
# Search for optical imagery with low cloud cover
results = sentinel_hub_api.search_sentinel2(
    bbox=[77.0, 28.0, 78.0, 29.0],  # [west, south, east, north]
    start_date="2024-01-01",
    end_date="2024-01-31",
    max_cloud_cover=20.0,  # Maximum 20% cloud cover
    limit=10
)

# Process results
for feature in results.get("features", []):
    info = sentinel_hub_api.get_feature_info(feature)
    print(f"Scene: {info['id']}")
    print(f"Date: {info['datetime']}")
    print(f"Cloud cover: {info['cloud_cover']}%")
```

### Search for Sentinel-1 SAR Data

```python
# Search for radar data (works through clouds)
results = sentinel_hub_api.search_sentinel1(
    bbox=[85.0, 25.0, 88.0, 27.0],
    start_date="2024-01-01",
    end_date="2024-01-31",
    orbit_direction="DESCENDING",  # Optional: ASCENDING or DESCENDING
    limit=10
)
```

### Browse Available Collections

```python
# Get list of all available satellite data collections
collections = sentinel_hub_api.get_collections()

for collection in collections:
    print(f"{collection['id']}: {collection['title']}")
```

### Advanced STAC Query

```python
# Custom query with multiple filters
results = sentinel_hub_api.search_stac(
    bbox=[77.0, 28.0, 78.0, 29.0],
    datetime_range="2024-01-01/2024-12-31",
    collections=["sentinel-2-l2a"],
    limit=50,
    query={
        "eo:cloud_cover": {"lte": 10},  # Less than or equal to 10%
        "platform": {"eq": "sentinel-2b"}  # Specific satellite
    }
)
```

## Understanding STAC Results

STAC search results are returned as a FeatureCollection:

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "id": "S2A_MSIL2A_20240115T053131_N0510_R105_T43RGM_20240115T084537",
      "type": "Feature",
      "geometry": { ... },
      "bbox": [77.0, 28.0, 78.0, 29.0],
      "properties": {
        "datetime": "2024-01-15T05:31:31Z",
        "platform": "sentinel-2a",
        "instruments": ["msi"],
        "eo:cloud_cover": 5.2,
        ...
      },
      "assets": {
        "B01": { "href": "...", "type": "image/jp2" },
        "B02": { "href": "...", "type": "image/jp2" },
        ...
      }
    }
  ]
}
```

## Common Use Cases

### 1. Flood Monitoring

Use Sentinel-1 SAR data (works through clouds):

```python
results = sentinel_hub_api.search_sentinel1(
    bbox=[flood_region_bbox],
    start_date="2024-01-01",
    end_date="2024-01-31",
    limit=10
)
```

### 2. Vegetation Analysis

Use Sentinel-2 optical data with low cloud cover:

```python
results = sentinel_hub_api.search_sentinel2(
    bbox=[agricultural_region_bbox],
    start_date="2024-01-01",
    end_date="2024-12-31",
    max_cloud_cover=10.0,
    limit=20
)
```

### 3. Change Detection

Search for data before and after an event:

```python
# Before event
before = sentinel_hub_api.search_sentinel2(
    bbox=[area_bbox],
    start_date="2023-12-01",
    end_date="2023-12-31",
    max_cloud_cover=15.0
)

# After event
after = sentinel_hub_api.search_sentinel2(
    bbox=[area_bbox],
    start_date="2024-01-01",
    end_date="2024-01-31",
    max_cloud_cover=15.0
)
```

## Testing

Run the test script to verify your setup:

```bash
python scripts/test_sentinel_api.py
```

Run the examples:

```bash
python examples/satellite_data_query.py
```

## API Limits

Free tier includes:
- 30,000 processing units per month
- Access to all Sentinel data
- STAC catalog search (unlimited)

For production use, consider upgrading to a paid plan.

## Troubleshooting

### Authentication Fails

- Verify credentials are correct in `.env`
- Check that OAuth client is active in dashboard
- Ensure no extra spaces in credentials

### No Results Found

- Check that bbox coordinates are in correct order: [west, south, east, north]
- Verify date format: YYYY-MM-DD
- Try expanding date range or increasing cloud cover threshold
- Confirm the area has satellite coverage

### Rate Limiting

- Free tier has processing unit limits
- STAC search is unlimited
- Consider caching results for repeated queries

## Additional Resources

- [Sentinel Hub Documentation](https://docs.sentinel-hub.com/)
- [STAC Specification](https://stacspec.org/)
- [Sentinel-2 User Guide](https://sentinel.esa.int/web/sentinel/user-guides/sentinel-2-msi)
- [Sentinel-1 User Guide](https://sentinel.esa.int/web/sentinel/user-guides/sentinel-1-sar)

## Next Steps

1. Set up your credentials
2. Run the test script
3. Try the example queries
4. Integrate with your Earth observation pipelines
5. Explore additional collections and filters
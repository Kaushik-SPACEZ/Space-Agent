# Flood Query Dashboard - Usage Guide

## 🌊 Dashboard Features

### Natural Language Queries

The dashboard supports **case-insensitive** queries. You can type state names in any case:

✅ **All these work the same:**
- "Show me floods in Tamil Nadu"
- "Show me floods in tamilnadu"
- "Show me floods in TAMIL NADU"
- "Show me floods in TaMiL nAdU"

### Query Examples

#### By Location:
```
Show me floods in Tamil Nadu
Show me floods in kerala
What are the floods in WEST BENGAL?
List floods in bihar
```

#### By Time:
```
Show me recent floods in Kerala
What are the floods in 2024?
Show me floods in Tamil Nadu for 2023
List floods between January and March 2024
```

#### By Severity:
```
Show me severe floods
What are the catastrophic floods in 2024?
Show me high severity floods in Kerala
List moderate floods in Tamil Nadu
```

#### By Area:
```
Show me floods affecting more than 500 sq km
What are the large floods in West Bengal?
Show me floods with area greater than 1000 sq km
```

#### Combined Queries:
```
Show me severe floods in Tamil Nadu for 2024
What are the recent high severity floods in Kerala?
List floods in West Bengal in 2023 affecting more than 100 sq km
```

### Map Features

- **Color Coding by Severity:**
  - 🟢 Green = Low
  - 🟠 Orange = Moderate  
  - 🔴 Red = High
  - 🔴 Dark Red = Severe
  - 🟣 Purple = Catastrophic

- **Marker Size:** Larger markers = more severe floods

- **Click Markers:** View detailed information about each flood

- **Zoom & Pan:** Navigate the map to explore different regions

### Statistics Cards

- **Total Flood Events:** All floods in database
- **Recent Floods:** Floods from last 30 days
- **Total Area Affected:** Sum of all flooded areas (sq km)
- **States Affected:** Number of states with flood events

### SQL Display

- After each query, the generated SQL is shown
- This helps you understand how your natural language query was converted
- Useful for learning SQL or debugging queries

## 🔧 Technical Details

### Case-Insensitive Matching

The system uses PostgreSQL's `ILIKE` operator for all text matching:

```sql
-- Works for any case variation
WHERE state ILIKE '%tamil nadu%'
```

This ensures:
- "Tamil Nadu" matches "Tamil Nadu"
- "tamilnadu" matches "Tamil Nadu"
- "TAMIL NADU" matches "Tamil Nadu"
- Any case variation works

### API Endpoints

1. **GET /** - Dashboard homepage
2. **POST /api/query** - Natural language query
   ```json
   {
     "query": "Show me floods in Tamil Nadu"
   }
   ```

3. **GET /api/stats** - Overall statistics
4. **GET /api/map-data?limit=100** - Map data

### Database

- **Database:** PostgreSQL with PostGIS
- **Table:** flood_events
- **Records:** 250 flood events
- **Spatial:** PostGIS POINT geometry for each flood

## 💡 Tips

1. **Be Natural:** Type questions as you would ask a person
2. **Try Examples:** Click example buttons to see how queries work
3. **Check SQL:** Review generated SQL to understand the query
4. **Explore Map:** Click markers to see flood details
5. **Experiment:** Try different phrasings - the AI is flexible!

## 🐛 Troubleshooting

### No Results Found

If you get "No results found":
1. Check spelling of state names
2. Try a broader date range
3. Check if data exists for that state/time period
4. Try one of the example queries

### Map Not Loading

1. Check internet connection (map tiles from OpenStreetMap)
2. Refresh the page
3. Check browser console for errors

### Query Not Working

1. Try rephrasing the question
2. Use one of the example queries as a template
3. Check the generated SQL for issues
4. Simplify the query (one filter at a time)

## 📊 Data Coverage

- **States:** 19 Indian states
- **Time Period:** 2020-2024
- **Total Events:** 250
- **Severity Levels:** Low, Moderate, High, Severe, Catastrophic

## 🚀 Advanced Usage

### Custom Queries

You can ask complex questions:
```
Show me all severe floods in Tamil Nadu and Kerala in 2024 affecting more than 200 sq km
```

The AI will generate appropriate SQL with multiple conditions.

### Spatial Queries (Future)

With PostGIS, you can add spatial queries:
- "Show me floods within 50km of Chennai"
- "Find floods in a specific bounding box"
- "Calculate distance between flood events"

---

**Dashboard URL:** http://localhost:5000

**To Stop Server:** Press Ctrl+C in terminal

**To Restart:** Run `python app_dashboard.py`
"""
Flask Web Dashboard for Flood Query System
Provides REST API and web interface for natural language flood queries
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import psycopg2
from dotenv import load_dotenv
from groq import Groq
import os
import json

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize Groq client
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Database schema info for LLM
SCHEMA_INFO = """
Database: flood_events table

Columns:
- uei (VARCHAR): Unique event identifier
- start_date (DATE): Flood start date
- end_date (DATE): Flood end date
- duration_days (INTEGER): Duration in days
- latitude (DECIMAL): Latitude coordinate
- longitude (DECIMAL): Longitude coordinate
- state (VARCHAR): Indian state name
- district (VARCHAR): District name
- severity (VARCHAR): 'Low', 'Moderate', 'High', 'Severe', 'Catastrophic'
- area_affected_sqkm (DECIMAL): Flooded area in square kilometers
- main_cause (TEXT): Cause of flood
- description (TEXT): Event description
- event_source (VARCHAR): Data source
- geometry (GEOMETRY): PostGIS point geometry

Available Views:
- recent_floods: Floods from last 30 days
- severe_floods: High, Severe, and Catastrophic floods
- floods_by_state: Summary statistics by state
- floods_by_year: Summary statistics by year
"""


def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME", "earth_obs"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD")
    )


def nl_to_sql(natural_query: str) -> str:
    """Convert natural language to SQL using Groq"""
    prompt = f"""You are a SQL expert. Convert the following natural language query into a PostgreSQL SQL query.

{SCHEMA_INFO}

Rules:
1. Return ONLY the SQL query, no explanations
2. Use proper PostgreSQL syntax
3. For date queries, use DATE format 'YYYY-MM-DD'
4. For recent/latest queries, use ORDER BY start_date DESC
5. Always include LIMIT clause (default 50) unless user specifies otherwise
6. ALWAYS use ILIKE (not LIKE) for ALL text matching to ensure case-insensitive searches
7. For state names, district names, or any text fields, ALWAYS use ILIKE '%value%' pattern
8. For year queries, use EXTRACT(YEAR FROM start_date)
9. Return SELECT * or specific columns as appropriate

IMPORTANT: Text matching must be case-insensitive. Use ILIKE, not LIKE or =.
Example: WHERE state ILIKE '%tamil nadu%' (works for "Tamil Nadu", "tamilnadu", "TAMIL NADU", etc.)

Natural Language Query: {natural_query}

SQL Query:"""
    
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a SQL expert. Return only SQL queries, no explanations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=500
        )
        
        sql_query = response.choices[0].message.content.strip()
        sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
        return sql_query
        
    except Exception as e:
        print(f"LLM error: {e}")
        return None


def execute_sql(sql_query: str):
    """Execute SQL and return results"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql_query)
        
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            result_dict = {}
            for i, col in enumerate(columns):
                value = row[i]
                if hasattr(value, 'isoformat'):
                    value = value.isoformat()
                result_dict[col] = value
            results.append(result_dict)
        
        cursor.close()
        conn.close()
        return results
        
    except Exception as e:
        print(f"SQL execution error: {e}")
        return None


@app.route('/')
def index():
    """Serve the dashboard"""
    return render_template('dashboard_v2.html')

@app.route('/v1')
def index_v1():
    """Serve the old dashboard"""
    return render_template('dashboard.html')


@app.route('/api/query', methods=['POST'])
def query():
    """Handle natural language query"""
    data = request.json
    natural_query = data.get('query', '')
    
    if not natural_query:
        return jsonify({"error": "No query provided"}), 400
    
    # Convert to SQL
    sql_query = nl_to_sql(natural_query)
    if not sql_query:
        return jsonify({"error": "Failed to convert query to SQL"}), 500
    
    # Execute SQL
    results = execute_sql(sql_query)
    if results is None:
        return jsonify({"error": "Failed to execute SQL query", "sql": sql_query}), 500
    
    return jsonify({
        "natural_query": natural_query,
        "sql_query": sql_query,
        "results": results,
        "count": len(results)
    })


@app.route('/api/stats', methods=['GET'])
def stats():
    """Get overall statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Total events
        cursor.execute("SELECT COUNT(*) FROM flood_events")
        total_events = cursor.fetchone()[0]
        
        # By severity
        cursor.execute("""
            SELECT severity, COUNT(*) as count 
            FROM flood_events 
            GROUP BY severity
            ORDER BY 
                CASE severity
                    WHEN 'Low' THEN 1
                    WHEN 'Moderate' THEN 2
                    WHEN 'High' THEN 3
                    WHEN 'Severe' THEN 4
                    WHEN 'Catastrophic' THEN 5
                END
        """)
        severity_counts = {row[0]: row[1] for row in cursor.fetchall()}
        
        # By state (top 10)
        cursor.execute("""
            SELECT state, COUNT(*) as count 
            FROM flood_events 
            GROUP BY state 
            ORDER BY count DESC 
            LIMIT 10
        """)
        state_counts = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Recent floods (last 30 days)
        cursor.execute("SELECT COUNT(*) FROM recent_floods")
        recent_count = cursor.fetchone()[0]
        
        # Total area affected
        cursor.execute("SELECT SUM(area_affected_sqkm) FROM flood_events")
        total_area = cursor.fetchone()[0] or 0
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "total_events": total_events,
            "recent_floods": recent_count,
            "total_area_affected": round(float(total_area), 2),
            "severity_counts": severity_counts,
            "state_counts": state_counts
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/map-data', methods=['GET'])
def map_data():
    """Get flood data for map visualization"""
    try:
        limit = request.args.get('limit', 100, type=int)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(f"""
            SELECT 
                uei, state, district, start_date, severity,
                area_affected_sqkm, latitude, longitude, main_cause
            FROM flood_events
            ORDER BY start_date DESC
            LIMIT {limit}
        """)
        
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        
        features = []
        for row in rows:
            result_dict = {}
            for i, col in enumerate(columns):
                value = row[i]
                if hasattr(value, 'isoformat'):
                    value = value.isoformat()
                result_dict[col] = value
            features.append(result_dict)
        
        cursor.close()
        conn.close()
        
        return jsonify({"features": features})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🌊 FLOOD QUERY DASHBOARD")
    print("=" * 60)
    print("\nStarting server...")
    print("Dashboard URL: http://localhost:5000")
    print("\nPress Ctrl+C to stop")
    print("=" * 60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
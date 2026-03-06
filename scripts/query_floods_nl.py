"""
Natural Language to SQL Query System for Flood Data
Uses Groq LLM to convert natural language queries to SQL
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import psycopg2
from dotenv import load_dotenv
from groq import Groq
import json

# Load environment variables
load_dotenv()


class FloodQuerySystem:
    """Natural language query system for flood data"""
    
    def __init__(self):
        """Initialize the query system"""
        # Initialize Groq client
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        # Database connection
        self.db_conn = None
        
        # Database schema information for LLM
        self.schema_info = """
        Database: flood_events table
        
        Columns:
        - uei (VARCHAR): Unique event identifier (e.g., 'FLOOD-IND-0001')
        - start_date (DATE): Flood start date
        - end_date (DATE): Flood end date
        - duration_days (INTEGER): Duration in days
        - latitude (DECIMAL): Latitude coordinate
        - longitude (DECIMAL): Longitude coordinate
        - state (VARCHAR): Indian state name
        - district (VARCHAR): District name (may be empty)
        - severity (VARCHAR): One of: 'Low', 'Moderate', 'High', 'Severe', 'Catastrophic'
        - area_affected_sqkm (DECIMAL): Flooded area in square kilometers
        - main_cause (TEXT): Cause of flood
        - description (TEXT): Event description
        - event_source (VARCHAR): Data source
        - created_at (TIMESTAMP): Record creation time
        - updated_at (TIMESTAMP): Last update time
        
        Available Views:
        - recent_floods: Floods from last 30 days
        - severe_floods: High, Severe, and Catastrophic floods
        - floods_by_state: Summary statistics by state
        - floods_by_year: Summary statistics by year
        """
    
    def connect_db(self):
        """Connect to PostgreSQL database"""
        try:
            self.db_conn = psycopg2.connect(
                host=os.getenv("DB_HOST", "localhost"),
                port=os.getenv("DB_PORT", "5432"),
                database=os.getenv("DB_NAME", "earth_obs"),
                user=os.getenv("DB_USER", "postgres"),
                password=os.getenv("DB_PASSWORD")
            )
            return True
        except Exception as e:
            print(f"✗ Database connection failed: {e}")
            return False
    
    def nl_to_sql(self, natural_query: str) -> str:
        """
        Convert natural language query to SQL using Groq LLM
        
        Args:
            natural_query: Natural language question
            
        Returns:
            SQL query string
        """
        prompt = f"""You are a SQL expert. Convert the following natural language query into a PostgreSQL SQL query.

{self.schema_info}

Rules:
1. Return ONLY the SQL query, no explanations
2. Use proper PostgreSQL syntax
3. For date queries, use DATE format 'YYYY-MM-DD'
4. For recent/latest queries, use ORDER BY start_date DESC
5. Always include LIMIT clause (default 10) unless user specifies otherwise
6. Use ILIKE for case-insensitive text matching
7. For year queries, use EXTRACT(YEAR FROM start_date)
8. Return SELECT * or specific columns as appropriate

Natural Language Query: {natural_query}

SQL Query:"""
        
        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a SQL expert. Return only SQL queries, no explanations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            sql_query = response.choices[0].message.content.strip()
            
            # Clean up the SQL query
            sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
            
            return sql_query
            
        except Exception as e:
            print(f"✗ LLM error: {e}")
            return None
    
    def execute_sql(self, sql_query: str):
        """
        Execute SQL query and return results
        
        Args:
            sql_query: SQL query string
            
        Returns:
            List of result rows
        """
        try:
            cursor = self.db_conn.cursor()
            cursor.execute(sql_query)
            
            # Get column names
            columns = [desc[0] for desc in cursor.description]
            
            # Fetch results
            rows = cursor.fetchall()
            
            # Convert to list of dictionaries
            results = []
            for row in rows:
                result_dict = {}
                for i, col in enumerate(columns):
                    value = row[i]
                    # Convert date/datetime to string
                    if hasattr(value, 'isoformat'):
                        value = value.isoformat()
                    result_dict[col] = value
                results.append(result_dict)
            
            cursor.close()
            return results
            
        except Exception as e:
            print(f"✗ SQL execution error: {e}")
            return None
    
    def query(self, natural_query: str):
        """
        Process natural language query end-to-end
        
        Args:
            natural_query: Natural language question
            
        Returns:
            Dictionary with SQL, results, and metadata
        """
        print(f"\n{'='*60}")
        print(f"Query: {natural_query}")
        print(f"{'='*60}")
        
        # Convert to SQL
        print("\n🔄 Converting to SQL...")
        sql_query = self.nl_to_sql(natural_query)
        
        if not sql_query:
            return {"error": "Failed to convert query to SQL"}
        
        print(f"✓ Generated SQL:\n{sql_query}")
        
        # Execute SQL
        print("\n🔄 Executing query...")
        results = self.execute_sql(sql_query)
        
        if results is None:
            return {"error": "Failed to execute SQL query", "sql": sql_query}
        
        print(f"✓ Found {len(results)} results")
        
        return {
            "natural_query": natural_query,
            "sql_query": sql_query,
            "results": results,
            "count": len(results)
        }
    
    def print_results(self, response: dict):
        """Pretty print query results"""
        if "error" in response:
            print(f"\n✗ Error: {response['error']}")
            return
        
        print(f"\n{'='*60}")
        print(f"RESULTS ({response['count']} records)")
        print(f"{'='*60}")
        
        if response['count'] == 0:
            print("No results found")
            return
        
        # Print first 5 results
        for i, result in enumerate(response['results'][:5], 1):
            print(f"\n{i}. {result.get('uei', 'N/A')}")
            print(f"   State: {result.get('state', 'N/A')}")
            print(f"   District: {result.get('district', 'N/A')}")
            print(f"   Date: {result.get('start_date', 'N/A')}")
            print(f"   Severity: {result.get('severity', 'N/A')}")
            print(f"   Area: {result.get('area_affected_sqkm', 'N/A')} sq km")
            print(f"   Cause: {result.get('main_cause', 'N/A')}")
        
        if response['count'] > 5:
            print(f"\n... and {response['count'] - 5} more results")
    
    def close(self):
        """Close database connection"""
        if self.db_conn:
            self.db_conn.close()


def main():
    """Main function with example queries"""
    print("\n" + "=" * 60)
    print("NATURAL LANGUAGE FLOOD QUERY SYSTEM")
    print("=" * 60)
    
    # Initialize system
    system = FloodQuerySystem()
    
    if not system.connect_db():
        print("\n✗ Failed to connect to database")
        return
    
    print("✓ System initialized")
    
    # Example queries
    example_queries = [
        "Show me all floods in Tamil Nadu",
        "Show me severe floods in 2024",
        "What are the recent floods in Kerala?",
        "Show me floods affecting more than 500 sq km",
        "List floods in West Bengal in 2023"
    ]
    
    print("\n" + "=" * 60)
    print("EXAMPLE QUERIES")
    print("=" * 60)
    
    try:
        for query in example_queries:
            response = system.query(query)
            system.print_results(response)
            print("\n" + "-" * 60)
        
        print("\n" + "=" * 60)
        print("✓ ALL QUERIES COMPLETED")
        print("=" * 60)
        print("\nYou can now:")
        print("1. Modify this script to add your own queries")
        print("2. Build a web interface or API")
        print("3. Integrate with your existing agent system")
        
    finally:
        system.close()
        print("\n✓ Database connection closed")


if __name__ == "__main__":
    main()
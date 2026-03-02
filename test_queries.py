"""
Test script for Earth Observation Agent
Tests various query types and validates responses
"""
import requests
import json
from typing import Dict, Any


class EarthAgentTester:
    """Test suite for Earth Observation Agent"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = []
    
    def test_query(self, query: str, expected_report_type: str = None) -> Dict[str, Any]:
        """
        Test a single query
        
        Args:
            query: Natural language query
            expected_report_type: Expected report type in response
            
        Returns:
            Test result dictionary
        """
        print(f"\n{'='*80}")
        print(f"Testing Query: {query}")
        print(f"{'='*80}")
        
        try:
            response = requests.post(
                f"{self.base_url}/query",
                json={"query": query},
                timeout=30
            )
            
            result = response.json()
            
            # Check if successful
            if result.get("success"):
                print("✅ Query successful!")
                
                data = result.get("data", {})
                print(f"\nReport Type: {data.get('report_type')}")
                print(f"Location: {data.get('location', {}).get('state')}")
                
                if data.get('location', {}).get('district'):
                    print(f"District: {data.get('location', {}).get('district')}")
                
                time_range = data.get('time_range', {})
                print(f"Time Range: {time_range.get('start')} to {time_range.get('end')}")
                print(f"Satellite: {data.get('satellite')}")
                
                # Print key details
                details = data.get('details', {})
                print(f"\nKey Details:")
                for key, value in list(details.items())[:5]:
                    print(f"  - {key}: {value}")
                
                # Check GeoJSON
                if data.get('geojson'):
                    feature_count = len(data['geojson'].get('features', []))
                    print(f"\nGeoJSON Features: {feature_count}")
                
                # Validate expected report type
                if expected_report_type:
                    actual_type = data.get('report_type')
                    if actual_type == expected_report_type:
                        print(f"✅ Report type matches: {expected_report_type}")
                    else:
                        print(f"❌ Report type mismatch: expected {expected_report_type}, got {actual_type}")
                
                test_result = {
                    "query": query,
                    "status": "success",
                    "response": result
                }
                
            else:
                print("❌ Query failed!")
                error = result.get("error", {})
                print(f"Error Type: {error.get('error_type')}")
                print(f"Error Message: {error.get('error')}")
                
                if error.get('suggestion'):
                    print(f"Suggestion: {error.get('suggestion')}")
                
                if error.get('available_options'):
                    print(f"Available Options:")
                    for option in error.get('available_options', []):
                        print(f"  - {option}")
                
                test_result = {
                    "query": query,
                    "status": "failed",
                    "error": error
                }
            
            self.test_results.append(test_result)
            return test_result
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {str(e)}")
            test_result = {
                "query": query,
                "status": "error",
                "error": str(e)
            }
            self.test_results.append(test_result)
            return test_result
    
    def test_health(self):
        """Test health endpoint"""
        print(f"\n{'='*80}")
        print("Testing Health Endpoint")
        print(f"{'='*80}")
        
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            result = response.json()
            
            print(f"Agent Status: {result.get('agent_status')}")
            print(f"Timestamp: {result.get('timestamp')}")
            
            print("\nPipeline Status:")
            for pipeline, status in result.get('pipelines', {}).items():
                status_icon = "✅" if status.get('status') == 'healthy' else "❌"
                print(f"  {status_icon} {pipeline}: {status.get('status')}")
            
            return result
            
        except Exception as e:
            print(f"❌ Health check failed: {str(e)}")
            return None
    
    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("\n" + "="*80)
        print("EARTH OBSERVATION AGENT - COMPREHENSIVE TEST SUITE")
        print("="*80)
        
        # Test health first
        self.test_health()
        
        # Flood queries
        print("\n\n" + "="*80)
        print("FLOOD MONITORING TESTS")
        print("="*80)
        
        self.test_query(
            "Show flood in Tamil Nadu past 2 weeks",
            expected_report_type="flood_monitoring"
        )
        
        self.test_query(
            "Flood extent in Chennai after cyclone",
            expected_report_type="flood_monitoring"
        )
        
        self.test_query(
            "Flooding in Kerala during August 2023",
            expected_report_type="flood_monitoring"
        )
        
        # Vegetation queries
        print("\n\n" + "="*80)
        print("VEGETATION MONITORING TESTS")
        print("="*80)
        
        self.test_query(
            "Crop stress in Coimbatore during January 2023",
            expected_report_type="vegetation_monitoring"
        )
        
        self.test_query(
            "NDVI values for Punjab rice fields last month",
            expected_report_type="vegetation_monitoring"
        )
        
        self.test_query(
            "Vegetation data in Kerala in 2022",
            expected_report_type="vegetation_monitoring"
        )
        
        # Generic queries
        print("\n\n" + "="*80)
        print("GENERIC DATASET TESTS")
        print("="*80)
        
        self.test_query(
            "Available EO datasets for Andhra Pradesh in October 2023",
            expected_report_type="dataset_availability"
        )
        
        self.test_query(
            "What satellite data is available for Karnataka?",
            expected_report_type="dataset_availability"
        )
        
        # Edge cases
        print("\n\n" + "="*80)
        print("EDGE CASE TESTS")
        print("="*80)
        
        self.test_query("Show flood in XYZ State past week")  # Invalid state
        self.test_query("Data for Tamil Nadu in year 3000")  # Future date
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        
        total = len(self.test_results)
        successful = sum(1 for r in self.test_results if r['status'] == 'success')
        failed = sum(1 for r in self.test_results if r['status'] == 'failed')
        errors = sum(1 for r in self.test_results if r['status'] == 'error')
        
        print(f"\nTotal Tests: {total}")
        print(f"✅ Successful: {successful}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️  Errors: {errors}")
        
        if successful == total:
            print("\n🎉 All tests passed!")
        else:
            print(f"\n⚠️  {failed + errors} test(s) did not pass")
        
        print("\n" + "="*80)


def main():
    """Main test execution"""
    print("Starting Earth Observation Agent Tests...")
    print("Make sure the API server is running on http://localhost:8000")
    
    input("\nPress Enter to continue...")
    
    tester = EarthAgentTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
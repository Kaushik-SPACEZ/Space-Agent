"""
FastAPI application for Earth Observation Agent
Main entry point for the API
"""
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any
import os
from dotenv import load_dotenv

from models.schemas import QueryInput
from agents.earth_agent import get_agent

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Earth Observation Agent API",
    description="Multi-pipeline natural language spatial intelligence engine for Earth observation data",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Earth Agent
earth_agent = get_agent(data_dir="data")


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Earth Observation Agent API",
        "version": "1.0.0",
        "description": "Multi-pipeline natural language spatial intelligence engine",
        "endpoints": {
            "query": "/query - Process natural language Earth observation queries",
            "health": "/health - Check system health",
            "pipelines": "/pipelines - Get available pipeline information",
            "docs": "/docs - Interactive API documentation"
        }
    }


@app.post("/query", response_model=Dict[str, Any])
async def process_query(query_input: QueryInput):
    """
    Process natural language Earth observation query
    
    Supports queries like:
    - "Show flood in Tamil Nadu past 2 weeks"
    - "Crop stress in Coimbatore during January 2023"
    - "Vegetation data in Kerala in 2022"
    - "Available EO datasets for Andhra Pradesh in October 2023"
    
    Returns:
        Standardized response with GeoJSON data
    """
    try:
        # Process query through Earth Agent
        result = earth_agent.process_query(query_input.query)
        
        if result["success"]:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=result
            )
        else:
            # Return error response with appropriate status code
            error_type = result["error"]["error_type"]
            
            if error_type == "no_data_found":
                status_code = status.HTTP_404_NOT_FOUND
            elif error_type == "validation_error" or error_type == "invalid_parameters":
                status_code = status.HTTP_400_BAD_REQUEST
            else:
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            
            return JSONResponse(
                status_code=status_code,
                content=result
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """
    Health check endpoint
    Returns status of agent and all pipelines
    """
    try:
        health = earth_agent.health_check()
        
        if health["agent_status"] == "healthy":
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=health
            )
        else:
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content=health
            )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "agent_status": "unhealthy",
                "error": str(e)
            }
        )


@app.get("/pipelines")
async def get_pipelines():
    """
    Get information about available pipelines
    """
    return earth_agent.get_pipeline_info()


@app.get("/examples")
async def get_examples():
    """
    Get example queries for each pipeline
    """
    return {
        "flood_queries": [
            "Show flood in Tamil Nadu past 2 weeks",
            "Flood extent in Chennai after cyclone",
            "Flooding in Kerala during August 2023",
            "Water logging in Mumbai last month"
        ],
        "vegetation_queries": [
            "Crop stress in Coimbatore during January 2023",
            "NDVI values for Punjab rice fields last month",
            "Vegetation data in Kerala in 2022",
            "Crop health in Haryana past 3 months"
        ],
        "generic_queries": [
            "Available EO datasets for Andhra Pradesh in October 2023",
            "Satellite coverage for Karnataka",
            "What data is available for Tamil Nadu?",
            "Show me all datasets for Gujarat in 2023"
        ]
    }


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "error": exc.detail,
                "error_type": "http_error"
            }
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "error": "An unexpected error occurred",
                "error_type": "internal_error",
                "details": str(exc)
            }
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", 8000))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug
    )
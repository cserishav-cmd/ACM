from fastapi import APIRouter, Query, HTTPException
from typing import Optional
import os
import json
from src.weather import WeatherService

router = APIRouter()
weather_service = WeatherService()

@router.get("/forecast")
async def get_weather_forecast(
    lat: float = Query(..., description="Latitude of the location"),
    lon: float = Query(..., description="Longitude of the location"),
    crop_condition: Optional[str] = Query(None, description="Current detected crop condition (e.g., Leaf Blast)")
):
    """
    Fetch the 7-day weather forecast and agricultural spraying insights 
    based on the provided latitude and longitude.
    """
    try:
        data = weather_service.get_forecast(lat, lon, crop_condition)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/impact-analysis")
async def get_impact_analysis():
    """
    Returns the data-driven weather-agrochemical impact analysis, including correlations
    and derived thresholds, as well as paths to generated visualizations.
    """
    try:
        insights_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "src", "analysis", "agrochemical_insights.json")
        insights = {}
        if os.path.exists(insights_path):
            with open(insights_path, "r") as f:
                insights = json.load(f)
                
        return {
            "success": True,
            "data": insights,
            "visualizations": {
                "correlation_heatmap": "/assets/analysis/correlation_heatmap.png",
                "yield_impact_scatter": "/assets/analysis/yield_impact_scatter.png"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch analysis: {str(e)}")

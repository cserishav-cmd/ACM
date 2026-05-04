from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from src.weather import WeatherService

router = APIRouter()
weather_service = WeatherService()

@router.get("/forecast")
async def get_weather_forecast(
    lat: float = Query(..., description="Latitude of the location"),
    lon: float = Query(..., description="Longitude of the location")
):
    """
    Fetch the 7-day weather forecast and agricultural spraying insights 
    based on the provided latitude and longitude.
    """
    try:
        data = weather_service.get_forecast(lat, lon)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

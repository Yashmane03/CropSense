import httpx
from typing import Optional, Dict, Any

OPEN_METEO_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
OPEN_METEO_GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"

async def fetch_weather_data(lat: float, lon: float) -> Dict[str, Any]:
    """
    Fetches real weather data from Open-Meteo API for given lat/lon.
    Retrieves current temperature, relative humidity, current precipitation,
    and 3-day recent historical rainfall sum.
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,rain,precipitation",
        "past_days": 3,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": "auto"
    }
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(OPEN_METEO_FORECAST_URL, params=params)
        if response.status_code != 200:
            raise Exception(f"Open-Meteo API error (HTTP {response.status_code}): {response.text}")
        
        data = response.json()
        
        current = data.get("current", {})
        daily = data.get("daily", {})
        
        recent_rain_sum = 0.0
        if "precipitation_sum" in daily and daily["precipitation_sum"]:
            # Sum up precipitation over available past days
            recent_rain_sum = round(sum([p for p in daily["precipitation_sum"] if p is not None]), 2)
            
        temp = current.get("temperature_2m", 25.0)
        humidity = current.get("relative_humidity_2m", 60.0)
        current_rain = current.get("rain", 0.0) or current.get("precipitation", 0.0) or 0.0

        return {
            "latitude": lat,
            "longitude": lon,
            "temperature_c": temp,
            "humidity_percent": humidity,
            "current_rain_mm": current_rain,
            "recent_rainfall_mm": recent_rain_sum,
            "timezone": data.get("timezone", "UTC"),
            "elevation": data.get("elevation", 0)
        }

async def geocode_location(location_name: str) -> Dict[str, Any]:
    """
    Resolves city or location name to latitude and longitude using Open-Meteo Geocoding API.
    """
    params = {
        "name": location_name,
        "count": 5,
        "language": "en",
        "format": "json"
    }
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(OPEN_METEO_GEOCODING_URL, params=params)
        if response.status_code != 200:
            raise Exception(f"Geocoding API error (HTTP {response.status_code}): {response.text}")
        
        data = response.json()
        results = data.get("results", [])
        if not results:
            raise Exception(f"No location found matching '{location_name}'")
        
        top = results[0]
        parts = [top.get("name")]
        if top.get("admin1"):
            parts.append(top.get("admin1"))
        if top.get("country"):
            parts.append(top.get("country"))
        formatted_name = ", ".join([p for p in parts if p])

        return {
            "name": top.get("name"),
            "formatted_name": formatted_name,
            "country": top.get("country", ""),
            "admin1": top.get("admin1", ""),
            "latitude": top["latitude"],
            "longitude": top["longitude"],
            "all_results": results
        }

import sys
import os
import asyncio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.services.weather import geocode_location, fetch_weather_data

async def test_location_flow():
    cities = ["Pune", "Mumbai", "Delhi"]
    
    for city in cities:
        print(f"\n--- Testing Search Location: '{city}' ---")
        geo = await geocode_location(city)
        print(f"Geocoded Name: {geo['formatted_name']}")
        print(f"Coordinates: {geo['latitude']:.2f}°, {geo['longitude']:.2f}°")
        
        weather = await fetch_weather_data(geo['latitude'], geo['longitude'])
        print(f"Open-Meteo Weather for {city}:")
        print(f"  Temp: {weather['temperature_c']} C")
        print(f"  Humidity: {weather['humidity_percent']}%")
        print(f"  Recent Rain: {weather['recent_rainfall_mm']} mm")

        assert geo['latitude'] != 0.0
        assert geo['longitude'] != 0.0
        assert 'temperature_c' in weather

    print("\n[SUCCESS] Location Geocoding & Weather flow verified for Pune, Mumbai, and Delhi!")

if __name__ == "__main__":
    asyncio.run(test_location_flow())

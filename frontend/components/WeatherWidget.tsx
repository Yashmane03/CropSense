'use client';

import React, { useState, useEffect } from 'react';
import { fetchWeather, geocodeLocation, WeatherData, GeocodedLocation } from '@/lib/api';

interface WeatherWidgetProps {
  onWeatherLoaded?: (weather: WeatherData) => void;
  onLocationChange?: (lat?: number, lon?: number, city?: string) => void;
  initialCity?: string;
}

export default function WeatherWidget({
  onWeatherLoaded,
  onLocationChange,
  initialCity = "Pune"
}: WeatherWidgetProps) {
  const [selectedLocation, setSelectedLocation] = useState<GeocodedLocation | null>(null);
  const [weatherData, setWeatherData] = useState<WeatherData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [cityInput, setCityInput] = useState<string>(initialCity);

  const searchLocation = async (query: string) => {
    if (!query || !query.trim()) {
      setError("Please enter a location name (e.g. Pune, Mumbai, Delhi).");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      // Step 1: Geocoding API -> resolve latitude & longitude
      const geo = await geocodeLocation(query.trim());
      setSelectedLocation(geo);

      // Step 2: Fetch Open-Meteo weather using exact coordinates
      const weather = await fetchWeather(geo.latitude, geo.longitude, geo.formatted_name);
      setWeatherData(weather);

      // Step 3: Notify parent component of exact selected coordinates
      if (onLocationChange) {
        onLocationChange(geo.latitude, geo.longitude, geo.formatted_name);
      }
      if (onWeatherLoaded) {
        onWeatherLoaded(weather);
      }
    } catch (err: any) {
      setError(err.message || `Unable to find location matching '${query}'`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    searchLocation(initialCity);
  }, []);

  const handleSearchSubmit = () => {
    searchLocation(cityInput);
  };

  return (
    <div className="bg-emerald-50/50 border border-emerald-100 rounded-lg p-4 space-y-3">
      {/* Search Header - NO <form> tag to prevent hydration error */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-emerald-100/60 pb-2">
        <div>
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Weather context</span>
          {selectedLocation && (
            <p className="text-sm font-medium text-slate-800 flex items-center gap-2">
              <span>{selectedLocation.formatted_name}</span>
              <span className="text-xs font-mono text-slate-500 font-normal">
                ({selectedLocation.latitude.toFixed(2)}°, {selectedLocation.longitude.toFixed(2)}°)
              </span>
            </p>
          )}
        </div>

        {/* Using <div> instead of <form> to prevent nested form HTML hydration error */}
        <div className="flex items-center space-x-2">
          <input
            type="text"
            value={cityInput}
            onChange={(e) => setCityInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault();
                handleSearchSubmit();
              }
            }}
            placeholder="Search location (e.g. Pune, Mumbai)..."
            className="text-xs bg-white border border-slate-200 rounded px-2.5 py-1 focus:outline-none focus:border-emerald-700"
          />
          <button
            type="button"
            onClick={handleSearchSubmit}
            disabled={loading}
            className="px-2.5 py-1 bg-emerald-800 text-white rounded text-xs hover:bg-emerald-900 transition-colors disabled:opacity-50"
          >
            {loading ? 'Fetching...' : 'Update'}
          </button>
        </div>
      </div>

      {/* Weather details display */}
      {error ? (
        <p className="text-xs text-amber-700 font-medium">{error}</p>
      ) : loading ? (
        <div className="py-3 flex items-center space-x-2 text-xs text-slate-500">
          <span className="w-3 h-3 border-2 border-emerald-700 border-t-transparent rounded-full animate-spin inline-block" />
          <span>Fetching geocoding & live weather data...</span>
        </div>
      ) : weatherData ? (
        <div className="grid grid-cols-3 gap-2 text-center">
          <div className="bg-white p-2.5 rounded border border-slate-200/80">
            <span className="block text-[11px] text-slate-500">Temperature</span>
            <span className="text-sm font-bold text-slate-800">{weatherData.temperature_c}°C</span>
          </div>

          <div className="bg-white p-2.5 rounded border border-slate-200/80">
            <span className="block text-[11px] text-slate-500">Humidity</span>
            <span className="text-sm font-bold text-slate-800">{weatherData.humidity_percent}%</span>
          </div>

          <div className="bg-white p-2.5 rounded border border-slate-200/80">
            <span className="block text-[11px] text-slate-500">Recent Rainfall</span>
            <span className="text-sm font-bold text-slate-800">{weatherData.recent_rainfall_mm} mm</span>
          </div>
        </div>
      ) : null}
    </div>
  );
}

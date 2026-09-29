from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

class FieldObservationSchema(BaseModel):
    crop: str = Field(default="Tomato", description="Crop species")
    growth_stage: str = Field(default="vegetative", description="early, vegetative, flowering, fruiting")
    soil_condition: str = Field(default="normal", description="dry, normal, wet")
    irrigation: str = Field(default="normal", description="none, normal, excessive")
    pests: str = Field(default="no", description="yes, no, unsure")
    recent_rainfall: str = Field(default="moderate", description="low, moderate, heavy")

class LocationInputSchema(BaseModel):
    latitude: Optional[float] = Field(default=None, description="Latitude coordinate")
    longitude: Optional[float] = Field(default=None, description="Longitude coordinate")
    city_search: Optional[str] = Field(default=None, description="City or region search name")

class ReanalyzeRequestSchema(BaseModel):
    analysis_id: Optional[str] = Field(default=None, description="ID of previous analysis to re-analyze")
    image_url: Optional[str] = Field(default=None, description="Saved image URL")
    field_observations: FieldObservationSchema
    location: LocationInputSchema

class WeatherRequestSchema(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    city: Optional[str] = None

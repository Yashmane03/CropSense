import os
import json
import base64
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.schemas.api_schemas import (
    FieldObservationSchema,
    LocationInputSchema,
    ReanalyzeRequestSchema,
    WeatherRequestSchema
)
from backend.services.image_quality import check_image_quality
from backend.services.vision import analyze_crop_image
from backend.services.weather import fetch_weather_data, geocode_location
from backend.reasoning.evidence_engine import evaluate_context_evidence
from backend.services.advisory import get_advisory_for_condition
from backend.services.database import db_service, UPLOADS_DIR

app = FastAPI(
    title="CropSense API",
    description="Context-Aware Crop Health Assessment Platform Backend",
    version="1.0.0"
)

# CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount local uploads static directory for image serving fallback
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")


@app.get("/api/health")
def health_check():
    return {"status": "ok", "platform": "CropSense", "target_crop": "Tomato"}


@app.get("/api/weather")
async def get_weather(
    lat: Optional[float] = Query(None),
    lon: Optional[float] = Query(None),
    city: Optional[str] = Query(None)
):
    """
    Retrieves real Open-Meteo weather data by lat/lon or city search.
    """
    try:
        if lat is not None and lon is not None:
            location_name = city.strip() if (city and city.strip()) else f"Coords ({lat:.2f}, {lon:.2f})"
        elif city and city.strip():
            geo = await geocode_location(city.strip())
            lat = geo["latitude"]
            lon = geo["longitude"]
            location_name = geo.get("formatted_name") or f"{geo['name']}, {geo['country']}"
        else:
            geo = await geocode_location("Pune")
            lat = geo["latitude"]
            lon = geo["longitude"]
            location_name = geo.get("formatted_name") or "Pune, Maharashtra, India"

        weather = await fetch_weather_data(lat, lon)
        weather["location_name"] = location_name
        return {"success": True, "weather": weather}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Weather retrieval failed: {str(e)}")


@app.post("/api/analyze")
async def analyze_crop(
    image: UploadFile = File(...),
    field_observations: str = Form(...),  # JSON string of FieldObservationSchema
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    city_search: Optional[str] = Form(None)
):
    """
    Main End-to-End Crop Assessment Pipeline:
    1. Check real image quality (blur, dark, bright, res). Stop if insufficient!
    2. Run EfficientNet-B0 fine-tuned PyTorch vision model.
    3. Fetch real Open-Meteo weather.
    4. Run evidence/rule-based reasoning engine (Visual + Weather + Field Obs).
    5. Generate advisory recommendations.
    6. Save complete analysis record to Supabase / DB.
    """
    image_bytes = await image.read()

    # Step 1: Image Quality Check
    quality_result = check_image_quality(image_bytes)
    if not quality_result["is_acceptable"]:
        return {
            "success": False,
            "stage": "image_quality_check",
            "is_acceptable": False,
            "message": quality_result["message"],
            "issues": quality_result["issues"],
            "metrics": quality_result["metrics"]
        }

    # Step 2: Vision Model Inference (PyTorch EfficientNet-B0)
    try:
        visual_predictions = analyze_crop_image(image_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Vision Model inference failed: {str(e)}")

    # Step 3: Real Weather Data Fetching
    try:
        if latitude is not None and longitude is not None:
            lat, lon = latitude, longitude
            loc_name = city_search.strip() if (city_search and city_search.strip()) else f"Coords ({lat:.2f}, {lon:.2f})"
        elif city_search and city_search.strip():
            geo = await geocode_location(city_search.strip())
            lat, lon = geo["latitude"], geo["longitude"]
            loc_name = geo.get("formatted_name") or f"{geo['name']}, {geo['country']}"
        else:
            geo = await geocode_location("Pune")
            lat, lon = geo["latitude"], geo["longitude"]
            loc_name = geo.get("formatted_name") or "Pune, Maharashtra, India"

        weather_data = await fetch_weather_data(lat, lon)
        weather_data["location_name"] = loc_name
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to retrieve weather data: {str(e)}")

    # Parse field observations JSON
    try:
        obs_dict = json.loads(field_observations)
        field_obs = FieldObservationSchema(**obs_dict).dict()
    except Exception as e:
        field_obs = FieldObservationSchema().dict()

    # Step 4: Context Reasoning Engine
    reasoning_result = evaluate_context_evidence(
        visual_predictions=visual_predictions,
        weather_data=weather_data,
        field_obs=field_obs
    )

    # Step 5: Agricultural Advisory
    advisory = get_advisory_for_condition(reasoning_result["condition_key"])

    # Step 6: Save Image & Analysis Record to Database
    image_url = await db_service.upload_image(image_bytes, image.filename or "tomato_leaf.jpg")

    record = await db_service.save_analysis(
        crop="Tomato",
        image_url=image_url,
        final_assessment=reasoning_result["final_assessment"],
        confidence=reasoning_result["confidence_level"],
        is_uncertain=reasoning_result["is_uncertain"],
        visual_predictions=visual_predictions,
        weather_data=weather_data,
        field_observations=field_obs,
        evidence={
            "posterior_probabilities": reasoning_result["posterior_probabilities"],
            "visual_evidence": reasoning_result["visual_evidence"],
            "why_this_assessment": reasoning_result["why_this_assessment"],
            "contextual_adjustments": reasoning_result["contextual_adjustments"],
            "uncertainty_reason": reasoning_result.get("uncertainty_reason")
        },
        advisory=advisory
    )

    return {
        "success": True,
        "is_acceptable": True,
        "quality_metrics": quality_result["metrics"],
        "analysis": record
    }


@app.post("/api/reanalyze")
async def reanalyze_crop(payload: ReanalyzeRequestSchema):
    """
    CropSense USP: Re-analyzes the SAME image with NEW context (weather / soil / irrigation / rainfall).
    Re-runs reasoning engine and highlights the evidence delta between Initial and Updated Assessment!
    """
    if not payload.analysis_id and not payload.image_url:
        raise HTTPException(status_code=400, detail="Must provide analysis_id or image_url for re-analysis.")

    initial_record = None
    if payload.analysis_id:
        initial_record = await db_service.get_analysis_by_id(payload.analysis_id)

    if initial_record:
        image_url = initial_record["image_url"]
        visual_predictions = initial_record["visual_predictions"]
    else:
        image_url = payload.image_url
        # If no prior visual prediction, default uniform predictions
        visual_predictions = {
            "top_class": "Tomato___healthy",
            "top_probability": 0.5,
            "probabilities": {
                "Tomato___healthy": 0.5,
                "Tomato___Early_blight": 0.2,
                "Tomato___Late_blight": 0.2,
                "Tomato___Leaf_Mold": 0.1
            }
        }

    # Fetch updated weather
    loc = payload.location
    try:
        if loc.city_search and loc.city_search.strip():
            geo = await geocode_location(loc.city_search.strip())
            lat, lon = geo["latitude"], geo["longitude"]
            loc_name = f"{geo['name']}, {geo['country']}"
        elif loc.latitude is not None and loc.longitude is not None:
            lat, lon = loc.latitude, loc.longitude
            loc_name = f"Coords ({lat:.2f}, {lon:.2f})"
        else:
            lat, lon = 12.9716, 77.5946
            loc_name = "Updated Field Coordinates"

        weather_data = await fetch_weather_data(lat, lon)
        weather_data["location_name"] = loc_name
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch updated weather: {str(e)}")

    new_field_obs = payload.field_observations.dict()

    # Re-evaluate reasoning engine with SAME visual predictions + NEW context
    updated_reasoning = evaluate_context_evidence(
        visual_predictions=visual_predictions,
        weather_data=weather_data,
        field_obs=new_field_obs
    )

    advisory = get_advisory_for_condition(updated_reasoning["condition_key"])

    # Save new analysis record
    updated_record = await db_service.save_analysis(
        crop="Tomato",
        image_url=image_url,
        final_assessment=updated_reasoning["final_assessment"],
        confidence=updated_reasoning["confidence_level"],
        is_uncertain=updated_reasoning["is_uncertain"],
        visual_predictions=visual_predictions,
        weather_data=weather_data,
        field_observations=new_field_obs,
        evidence={
            "posterior_probabilities": updated_reasoning["posterior_probabilities"],
            "visual_evidence": updated_reasoning["visual_evidence"],
            "why_this_assessment": updated_reasoning["why_this_assessment"],
            "contextual_adjustments": updated_reasoning["contextual_adjustments"],
            "uncertainty_reason": updated_reasoning.get("uncertainty_reason")
        },
        advisory=advisory
    )

    # Compare Initial vs Updated
    initial_assessment = initial_record["final_assessment"] if initial_record else "Initial Assessment"
    is_updated = initial_assessment != updated_reasoning["final_assessment"]

    return {
        "success": True,
        "is_context_updated": True,
        "assessment_changed": is_updated,
        "message": "Assessment updated because new contextual evidence was provided." if is_updated else "Context updated; assessment confirmed.",
        "initial_record": initial_record,
        "updated_record": updated_record
    }


@app.get("/api/analysis/{analysis_id}")
async def get_analysis_detail(analysis_id: str):
    record = await db_service.get_analysis_by_id(analysis_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Analysis with ID {analysis_id} not found.")
    return {"success": True, "analysis": record}


@app.get("/api/history")
async def get_history(limit: int = 50):
    history = await db_service.get_history(limit=limit)
    return {"success": True, "count": len(history), "history": history}


@app.post("/api/upload")
async def upload_file(image: UploadFile = File(...)):
    image_bytes = await image.read()
    url = await db_service.upload_image(image_bytes, image.filename or "upload.jpg")
    return {"success": True, "image_url": url}

import sys
import os
import asyncio
import numpy as np
from PIL import Image, ImageDraw
import io

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.services.image_quality import check_image_quality
from backend.services.vision import analyze_crop_image
from backend.services.weather import fetch_weather_data
from backend.reasoning.evidence_engine import evaluate_context_evidence
from backend.services.advisory import get_advisory_for_condition
from backend.services.database import db_service

async def test_full_pipeline():
    print("--- 1. Testing Image Quality Checker ---")
    arr = np.random.randint(50, 200, (400, 400, 3), dtype=np.uint8)
    arr[:, :, 1] = np.clip(arr[:, :, 1] + 60, 0, 255)
    img = Image.fromarray(arr, mode="RGB")
    draw = ImageDraw.Draw(img)
    draw.ellipse([80, 80, 260, 260], fill=(120, 60, 20), outline=(40, 20, 10))
    draw.line([(200, 20), (200, 380)], fill=(30, 180, 30), width=5)

    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    img_bytes = buf.getvalue()

    q_res = check_image_quality(img_bytes)
    print(f"Quality Check Result: Acceptable={q_res['is_acceptable']}, Metrics={q_res['metrics']}")
    assert q_res['is_acceptable'] == True

    print("\n--- 2. Testing PyTorch Vision Inference ---")
    v_res = analyze_crop_image(img_bytes)
    print(f"Vision Top Class: {v_res['top_class']} (Prob: {v_res['top_probability']})")
    assert "probabilities" in v_res

    print("\n--- 3. Testing Open-Meteo Weather API ---")
    weather = await fetch_weather_data(12.9716, 77.5946)
    print(f"Weather Temp: {weather['temperature_c']} C, Humidity: {weather['humidity_percent']}%, Recent Rain: {weather['recent_rainfall_mm']}mm")
    assert "temperature_c" in weather

    print("\n--- 4. Testing Context Reasoning Engine (Initial Context) ---")
    field_obs_initial = {
        "crop": "Tomato",
        "growth_stage": "vegetative",
        "soil_condition": "dry",
        "irrigation": "normal",
        "pests": "no",
        "recent_rainfall": "low"
    }
    r_initial = evaluate_context_evidence(v_res, weather, field_obs_initial)
    print(f"Initial Assessment: {r_initial['final_assessment']} (Confidence: {r_initial['confidence_level']})")

    print("\n--- 5. Testing Context Reasoning Engine (USP Updated Context) ---")
    field_obs_updated = {
        "crop": "Tomato",
        "growth_stage": "vegetative",
        "soil_condition": "wet",
        "irrigation": "excessive",
        "pests": "yes",
        "recent_rainfall": "heavy"
    }
    r_updated = evaluate_context_evidence(v_res, weather, field_obs_updated)
    print(f"Updated Assessment: {r_updated['final_assessment']} (Confidence: {r_updated['confidence_level']})")

    print("\n--- 6. Testing Database Persistence ---")
    url = await db_service.upload_image(img_bytes, "test_leaf.jpg")
    saved = await db_service.save_analysis(
        crop="Tomato",
        image_url=url,
        final_assessment=r_updated["final_assessment"],
        confidence=r_updated["confidence_level"],
        is_uncertain=r_updated["is_uncertain"],
        visual_predictions=v_res,
        weather_data=weather,
        field_observations=field_obs_updated,
        evidence=r_updated,
        advisory=get_advisory_for_condition(r_updated["condition_key"])
    )
    print(f"Saved Record ID: {saved['analysis_id']}")
    history = await db_service.get_history(limit=5)
    print(f"History records count: {len(history)}")
    assert len(history) > 0

    print("\n[SUCCESS] ALL END-TO-END PIPELINE TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(test_full_pipeline())

from typing import Dict, Any, List
from backend.reasoning.rules import TOMATO_DISEASE_RULES

def evaluate_context_evidence(
    visual_predictions: Dict[str, float],
    weather_data: Dict[str, Any],
    field_obs: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Core CropSense Reasoning Engine.
    Combines Visual Model Probabilities + Real Weather + Field Observations.
    Distinguishes Visual Evidence vs Contextual Evidence.
    Applies explicit weighted agronomic rules to compute updated final scores.
    """
    raw_probs = visual_predictions.get("probabilities", {})
    temp = weather_data.get("temperature_c", 25.0)
    humidity = weather_data.get("humidity_percent", 60.0)
    recent_rain = weather_data.get("recent_rainfall_mm", 0.0)

    soil = field_obs.get("soil_condition", "normal").lower()       # dry, normal, wet
    irrigation = field_obs.get("irrigation", "normal").lower()    # none, normal, excessive
    pests = field_obs.get("pests", "no").lower()                  # yes, no, unsure
    growth_stage = field_obs.get("growth_stage", "vegetative").lower() # early, vegetative, flowering, fruiting
    rainfall_obs = field_obs.get("recent_rainfall", "moderate").lower() # low, moderate, heavy

    disease_scores = {}
    contextual_adjustments = {}
    evidence_explanations = {}

    for condition, rule in TOMATO_DISEASE_RULES.items():
        base_visual_prob = raw_probs.get(condition, 0.0)
        c_score = 0.0
        explanations = []

        c_weights = rule.get("context_weights", {})
        neg_weights = rule.get("negative_weights", {})
        env = rule.get("environmental_factors", {})

        # Weather Factors
        if "humidity_threshold" in env:
            thresh = env["humidity_threshold"]
            if humidity >= thresh:
                if condition == "Tomato___Leaf_Mold" and humidity >= 85.0:
                    c_score += c_weights.get("extreme_humidity", 0.30)
                    explanations.append(f"Extreme relative humidity ({humidity}%) strongly supports Leaf Mold development")
                elif condition == "Tomato___Late_blight":
                    c_score += c_weights.get("high_humidity", 0.25)
                    explanations.append(f"High relative humidity ({humidity}%) provides ideal moisture for Late Blight spores")
                elif condition == "Tomato___Early_blight":
                    c_score += c_weights.get("moderate_high_humidity", 0.20)
                    explanations.append(f"Elevated humidity ({humidity}%) favors Early Blight leaf wetness")
            elif humidity < 50.0:
                c_score += neg_weights.get("low_humidity", -0.25)
                explanations.append(f"Low relative humidity ({humidity}%) suppresses fungal spore germination")

        if "ideal_temp_range" in env:
            t_min, t_max = env["ideal_temp_range"]
            if t_min <= temp <= t_max:
                c_score += c_weights.get("favorable_temp", 0.15)
                explanations.append(f"Ambient temperature ({temp}°C) falls in prime growth range ({t_min}-{t_max}°C)")

        # Soil & Irrigation Factors
        if soil == "wet" or soil == "waterlogged":
            if "wet_soil" in c_weights:
                c_score += c_weights["wet_soil"]
                explanations.append("Wet/Waterlogged soil increases root/foliar moisture persistence")
            elif "wet_soil" in neg_weights:
                c_score += neg_weights["wet_soil"]

        elif soil == "dry":
            if "dry_soil" in c_weights:
                c_score += c_weights["dry_soil"]
                explanations.append("Dry soil condition supports healthy root environment")
            elif "dry_soil" in neg_weights:
                c_score += neg_weights["dry_soil"]

        if irrigation == "excessive":
            if "excessive_irrigation" in c_weights:
                c_score += c_weights["excessive_irrigation"]
                explanations.append("Excessive irrigation creates standing canopy moisture")
            elif "excessive_irrigation" in neg_weights:
                c_score += neg_weights["excessive_irrigation"]

        # Rainfall Observations
        if rainfall_obs == "heavy" or recent_rain > 10.0:
            if "heavy_rainfall_obs" in c_weights:
                c_score += c_weights["heavy_rainfall_obs"]
                explanations.append(f"Heavy rainfall ({recent_rain}mm recorded) facilitates fungal sporangia dispersal")
            elif "heavy_rainfall_obs" in neg_weights:
                c_score += neg_weights["heavy_rainfall_obs"]

        # Pests & Stage
        if pests == "yes" and "pests_observed" in c_weights:
            c_score += c_weights["pests_observed"]
            explanations.append("Observed pest damage creates entry wounds for leaf pathogens")
        elif pests == "no" and "no_pests" in c_weights:
            c_score += c_weights["no_pests"]
            explanations.append("Absence of insect pests minimizes secondary infections")

        if (growth_stage in ["flowering", "fruiting"]) and "flowering_fruiting_stage" in c_weights:
            c_score += c_weights["flowering_fruiting_stage"]
            explanations.append(f"Dense canopy during {growth_stage.capitalize()} stage reduces air circulation")

        contextual_adjustments[condition] = round(c_score, 4)
        evidence_explanations[condition] = explanations

        # Combine visual probability + contextual adjustment (weighted 65% visual, 35% context)
        final_unnorm = max(0.01, (base_visual_prob * 0.65) + (max(-0.4, c_score) * 0.35))
        disease_scores[condition] = final_unnorm

    # Normalize final posterior probabilities so they sum to 1.0
    total_score = sum(disease_scores.values())
    posterior_probs = {k: round(v / total_score, 4) for k, v in disease_scores.items()}

    # Determine top condition
    sorted_conditions = sorted(posterior_probs.items(), key=lambda x: x[1], reverse=True)
    top_condition, top_prob = sorted_conditions[0]
    second_condition, second_prob = sorted_conditions[1]

    # Visual top condition
    top_visual_class = visual_predictions.get("top_class", top_condition)
    top_visual_prob = raw_probs.get(top_visual_class, 0.0)

    # Uncertainty Check
    # If top visual prob < 0.30 or difference between top 2 posterior < 0.08 -> uncertain
    is_uncertain = False
    uncertainty_reason = None
    if top_prob < 0.32 or (top_prob - second_prob < 0.07):
        is_uncertain = True
        uncertainty_reason = "Model visual prediction and environmental context yielded close ambiguous scores between top conditions."

    # Map condition names to human readable titles
    condition_display_names = {
        "Tomato___healthy": "Tomato Healthy",
        "Tomato___Early_blight": "Tomato Early Blight",
        "Tomato___Late_blight": "Tomato Late Blight",
        "Tomato___Leaf_Mold": "Tomato Leaf Mold"
    }

    display_name = condition_display_names.get(top_condition, top_condition)

    # Confidence label
    if is_uncertain:
        confidence_level = "Uncertain"
    elif top_prob >= 0.70:
        confidence_level = "High"
    elif top_prob >= 0.45:
        confidence_level = "Moderate"
    else:
        confidence_level = "Low"

    # Assemble concise evidence points for UI
    visual_evidence_points = [
        f"EfficientNet-B0 visual model detected foliage symptoms matching {condition_display_names.get(top_visual_class, top_visual_class)} (Visual Prob: {top_visual_prob*100:.1f}%)"
    ]
    for c, p in raw_probs.items():
        if c != top_visual_class and p > 0.15:
            visual_evidence_points.append(f"Secondary visual signal for {condition_display_names.get(c, c)} ({p*100:.1f}%)")

    why_this_assessment = []
    why_this_assessment.append(f"Visual symptoms support {display_name} ({raw_probs.get(top_condition, 0)*100:.1f}% visual signal)")
    
    top_explanations = evidence_explanations.get(top_condition, [])
    if top_explanations:
        why_this_assessment.extend(top_explanations[:3])
    else:
        why_this_assessment.append("Environmental weather and soil conditions align with expected agronomic parameters")

    return {
        "final_assessment": display_name if not is_uncertain else "Assessment Uncertain",
        "condition_key": top_condition if not is_uncertain else "Uncertain",
        "confidence_level": confidence_level,
        "is_uncertain": is_uncertain,
        "uncertainty_reason": uncertainty_reason,
        "posterior_probabilities": posterior_probs,
        "visual_predictions": raw_probs,
        "contextual_adjustments": contextual_adjustments,
        "visual_evidence": visual_evidence_points,
        "why_this_assessment": why_this_assessment,
        "context_details": {
            "weather": weather_data,
            "field_observations": field_obs
        }
    }

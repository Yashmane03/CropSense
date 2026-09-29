"""
CropSense Transparent Context Rules Configuration for Tomato Health Assessment.
Contains scientifically grounded agronomic rules linking weather, soil, irrigation,
and pest observations to tomato diseases.
"""

TOMATO_DISEASE_RULES = {
    "Tomato___Late_blight": {
        "description": "Late Blight (Phytophthora infestans) is a water mold that thrives in cool, very wet, and humid weather.",
        "environmental_factors": {
            "humidity_threshold": 80.0,       # High humidity favorability
            "ideal_temp_range": (15.0, 24.0), # Cool to moderate temps
            "high_rainfall_mm": 10.0          # Heavy recent rainfall
        },
        "context_weights": {
            "high_humidity": 0.25,
            "favorable_temp": 0.15,
            "wet_soil": 0.20,
            "excessive_irrigation": 0.20,
            "heavy_rainfall_obs": 0.20
        },
        "negative_weights": {
            "dry_soil": -0.25,
            "low_humidity": -0.30
        }
    },
    "Tomato___Early_blight": {
        "description": "Early Blight (Alternaria solani) causes target-spot leaf lesions, favored by warm temperatures and alternating leaf wetness.",
        "environmental_factors": {
            "humidity_threshold": 65.0,
            "ideal_temp_range": (20.0, 30.0),
            "high_rainfall_mm": 5.0
        },
        "context_weights": {
            "moderate_high_humidity": 0.20,
            "favorable_temp": 0.20,
            "wet_soil": 0.15,
            "normal_or_excessive_irrigation": 0.15,
            "moderate_rainfall_obs": 0.15,
            "pests_observed": 0.15  # Wounds from insects facilitate fungal entry
        },
        "negative_weights": {
            "dry_soil": -0.15,
            "very_low_humidity": -0.20
        }
    },
    "Tomato___Leaf_Mold": {
        "description": "Leaf Mold (Passalora fulva) affects tomato foliage in humid conditions with limited airflow.",
        "environmental_factors": {
            "humidity_threshold": 85.0,
            "ideal_temp_range": (20.0, 28.0),
            "high_rainfall_mm": 5.0
        },
        "context_weights": {
            "extreme_humidity": 0.35,
            "favorable_temp": 0.15,
            "flowering_fruiting_stage": 0.15, # Dense canopy during later stages
            "wet_soil": 0.10
        },
        "negative_weights": {
            "low_humidity": -0.35
        }
    },
    "Tomato___healthy": {
        "description": "Healthy foliage with no active fungal or bacterial pathogens.",
        "context_weights": {
            "normal_soil": 0.25,
            "dry_soil": 0.15,
            "normal_irrigation": 0.25,
            "no_pests": 0.20,
            "moderate_humidity": 0.15
        },
        "negative_weights": {
            "wet_soil": -0.20,
            "excessive_irrigation": -0.25,
            "heavy_rainfall_obs": -0.20,
            "pests_observed": -0.20
        }
    }
}

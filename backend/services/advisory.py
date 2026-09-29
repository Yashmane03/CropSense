"""
Structured Advisory Module for CropSense Tomato Health Assessment.
Backing evidence-based cultural practices and crop management guidelines.
"""

TOMATO_ADVISORY_KNOWLEDGE_BASE = {
    "Tomato___healthy": {
        "condition": "Tomato Healthy",
        "monitoring": [
            "Inspect lower foliage weekly for early signs of leaf spots or yellowing.",
            "Monitor relative humidity levels, especially after rain events."
        ],
        "field_actions": [
            "Maintain drip irrigation or ground-level watering to keep foliage dry.",
            "Ensure proper plant spacing (45–60 cm) to maximize air circulation.",
            "Apply mulch around base to prevent soil splashing onto lower leaves."
        ],
        "escalation": [
            "If humidity remains >80% for consecutive days, increase crop canopy inspection frequency."
        ]
    },
    "Tomato___Early_blight": {
        "condition": "Tomato Early Blight",
        "monitoring": [
            "Look for concentric dark rings ('target spots') on older lower leaves.",
            "Track lesion spread up the plant canopy following rain or irrigation."
        ],
        "field_actions": [
            "Prune and remove infected lower leaves immediately; dispose far from crop field.",
            "Avoid overhead sprinkler irrigation; switch to drip lines to reduce leaf wetness duration.",
            "Sturdy staking/trellising to keep stems and foliage off moist soil."
        ],
        "escalation": [
            "If >15% of lower leaves show target lesions, consult local extension office for bio-fungicide copper spray application guidelines."
        ]
    },
    "Tomato___Late_blight": {
        "condition": "Tomato Late Blight",
        "monitoring": [
            "Check for pale green/dark water-soaked lesions with white moldy growth under leaves during humid mornings.",
            "Inspect stems and fruits for firm brown lesions."
        ],
        "field_actions": [
            "Immediately destroy and clear severely infected plant tissue.",
            "Halt overhead irrigation and improve drainage in waterlogged field zones.",
            "Disinfect pruning tools with 70% alcohol or bleach between plants."
        ],
        "escalation": [
            "Late Blight can rapidly destroy tomato fields within days under high humidity. Contact regional agricultural extension officer immediately."
        ]
    },
    "Tomato___Leaf_Mold": {
        "condition": "Tomato Leaf Mold",
        "monitoring": [
            "Examine upper leaf surfaces for pale green/yellow spots and lower surfaces for olive-green velvety mold.",
            "Monitor greenhouse or field humidity levels."
        ],
        "field_actions": [
            "Increase plant spacing and prune inner leaves to improve air circulation.",
            "Reduce greenhouse or microclimate humidity below 80% if under shade/cover.",
            "Keep foliage dry during evening hours."
        ],
        "escalation": [
            "If mold spreads across middle canopy, evaluate copper-based protective sprays as approved by local organic regulations."
        ]
    },
    "Uncertain": {
        "condition": "Assessment Uncertain",
        "monitoring": [
            "Take high-resolution, well-lit photos of individual leaves showing symptoms.",
            "Monitor if symptoms change or spread over the next 24-48 hours."
        ],
        "field_actions": [
            "Isolate suspected leaves and check for physical pest infestation.",
            "Ensure baseline crop hygiene (avoid leaf wetness, maintain balanced moisture)."
        ],
        "escalation": [
            "Submit high-quality sample to a local agricultural diagnostic laboratory or expert agronomist."
        ]
    }
}

def get_advisory_for_condition(condition_key: str) -> dict:
    """
    Returns advisory dict for a given condition key.
    """
    # Normalize condition key
    if "healthy" in condition_key.lower():
        key = "Tomato___healthy"
    elif "early" in condition_key.lower():
        key = "Tomato___Early_blight"
    elif "late" in condition_key.lower():
        key = "Tomato___Late_blight"
    elif "mold" in condition_key.lower():
        key = "Tomato___Leaf_Mold"
    else:
        key = "Uncertain"

    return TOMATO_ADVISORY_KNOWLEDGE_BASE.get(key, TOMATO_ADVISORY_KNOWLEDGE_BASE["Uncertain"])

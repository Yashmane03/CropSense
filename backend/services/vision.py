import io
from PIL import Image
import sys
import os

# Ensure ml package is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from ml.inference import TomatoClassifier

# Singleton classifier instance
_classifier_instance = None

def get_vision_classifier():
    global _classifier_instance
    if _classifier_instance is None:
        model_path = os.path.join("models", "tomato_efficientnet_b0.pth")
        class_names_path = os.path.join("models", "class_names.json")
        _classifier_instance = TomatoClassifier(model_path=model_path, class_names_path=class_names_path)
    return _classifier_instance

def analyze_crop_image(image_bytes: bytes) -> dict:
    """
    Passes image bytes through PyTorch EfficientNet-B0 tomato classifier.
    Returns visual prediction probabilities.
    """
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    classifier = get_vision_classifier()
    result = classifier.predict(image)
    return result

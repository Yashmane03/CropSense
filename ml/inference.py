import os
import json
from PIL import Image
import torch
import torch.nn.functional as F

from ml.model import get_tomato_model, DEFAULT_CLASS_NAMES
from ml.preprocessing import get_inference_transforms

class TomatoClassifier:
    """
    Inference class for CropSense Tomato Health Classifier.
    Loads trained .pth model weights and performs softmax prediction.
    """
    def __init__(self, model_path="models/tomato_efficientnet_b0.pth", class_names_path="models/class_names.json"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.transform = get_inference_transforms()
        
        # Load class names if present
        if os.path.exists(class_names_path):
            with open(class_names_path, "r") as f:
                self.class_names = json.load(f)
        else:
            self.class_names = DEFAULT_CLASS_NAMES

        # Initialize model architecture
        self.model = get_tomato_model(num_classes=len(self.class_names), pretrained=False)
        
        # Load weights if available
        if os.path.exists(model_path):
            state_dict = torch.load(model_path, map_location=self.device)
            self.model.load_state_dict(state_dict)
            print(f"[TomatoClassifier] Successfully loaded weights from {model_path}")
        else:
            print(f"[TomatoClassifier] Warning: Weights file {model_path} not found! Initialized with default architecture.")

        self.model.to(self.device)
        self.model.eval()

    def predict(self, image_input):
        """
        Runs inference on an image (PIL Image or file path).
        Returns dict containing top prediction, probabilities per class, and sorted predictions list.
        """
        if isinstance(image_input, str):
            image = Image.open(image_input).convert("RGB")
        elif isinstance(image_input, Image.Image):
            image = image_input.convert("RGB")
        else:
            raise ValueError("image_input must be PIL Image or file path string")

        tensor_img = self.transform(image).unsqueeze(0).to(self.device)

        with torch.no_grad():
            outputs = self.model(tensor_img)
            probabilities = F.softmax(outputs, dim=1)[0]

        prob_dict = {}
        predictions = []
        for i, prob in enumerate(probabilities):
            cls_name = self.class_names[i]
            val = round(prob.item(), 4)
            prob_dict[cls_name] = val
            predictions.append({"class_name": cls_name, "probability": val})

        predictions.sort(key=lambda x: x["probability"], reverse=True)
        top_pred = predictions[0]

        return {
            "top_class": top_pred["class_name"],
            "top_probability": top_pred["probability"],
            "probabilities": prob_dict,
            "predictions": predictions
        }

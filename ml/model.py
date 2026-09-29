import torch
import torch.nn as nn
from torchvision.models import efficientnet_b0, EfficientNet_B0_Weights

def get_tomato_model(num_classes=4, pretrained=True):
    """
    Returns an EfficientNet-B0 model fine-tuned for tomato leaf disease classification.
    Classes:
      0: Tomato___healthy
      1: Tomato___Early_blight
      2: Tomato___Late_blight
      3: Tomato___Leaf_Mold
    """
    weights = EfficientNet_B0_Weights.DEFAULT if pretrained else None
    model = efficientnet_b0(weights=weights)
    
    # EfficientNet classifier is a Sequential block with Dropout + Linear
    in_features = model.classifier[1].in_features
    model.classifier[1] = nn.Linear(in_features, num_classes)
    
    return model

DEFAULT_CLASS_NAMES = [
    "Tomato___healthy",
    "Tomato___Early_blight",
    "Tomato___Late_blight",
    "Tomato___Leaf_Mold"
]

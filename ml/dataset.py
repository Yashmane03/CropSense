import os
from PIL import Image, ImageDraw
import torch
from torch.utils.data import Dataset
from torchvision.datasets import ImageFolder

class TomatoDataset(Dataset):
    """
    Dataset wrapper for Tomato disease images.
    Supports ImageFolder layout:
      data_dir/
        Tomato___healthy/
        Tomato___Early_blight/
        Tomato___Late_blight/
        Tomato___Leaf_Mold/
    """
    def __init__(self, root_dir, transform=None):
        self.root_dir = root_dir
        self.transform = transform
        self.image_folder = ImageFolder(root=root_dir, transform=transform)
        self.classes = self.image_folder.classes
        self.class_to_idx = self.image_folder.class_to_idx

    def __len__(self):
        return len(self.image_folder)

    def __getitem__(self, idx):
        return self.image_folder[idx]

def create_sample_dataset(output_dir="data/tomato_sample", num_samples_per_class=10):
    """
    Utility function to create a minimal sample dataset for demonstration and automated testing
    if full PlantVillage dataset is not present.
    Creates realistic leaf-like patterns with class-specific synthetic visual cues.
    """
    os.makedirs(output_dir, exist_ok=True)
    classes = [
        "Tomato___healthy",
        "Tomato___Early_blight",
        "Tomato___Late_blight",
        "Tomato___Leaf_Mold"
    ]
    
    for cls in classes:
        cls_dir = os.path.join(output_dir, cls)
        os.makedirs(cls_dir, exist_ok=True)
        for i in range(num_samples_per_class):
            img_path = os.path.join(cls_dir, f"{cls}_{i+1}.jpg")
            if not os.path.exists(img_path):
                # Generate green leaf background
                img = Image.new("RGB", (256, 256), color=(45, 120, 45))
                draw = ImageDraw.Draw(img)
                
                # Add class specific synthetic markers for training sanity
                if cls == "Tomato___Early_blight":
                    # Concentric brown spots (target-like)
                    draw.ellipse([80, 80, 140, 140], fill=(100, 60, 20), outline=(50, 30, 10))
                    draw.ellipse([95, 95, 125, 125], fill=(70, 40, 15))
                elif cls == "Tomato___Late_blight":
                    # Large dark water-soaked lesions
                    draw.ellipse([60, 50, 170, 160], fill=(40, 45, 30), outline=(20, 25, 15))
                elif cls == "Tomato___Leaf_Mold":
                    # Pale yellow upper / olive brown lower patches
                    draw.ellipse([50, 60, 130, 140], fill=(180, 170, 60))
                else:
                    # Healthy leaf with bright green veins
                    draw.line([(128, 20), (128, 236)], fill=(70, 180, 70), width=4)
                    draw.line([(128, 100), (60, 50)], fill=(70, 180, 70), width=2)
                    draw.line([(128, 140), (196, 90)], fill=(70, 180, 70), width=2)

                img.save(img_path)
    print(f"Sample dataset generated at: {output_dir}")

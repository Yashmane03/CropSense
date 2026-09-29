import os
import json
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision.datasets import ImageFolder

from model import get_tomato_model
from preprocessing import get_inference_transforms

def evaluate_model(model_path="models/tomato_efficientnet_b0.pth", class_names_path="models/class_names.json", data_dir="data/tomato_dataset"):
    if not os.path.exists(model_path):
        print(f"Error: Model weights not found at {model_path}")
        return

    with open(class_names_path, "r") as f:
        class_names = json.load(f)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = get_tomato_model(num_classes=len(class_names), pretrained=False)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model = model.to(device)
    model.eval()

    val_tf = get_inference_transforms()
    dataset = ImageFolder(root=data_dir, transform=val_tf)
    loader = DataLoader(dataset, batch_size=16, shuffle=False)

    correct = 0
    total = 0
    class_correct = {c: 0 for c in class_names}
    class_total = {c: 0 for c in class_names}

    with torch.no_grad():
        for inputs, labels in loader:
            inputs = inputs.to(device)
            labels = labels.to(device)

            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)

            total += labels.size(0)
            correct += (preds == labels).sum().item()

            for i in range(labels.size(0)):
                label = labels[i].item()
                pred = preds[i].item()
                c_name = class_names[label]
                class_total[c_name] += 1
                if label == pred:
                    class_correct[c_name] += 1

    overall_acc = correct / total if total > 0 else 0
    print(f"\n--- Evaluation Results ---")
    print(f"Overall Accuracy: {overall_acc * 100:.2f}% ({correct}/{total})")
    print("Class-wise Accuracy:")
    for c in class_names:
        c_acc = (class_correct[c] / class_total[c] * 100) if class_total[c] > 0 else 0
        print(f"  - {c}: {c_acc:.2f}% ({class_correct[c]}/{class_total[c]})")

if __name__ == "__main__":
    evaluate_model()

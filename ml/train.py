import os
import json
import time
import argparse
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
from torchvision.datasets import ImageFolder

from model import get_tomato_model, DEFAULT_CLASS_NAMES
from preprocessing import get_train_transforms, get_inference_transforms
from dataset import create_sample_dataset

def train_model(data_dir="data/tomato_dataset", output_dir="models", epochs=5, batch_size=16, lr=0.001):
    os.makedirs(output_dir, exist_ok=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    if not os.path.exists(data_dir) or len(os.listdir(data_dir)) == 0:
        print(f"Data directory '{data_dir}' not found or empty. Generating sample dataset...")
        create_sample_dataset(output_dir=data_dir, num_samples_per_class=25)

    train_tf = get_train_transforms()
    val_tf = get_inference_transforms()

    # Load dataset
    full_dataset = ImageFolder(root=data_dir, transform=train_tf)
    class_names = full_dataset.classes
    print(f"Loaded {len(full_dataset)} images across classes: {class_names}")

    # Train / Val split (80% / 20%)
    val_size = max(1, int(len(full_dataset) * 0.2))
    train_size = len(full_dataset) - val_size
    train_ds, val_ds = random_split(full_dataset, [train_size, val_size])

    # Assign separate transform for val set
    val_dataset_clean = ImageFolder(root=data_dir, transform=val_tf)
    val_ds.dataset = val_dataset_clean

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False, num_workers=0)

    model = get_tomato_model(num_classes=len(class_names), pretrained=True)
    model = model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)

    best_acc = 0.0
    metrics_history = []

    start_time = time.time()
    print("Starting fine-tuning...")

    for epoch in range(epochs):
        # Training Phase
        model.train()
        running_loss = 0.0
        running_corrects = 0

        for inputs, labels in train_loader:
            inputs = inputs.to(device)
            labels = labels.to(device)

            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            _, preds = torch.max(outputs, 1)

            loss.backward()
            optimizer.step()

            running_loss += loss.item() * inputs.size(0)
            running_corrects += torch.sum(preds == labels.data)

        epoch_train_loss = running_loss / train_size
        epoch_train_acc = running_corrects.double().item() / train_size

        # Validation Phase
        model.eval()
        val_loss = 0.0
        val_corrects = 0

        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs = inputs.to(device)
                labels = labels.to(device)

                outputs = model(inputs)
                loss = criterion(outputs, labels)
                _, preds = torch.max(outputs, 1)

                val_loss += loss.item() * inputs.size(0)
                val_corrects += torch.sum(preds == labels.data)

        epoch_val_loss = val_loss / val_size
        epoch_val_acc = val_corrects.double().item() / val_size

        print(f"Epoch [{epoch+1}/{epochs}] | "
              f"Train Loss: {epoch_train_loss:.4f} Acc: {epoch_train_acc:.4f} | "
              f"Val Loss: {epoch_val_loss:.4f} Acc: {epoch_val_acc:.4f}")

        metrics_history.append({
            "epoch": epoch + 1,
            "train_loss": round(epoch_train_loss, 4),
            "train_acc": round(epoch_train_acc, 4),
            "val_loss": round(epoch_val_loss, 4),
            "val_acc": round(epoch_val_acc, 4)
        })

        if epoch_val_acc >= best_acc:
            best_acc = epoch_val_acc
            model_path = os.path.join(output_dir, "tomato_efficientnet_b0.pth")
            torch.save(model.state_dict(), model_path)
            print(f"--> Saved best model checkpoint to {model_path}")

    elapsed = time.time() - start_time
    print(f"Training completed in {elapsed:.2f}s. Best Val Accuracy: {best_acc:.4f}")

    # Save class names & metadata
    class_map_path = os.path.join(output_dir, "class_names.json")
    with open(class_map_path, "w") as f:
        json.dump(class_names, f, indent=2)

    metrics_path = os.path.join(output_dir, "metrics.json")
    with open(metrics_path, "w") as f:
        json.dump({
            "model_architecture": "EfficientNet-B0",
            "epochs": epochs,
            "best_val_acc": round(best_acc, 4),
            "training_time_sec": round(elapsed, 2),
            "classes": class_names,
            "history": metrics_history
        }, f, indent=2)

    print("All training artifacts saved successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train CropSense EfficientNet-B0 Tomato Model")
    parser.add_argument("--data_dir", type=str, default="data/tomato_dataset", help="Path to tomato dataset directory")
    parser.add_argument("--output_dir", type=str, default="models", help="Directory to save model artifacts")
    parser.add_argument("--epochs", type=int, default=5, help="Number of epochs")
    parser.add_argument("--batch_size", type=int, default=16, help="Batch size")
    parser.add_argument("--lr", type=float, default=0.001, help="Learning rate")
    args = parser.parse_args()

    train_model(data_dir=args.data_dir, output_dir=args.output_dir, epochs=args.epochs, batch_size=args.batch_size, lr=args.lr)

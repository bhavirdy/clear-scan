import torch
from torch import nn, optim
from sklearn.metrics import classification_report, confusion_matrix
import numpy as np
import os
import wandb
from torch.utils.data import DataLoader
from dataset import get_datasets
from model_utils import create_model

# Config
EPOCHS = [6, 4, 2]
LRS = [1e-3, 1e-4, 1e-5]
BATCH_SIZE = 16
NUM_CLASSES = 3
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class_names = ['normal', 'tb', 'pneumonia']

def eval_model(model, dataloader, device):
    criterion = nn.CrossEntropyLoss()
    model.eval()
    running_loss = 0
    correct = 0
    total = 0
    all_preds = []
    all_labels = []

    with torch.no_grad():
        for images, labels in dataloader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            loss = criterion(outputs, labels)
            running_loss += loss.item() * images.size(0)
            preds = outputs.argmax(dim=1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)

            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

    report = classification_report(all_labels, all_preds, target_names=class_names, output_dict=True)
    cm = confusion_matrix(all_labels, all_preds)
    return running_loss / total, correct / total, report, cm

def train_epoch(model, dataloader, optimizer, device):
    criterion = nn.CrossEntropyLoss()
    model.train()
    running_loss = 0
    correct = 0
    total = 0

    for images, labels in dataloader:
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item() * images.size(0)
        preds = outputs.argmax(dim=1)
        correct += (preds == labels).sum().item()
        total += labels.size(0)

    return running_loss / total, correct / total

def run_stage(model, train_loader, val_loader, epochs, lr, device, layers_to_unfreeze=None, wandb=None):
    from model_utils import set_trainable_layers

    set_trainable_layers(model, layers_to_unfreeze)
    trainable_params = [p for p in model.parameters() if p.requires_grad]
    if not trainable_params:
        raise ValueError("No parameters to optimize. Check your layer unfreezing!")

    optimizer = optim.Adam(trainable_params, lr=lr)

    for epoch in range(epochs):
        train_loss, train_acc = train_epoch(model, train_loader, optimizer, device)
        val_loss, val_acc, report, cm = eval_model(model, val_loader, device)

        avg_precision = np.mean([report[c]['precision'] for c in class_names])
        avg_recall = np.mean([report[c]['recall'] for c in class_names])
        avg_f1 = np.mean([report[c]['f1-score'] for c in class_names])

        if wandb:
            wandb.log({
                "train_loss": train_loss,
                "train_acc": train_acc,
                "val_loss": val_loss,
                "val_acc": val_acc,
                "precision": avg_precision,
                "recall": avg_recall,
                "f1": avg_f1
            })

        print(f"Epoch [{epoch+1}/{epochs}] | Train Acc: {train_acc:.4f} | Val Acc: {val_acc:.4f}")

def main():
    wandb.init(project="tb-pneumonia-xray", config={
        "epochs": EPOCHS,
        "learning_rates": LRS,
        "batch_size": BATCH_SIZE,
        "num_classes": NUM_CLASSES
    })

    train_dataset, val_dataset, _ = get_datasets()
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=4)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=4)

    model = create_model(NUM_CLASSES, DEVICE)

    print("Stage 1: Training classifier head only...")
    run_stage(model, train_loader, val_loader, EPOCHS[0], LRS[0], DEVICE, layers_to_unfreeze=["classifier"], wandb=wandb)

    print("Stage 2: Unfreezing last dense block + classifier...")
    run_stage(model, train_loader, val_loader, EPOCHS[1], LRS[1], DEVICE, layers_to_unfreeze=["features.denseblock4", "features.norm5", "classifier"], wandb=wandb)

    print("Stage 3: Unfreezing entire network...")
    run_stage(model, train_loader, val_loader, EPOCHS[2], LRS[2], DEVICE, layers_to_unfreeze=None, wandb=wandb)

    os.makedirs("models", exist_ok=True)
    torch.save(model.state_dict(), "models/densenet_tb_pneumonia.pt")
    print("Model saved.")

    wandb.finish()

if __name__ == "__main__":
    main()

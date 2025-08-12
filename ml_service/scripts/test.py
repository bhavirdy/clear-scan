import torch
from torch.utils.data import DataLoader
from sklearn.metrics import classification_report, confusion_matrix
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from dataset import get_datasets
from model_utils import create_model

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
NUM_CLASSES = 3
class_names = ['normal', 'pneumonia', 'tb']

def evaluate_test(model, test_loader):
    model.eval()
    all_preds = []
    all_labels = []

    with torch.no_grad():
        for images, labels in test_loader:
            images, labels = images.to(DEVICE), labels.to(DEVICE)
            outputs = model(images)
            preds = outputs.argmax(dim=1)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

    print(classification_report(all_labels, all_preds, target_names=class_names))
    cm = confusion_matrix(all_labels, all_preds)
    plt.figure(figsize=(6,6))
    sns.heatmap(cm, annot=True, fmt="d", xticklabels=class_names, yticklabels=class_names, cmap="Blues")
    plt.xlabel("Predicted")
    plt.ylabel("True")
    plt.title("Confusion Matrix")
    plt.show()

def main():
    _, _, test_dataset = get_datasets()
    test_loader = DataLoader(test_dataset, batch_size=16, shuffle=False)

    model = create_model(NUM_CLASSES, DEVICE)
    model.load_state_dict(torch.load("models/densenet_tb_pneumonia.pt", map_location=DEVICE))
    model.to(DEVICE)

    evaluate_test(model, test_loader)

if __name__ == "__main__":
    main()

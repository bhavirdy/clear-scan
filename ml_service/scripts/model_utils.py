import torch
from torchvision.models import densenet121, DenseNet121_Weights
from torch import nn

def set_trainable_layers(model, layers_to_unfreeze):
    if layers_to_unfreeze is None:
        for param in model.parameters():
            param.requires_grad = True
        return

    for name, param in model.named_parameters():
        param.requires_grad = False
        if any(layer in name for layer in layers_to_unfreeze):
            param.requires_grad = True

def create_model(num_classes=3, device=torch.device("cpu")):
    model = densenet121(weights=DenseNet121_Weights.DEFAULT)
    # Freeze all params initially
    for param in model.parameters():
        param.requires_grad = False
    # Replace classifier head
    num_features = model.classifier.in_features
    model.classifier = nn.Linear(num_features, num_classes)
    model = model.to(device)
    return model

from torchvision import transforms
from torchvision.datasets import ImageFolder

def get_datasets(data_dir="data"):
    train_transforms = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomRotation(degrees=7),
        transforms.ColorJitter(brightness=0.1, contrast=0.1),
        transforms.RandomResizedCrop(224, scale=(0.9, 1.0)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225])
    ])

    val_test_transforms = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225])
    ])

    train_dataset = ImageFolder(root=f"{data_dir}/merged_dataset/train", transform=train_transforms)
    val_dataset = ImageFolder(root=f"{data_dir}/merged_dataset/val", transform=val_test_transforms)
    test_dataset = ImageFolder(root=f"{data_dir}/merged_dataset/test", transform=val_test_transforms)

    return train_dataset, val_dataset, test_dataset

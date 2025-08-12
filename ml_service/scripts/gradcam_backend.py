import os
import torch
from torchvision import transforms, models
from torchcam.methods import GradCAM
from torchcam.utils import overlay_mask
from PIL import Image

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
MODEL_PATH = "models/tb_pneumonia_model.pth"
CLASS_NAMES = ["normal", "tb", "pneumonia"]

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.Grayscale(num_output_channels=3),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

model = models.densenet121(pretrained=True)
model.classifier = torch.nn.Linear(model.classifier.in_features, len(CLASS_NAMES))
model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
model = model.to(DEVICE)
model.eval()

cam_extractor = GradCAM(model, target_layer='features.denseblock4')

def process_image(img_path):
    img = Image.open(img_path).convert('RGB')
    input_tensor = transform(img).unsqueeze(0).to(DEVICE)

    output = model(input_tensor)
    pred_class = output.argmax(dim=1).item()

    activation_map = cam_extractor(pred_class, output)
    heatmap = Image.fromarray(activation_map[0].cpu().numpy())

    result = overlay_mask(img, heatmap, alpha=0.5)

    gradcam_dir = "../gradcams"
    os.makedirs(gradcam_dir, exist_ok=True)
    gradcam_path = os.path.join(gradcam_dir, os.path.basename(img_path) + "_gradcam.png")
    result.save(gradcam_path)

    return CLASS_NAMES[pred_class], gradcam_path

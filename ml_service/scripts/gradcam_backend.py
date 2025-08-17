import os
import torch
from torchvision import transforms, models
from torchcam.methods import GradCAM
from torchcam.utils import overlay_mask
from PIL import Image

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
MODEL_PATH = "models/densenet_tb_pneumonia.pt"
CLASS_NAMES = ["normal", "pneumonia", "tb"]
CONFIDENCE_THRESHOLD = 0.7  # Threshold for valid predictions

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.Grayscale(num_output_channels=3),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

# Load model
model = models.densenet121()
model.classifier = torch.nn.Linear(model.classifier.in_features, len(CLASS_NAMES))
model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
model = model.to(DEVICE)
model.eval()

# Initialize GradCAM
cam_extractor = GradCAM(model, target_layer='features.norm5')

def process_image(img_path):
    # Load and preprocess image
    img = Image.open(img_path).convert('RGB')
    input_tensor = transform(img).unsqueeze(0).to(DEVICE)
    input_tensor.requires_grad_(True)
    
    # Forward pass
    with torch.set_grad_enabled(True):
        output = model(input_tensor)
    
    pred_class = output.argmax(dim=1).item()
    confidence = torch.softmax(output, dim=1)[0][pred_class].item()
    
    # Check confidence threshold
    if confidence < CONFIDENCE_THRESHOLD:
        print(f"⚠️  Low confidence prediction: {confidence:.3f}")
        print(f"    This may not be a valid chest X-ray image.")
        return "INVALID_INPUT", confidence, None
    
    # Generate activation map
    activation_maps = cam_extractor(pred_class, output)
    activation_map = activation_maps[0].squeeze().cpu()
    
    # Create GradCAM overlay
    result = overlay_mask(img, Image.fromarray(activation_map.numpy()), alpha=0.4)
    
    # Save result
    gradcam_dir = "gradcams"
    os.makedirs(gradcam_dir, exist_ok=True)
    gradcam_path = os.path.join(
        gradcam_dir, os.path.basename(img_path) + "_gradcam.png"
    )
    result.save(gradcam_path)
    
    return CLASS_NAMES[pred_class], confidence, gradcam_path

if __name__ == "__main__":
    # testing preds
    # img_path = "uploads/CHNCXR_0327_1.png" # tb
    # img_path = "uploads/person1_bacteria_1.jpeg" # pneumonia
    # img_path = "uploads/CHNCXR_0001_0.png" # normal
    img_path = "uploads/radiologist.jpeg"
    
    try:
        pred_label, confidence, gradcam_path = process_image(img_path)
        
        if pred_label != "INVALID_INPUT":
            print(f"✅ Prediction: {pred_label} ({confidence:.3f})")
            print(f"🔥 GradCAM saved to: {gradcam_path}")
        
    except Exception as e:
        print(f"❌ Error running GradCAM: {e}")
        import traceback
        traceback.print_exc()
import torch
from torchvision import models, transforms
from PIL import Image

# Load a pre-trained ResNet model
model = models.resnet50(pretrained=True)
model.eval()

# Define image transformations
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

def extract_features(image_path):
    """
    Extract features from an image using a pre-trained ResNet model.
    """
    image = Image.open(image_path)
    image = transform(image).unsqueeze(0)  # Add batch dimension
    with torch.no_grad():
        features = model(image)
    return features.squeeze().numpy()  # Convert to numpy array

import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms, models
from PIL import Image
import os

# =========================
# Labels (same as training)
# =========================
crops = ["banana", "mango", "papaya", "tomato"]
stages = ["unripe", "semiripe", "ripe"]

# =========================
# Device
# =========================
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Using device:", device)

# =========================
# Image Transform
# =========================
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

# =========================
# Model Architecture
# =========================
base_model = models.resnet18(
    weights=models.ResNet18_Weights.IMAGENET1K_V1
)
num_ftrs = base_model.fc.in_features


class MultiOutputModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.shared = nn.Sequential(*list(base_model.children())[:-1])
        self.crop_head = nn.Linear(num_ftrs, len(crops))
        self.stage_head = nn.Linear(num_ftrs, len(stages))

    def forward(self, x):
        x = self.shared(x)
        x = x.view(x.size(0), -1)
        crop_output = self.crop_head(x)
        stage_output = self.stage_head(x)
        return crop_output, stage_output


# =========================
# Load Model (FIXED PATH)
# =========================
MODEL_PATH = os.path.join(os.path.dirname(__file__), "ripeness_model.pth")

model = MultiOutputModel().to(device)
model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
model.eval()

print("Model loaded successfully.")

# =====================================================
# PIPELINE-SAFE FUNCTION (THIS IS WHAT YOU WILL USE)
# =====================================================
def predict_image(image_path: str):
    """
    Pipeline-safe function.
    Takes image path and returns crop + stage + confidence.
    """

    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    image = Image.open(image_path).convert("RGB")
    image_tensor = transform(image).unsqueeze(0).to(device)

    with torch.no_grad():
        outputs_crop, outputs_stage = model(image_tensor)

        crop_probs = F.softmax(outputs_crop, dim=1)
        stage_probs = F.softmax(outputs_stage, dim=1)

        crop_idx = crop_probs.argmax(dim=1).item()
        stage_idx = stage_probs.argmax(dim=1).item()

    return {
        "crop": crops[crop_idx],
        "stage": stages[stage_idx],
        "crop_confidence": round(crop_probs[0][crop_idx].item() * 100, 2),
        "stage_confidence": round(stage_probs[0][stage_idx].item() * 100, 2)
    }

# =====================================================
# CLI MODE (ONLY RUNS WHEN FILE IS EXECUTED DIRECTLY)
# =====================================================
if __name__ == "__main__":

    image_path = input("Enter full image path: ").strip()

    if not os.path.isfile(image_path):
        print("Error: File not found at the given path.")
    else:
        result = predict_image(image_path)

        crop_name = result["crop"]
        stage_name = result["stage"]
        crop_conf = result["crop_confidence"]
        stage_conf = result["stage_confidence"]

        print(f"Your crop is : {crop_name} ({crop_conf:.2f}% confidence)")
        print(f"Your {crop_name} is in this stage : {stage_name} ({stage_conf:.2f}% confidence)")

        # Save output for next module (optional)
        with open("abhi_output_for_karan.txt", "w") as f:
            f.write(f"crop : {crop_name} ({crop_conf:.2f}%)\n")
            f.write(f"stage : {stage_name} ({stage_conf:.2f}%)\n")

        print("Saved output for Karan in abhi_output_for_karan.txt")

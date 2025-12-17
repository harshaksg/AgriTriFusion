# 🌱 AgriTriFusion

AgriTriFusion is an intelligent agriculture decision-support system that integrates **computer vision** and **machine learning** to assist farmers with **crop ripeness detection, fertilizer recommendation, and harvest prediction**.

The system is designed as a modular pipeline where each component can work independently or as part of a unified dashboard.

---

## 🚀 Features

### 1️⃣ Crop & Ripening Stage Detection (Image-Based)
- Upload an image of the crop
- Deep Learning (ResNet-based CNN) predicts:
  - Crop type (Tomato, Banana, Mango, Papaya)
  - Ripening stage (Unripe, Semiripe, Ripe)

---

### 2️⃣ Fertilizer Recommendation (ML + Rule-Based)
- Uses:
  - Output from crop detection (crop name, stage)
  - Manual soil inputs (N, P, K values)
- Powered by:
  - XGBoost models for nutrient priority
  - Rule engine for fertilizer selection
- Outputs:
  - Primary fertilizer (major deficiency)
  - Secondary fertilizer (if applicable)
  - Action (Increase / Normal / OK)
  - Farmer-friendly recommendation message

---

### 3️⃣ Harvest Prediction (Image-Aware)
- Depends on crop & ripening stage
- Uses **sub-stage detection**:
  - Early / Mid / Late
- Image features used:
  - Color (Hue distribution)
  - Texture (Laplacian variance)
- Outputs:
  - Harvest window (Earliest – Expected – Latest)
  - Harvest dates

---

### 4️⃣ Yield Estimation (Independent Module)
- Does NOT depend on image input
- Based on manual agronomic inputs:
  - Crop type
  - Area cultivated
  - Number of plants
  - Soil type & pH
  - Irrigation method
- Outputs:
  - Estimated total yield
  - Yield per hectare
  - Yield range

---

## 🧠 System Architecture

Image Upload
↓
Crop & Ripening Detection (CNN)
↓
Fertilizer Recommendation (XGBoost + Rules)
↓
Harvest Prediction (Sub-stage Analysis)

Yield Estimation runs **independently** via manual inputs.

---

## 🖥️ Tech Stack

- Python 3.10+
- PyTorch (CNN model)
- XGBoost
- Scikit-learn
- OpenCV
- Streamlit (Dashboard)
- Joblib (Model persistence)

---

## 📁 Project Structure

AgriTriFusion/
│
├── app.py # Streamlit dashboard
│
├── modules/
│ ├── stage_detection/
│ │ ├── abhi_predict.py
│ │ └── ripeness_model.pth
│ │
│ ├── fertilizer_reco/
│ │ ├── fert_reco.py
│ │ ├── fertilizer_rule_engine.py
│ │ └── saved_models/
│ │ ├── fertilizer_preprocessor.joblib
│ │ └── nutrient_priority_models.joblib
│ │
│ ├── harvest_prediction/
│ │ └── harvest_predictor.py
│
├── assets/
│ └── sample images
│
├── utils/
│ └── integration.py
│
└── README.md


---

## ▶️ How to Run

### 1️⃣ Create virtual environment
```bash
python -m venv .venv

2️⃣ Activate environment
# Windows
.venv\Scripts\activate

# Linux / Mac
source .venv/bin/activate

3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ Run Streamlit app
streamlit run app.py


---

# ✅ Git Commands (Full Commit)

Run these **exact commands** from your project root:

```bash
git status
import streamlit as st
from PIL import Image
import tempfile
import os
from datetime import datetime

# === IMPORTS ===
from modules.stage_detection.abhi_predict import predict_image
from modules.fertilizer_reco.fert_reco import recommend_fertilizer
from modules.harvest_prediction.harvest_predictor import HarvestPredictor

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(
    page_title="AgriTriFusion",
    page_icon="🌿",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS for clean look
st.markdown("""
<style>
    .main-header {font-size: 3.5rem; font-weight: bold; text-align: center;
        background: linear-gradient(90deg, #1e3c72, #2a5298);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.5rem;}
    .subtitle {text-align: center; font-size: 1.3rem; color: #555; margin-bottom: 2rem;}
    .stButton>button {background-color: #228B22; color: white; font-size: 1.2rem;
        height: 3em; width: 100%; border-radius: 10px; border: none; box-shadow: 0 4px 8px rgba(0,0,0,0.2);}
    .stButton>button:hover {background-color: #1e6f1e; transform: scale(1.05); transition: all 0.3s;}
    .result-card {padding: 1.5rem; border-radius: 15px; background-color: #f8fff8;
        border-left: 6px solid #228B22; box-shadow: 0 4px 12px rgba(0,0,0,0.1); margin-bottom: 1rem;}
    .npk-label {font-size: 1.1rem; font-weight: bold; color: #333; margin-bottom: 0.5rem;}
    .npk-container {padding: 1rem; background-color: #f8fff8; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);}
</style>
""", unsafe_allow_html=True)

# HEADER
st.markdown('<div class="main-header">🌱 AgriTriFusion</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI-Powered Crop Intelligence: Detect • Recommend • Predict • Estimate</div>', unsafe_allow_html=True)

# TABS
tab1, tab2 = st.tabs(["📸 Image-Based Full Analysis", "🌾 Yield Estimation (Manual)"])

# =============================================
# TAB 1: IMAGE-BASED FULL ANALYSIS (WITH YOUR DESIRED NPK UI)
# =============================================
with tab1:
    st.markdown("### 1. Upload Crop Image")
    uploaded_file = st.file_uploader("Drag & drop or browse JPG, PNG", type=["jpg", "jpeg", "png"], key="image_upload")

    if uploaded_file is not None:
        image = Image.open(uploaded_file).convert("RGB")
        st.image(image, caption="Uploaded Image", use_column_width=True)
        st.success("Image uploaded successfully")

        # Save temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            image.save(tmp.name)
            temp_path = tmp.name

        # 2. NPK Input Section - exactly like your screenshot
        st.markdown("### 2. Enter Soil Nutrients (NPK)")
        with st.container():
            st.markdown('<div class="npk-container">', unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown('<p class="npk-label">Nitrogen (N) mg/kg</p>', unsafe_allow_html=True)
                N = st.number_input("", min_value=0.0, max_value=500.0, value=4.0, step=0.1, key="npk_n", label_visibility="collapsed")

            with col2:
                st.markdown('<p class="npk-label">Phosphorus (P) mg/kg</p>', unsafe_allow_html=True)
                P = st.number_input("", min_value=0.0, max_value=500.0, value=2.0, step=0.1, key="npk_p", label_visibility="collapsed")

            with col3:
                st.markdown('<p class="npk-label">Potassium (K) mg/kg</p>', unsafe_allow_html=True)
                K = st.number_input("", min_value=0.0, max_value=500.0, value=3.0, step=0.1, key="npk_k", label_visibility="collapsed")

            st.markdown('</div>', unsafe_allow_html=True)

        # Analyze Button
        if st.button("🔍 Analyze Crop", type="primary", use_container_width=True):
            with st.spinner("Analyzing image and soil nutrients..."):
                try:
                    # Step 1: Detect crop & stage
                    abhi_result = predict_image(temp_path)
                    crop = abhi_result["crop"]
                    stage = abhi_result["stage"]

                    # Step 2: Fertilizer using detected crop/stage + manual NPK
                    fert_result = recommend_fertilizer(
                        crop=crop,
                        stage=stage,
                        N_mgkg=N,
                        P_mgkg=P,
                        K_mgkg=K
                    )

                    # Step 3: Harvest prediction
                    predictor = HarvestPredictor()
                    harvest_result = predictor.predict(temp_path, crop, stage)

                    # Save results
                    st.session_state.results = {
                        "crop": crop.capitalize(),
                        "stage": stage.capitalize(),
                        "crop_conf": abhi_result["crop_confidence"],
                        "stage_conf": abhi_result["stage_confidence"],
                        "fertilizer": fert_result,
                        "harvest": harvest_result
                    }

                    st.success("✅ Full analysis complete!")

                except Exception as e:
                    st.error(f"⚠️ Error: {str(e)}")

        # Clean up temp file
        if 'image_path' in st.session_state and st.session_state.image_path != temp_path:
            if os.path.exists(st.session_state.image_path):
                os.unlink(st.session_state.image_path)
        st.session_state.image_path = temp_path

    else:
        st.info("Upload an image to start analysis")

    # Show results
    if 'results' in st.session_state and st.session_state.results:
        res = st.session_state.results
        st.markdown("---")
        st.markdown("### 🎯 Analysis Results")

        # Crop & Stage
        with st.container():
            st.markdown('<div class="result-card">', unsafe_allow_html=True)
            cols = st.columns(2)
            cols[0].metric("🌾 Detected Crop", res["crop"], f"{res['crop_conf']}% confidence")
            cols[1].metric("🍃 Ripening Stage", res["stage"], f"{res['stage_conf']}% confidence")
            st.markdown('</div>', unsafe_allow_html=True)

        # Fertilizer Recommendations
        st.markdown("### 🧪 Fertilizer Recommendations")
        col1, col2 = st.columns(2)

        primary = res["fertilizer"].get("primary")
        secondary = res["fertilizer"].get("secondary")

        with col1:
            st.markdown("#### 🟢 Primary (Most Urgent)")
            if primary:
                st.write(f"**Function:** {primary.get('fertilizer_type', 'N/A').capitalize()}")
                st.write(f"**Recommended:** {primary['fertilizer_name']}")
                st.write(f"**Dose:** {primary['dose_kg_acre']} kg/acre")
                st.success(primary["message"])
            else:
                st.success("✅ No major nutrient deficiency detected.")

        with col2:
            st.markdown("#### 🟡 Secondary (If Needed)")
            if secondary:
                st.write(f"**Function:** {secondary.get('fertilizer_type', 'N/A').capitalize()}")
                st.write(f"**Recommended:** {secondary['fertilizer_name']}")
                st.write(f"**Dose:** {secondary['dose_kg_acre']} kg/acre")
                st.info(secondary["message"])
            else:
                st.info("✅ Other nutrients are sufficient.")

        # Harvest Prediction
        st.markdown("### 📅 Harvest Prediction")
        harvest = res["harvest"]
        days = harvest["harvest_window_days"]
        dates = harvest["harvest_window_dates"]
        st.markdown(f"**Sub-Stage:** {harvest['sub_stage'].upper()}")
        c1, c2, c3 = st.columns(3)
        c1.metric("Earliest", f"{days['earliest']} days", dates["earliest"])
        c2.metric("Expected", f"{days['expected']} days", dates["expected"])
        c3.metric("Latest", f"{days['latest']} days", dates["latest"])

        # Clean up
        if os.path.exists(st.session_state.image_path):
            os.unlink(st.session_state.image_path)

# =============================================
# TAB 2: YIELD ESTIMATION (MANUAL) - unchanged
# =============================================
with tab2:
    st.markdown("### 🌾 Yield Estimation – Manual Input")
    st.info("No image needed! Just enter your field details for accurate yield prediction.")

    col1, col2 = st.columns(2)
    with col1:
        crop = st.selectbox("🌱 Crop Type *", ["tomato", "banana", "mango", "papaya"], help="Select your crop")
        area_acres = st.number_input("📏 Cultivated Area (acres) *", min_value=0.1, value=1.0, step=0.5)
        num_plants = st.number_input("🌿 Number of Plants/Seeds *", min_value=1, value=5000, step=100)

    with col2:
        soil_type = st.selectbox("🪴 Soil Type *", ["Loamy", "Black", "Red", "Clay", "Sandy"])
        soil_ph = st.number_input("⚗️ Soil pH *", min_value=0.0, max_value=14.0, value=6.5, step=0.1)
        irrigation = st.selectbox("💧 Irrigation Type *", ["Drip", "Sprinkler", "Flood", "Rain-fed"])

    st.markdown("#### Optional (for better accuracy)")
    col3, col4 = st.columns(2)
    with col3:
        fertilizer_level = st.select_slider("🧴 Fertilizer Practice", options=["Low", "Medium", "High"], value="Medium")
    with col4:
        avg_temp = st.number_input("🌡️ Average Temperature (°C)", min_value=10.0, max_value=50.0, value=28.0)

    if st.button("📊 ESTIMATE YIELD NOW", type="primary", use_container_width=True):
        with st.spinner("Calculating yield..."):
            BASE_YIELD_TONS_ACRE = {"tomato": 26.3, "banana": 16.2, "mango": 6.1, "papaya": 20.2}

            ph_factor = 1.0 if 6.0 <= soil_ph <= 7.0 else 0.9 if 5.5 <= soil_ph <= 7.5 else 0.75
            soil_factor = {"Loamy": 1.0, "Black": 0.98, "Red": 0.92, "Clay": 0.88, "Sandy": 0.80}.get(soil_type, 0.85)
            irr_factor = {"Drip": 1.1, "Sprinkler": 1.0, "Flood": 0.9, "Rain-fed": 0.75}.get(irrigation, 0.9)
            fert_factor = {"Low": 0.8, "Medium": 1.0, "High": 1.15}.get(fertilizer_level, 1.0)
            temp_factor = 1.0 if 20 <= avg_temp <= 32 else 0.9 if 15 <= avg_temp <= 35 else 0.75

            optimal_plants_per_acre = {"tomato": 10000, "banana": 700, "mango": 40, "papaya": 2000}
            optimal = optimal_plants_per_acre.get(crop, 5000)
            density_ratio = num_plants / (area_acres * optimal)
            density_factor = min(1.15, max(0.7, density_ratio))

            base_yield = BASE_YIELD_TONS_ACRE[crop]
            estimated_tons = base_yield * area_acres * ph_factor * soil_factor * irr_factor * fert_factor * temp_factor * density_factor
            min_tons = estimated_tons * 0.85
            max_tons = estimated_tons * 1.15
            estimated_kg = estimated_tons * 1000

            st.markdown("### 📈 Estimated Yield Results")
            st.markdown('<div class="result-card">', unsafe_allow_html=True)

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Yield", f"{estimated_kg:,.0f} kg", f"{estimated_tons:.1f} tons")
            c2.metric("Per Acre", f"{estimated_tons/area_acres:.1f} tons", f"{(estimated_kg / area_acres):,.0f} kg")
            c3.metric("Min Expected", f"{min_tons:.1f} tons")
            c4.metric("Max Expected", f"{max_tons:.1f} tons")

            st.markdown(f"**Yield influenced by:** Optimal pH, {soil_type.lower()} soil, {irrigation.lower()} irrigation, and good plant density.")
            st.markdown('</div>', unsafe_allow_html=True)
            st.success("Yield estimation complete!")

# Footer
st.markdown("---")
st.caption("PROJECT BATCH 24")
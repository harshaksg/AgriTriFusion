import streamlit as st
from PIL import Image
import matplotlib.pyplot as plt

from utils.integration import predict_stage_mock, fertilizer_mock, yield_mock, load_fertilizer_rules
from utils.preprocess import preprocess_image_pil, quality_check

st.set_page_config(page_title='AgriTriFusion', layout='wide')

st.title('AgriTriFusion — Growth Stage → Fertilizer → Yield')
st.markdown('Upload a crop image to run the demo pipeline (using placeholder models).')

rules = load_fertilizer_rules()

with st.sidebar:
    st.header('Fertilizer Rules (loaded)')
    if rules:
        for crop, crop_rules in rules.items():
            st.subheader(crop)
            for stage, r in crop_rules.items():
                st.markdown(f"**{stage}**: {r.get('recommended_fertilizer')} — {r.get('dose')}  \n{r.get('reason')}")
    else:
        st.info('No fertilizer_rules.csv found. Place it in modules/fertilizer_reco/ to display rules.')

col1, col2 = st.columns([1,2])

with col1:
    uploaded = st.file_uploader('Upload image', type=['jpg','jpeg','png'])
    run_button = st.button('Run Pipeline (demo)')

with col2:
    st.header('Results')
    stage_box = st.empty()
    fert_box = st.empty()
    yield_box = st.empty()
    chart_box = st.empty()

def stage_badge(stage):
    if stage == 'Unripe':
        color = '#FFD54F'
    elif stage == 'Semi-Ripe':
        color = '#FFB74D'
    else:
        color = '#81C784'
    return f"<div style='display:inline-block;padding:6px 10px;background:{color};border-radius:6px'>{stage}</div>"

if run_button:
    if not uploaded:
        st.warning('Please upload an image first.')
    else:
        try:
            image = Image.open(uploaded).convert('RGB')
            st.image(image, caption='Uploaded image', use_column_width=True)
            if not quality_check(image):
                st.warning('Image seems small. Try a higher-resolution image for better results.')
            stage_out = predict_stage_mock(image)
            stage_html = stage_badge(stage_out.get('stage','Unknown'))
            stage_box.markdown(f"**Stage:** {stage_html}<br>**Crop:** {stage_out.get('crop')}<br>**Confidence:** {stage_out.get('confidence')}", unsafe_allow_html=True)
            fert_out = fertilizer_mock(stage_out, rules)
            fert_box.markdown(f"**Fertilizer:** {fert_out.get('fertilizer')}  \n**Dose:** {fert_out.get('dose')}  \n**Reason:** {fert_out.get('reason')}")
            yield_out = yield_mock(fert_out)
            yield_box.markdown(f"**Predicted Yield:** {yield_out.get('yield')}  \n**Days to Harvest:** {yield_out.get('days_left')}")
            days = [0, int(yield_out.get('days_left'))//2, int(yield_out.get('days_left'))]
            base_yield = float(str(yield_out.get('yield')).split()[0]) if yield_out.get('yield') else 9.0
            y_values = [base_yield*0.6, base_yield*0.85, base_yield]
            fig, ax = plt.subplots()
            ax.plot(days, y_values, marker='o')
            ax.set_title('Projected Yield Progression (mock)')
            ax.set_xlabel('Days from now')
            ax.set_ylabel('Yield (tons/acre)')
            chart_box.pyplot(fig)
        except Exception as e:
            st.error(f'Error running pipeline: {e}')

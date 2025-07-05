import pandas as pd
import numpy as np
import joblib
import streamlit as st
import os
import gdown

model_path = "pollution_model.pkl"
if not os.path.exists(model_path):
    url = "https://drive.google.com/uc?id=1AbCdeFgHIJKlmNoPQR"
    gdown.download(url, model_path, quiet=False)

model = joblib.load(model_path)
model_cols = joblib.load("model_columns.pkl")

st.set_page_config(page_title="Water Pollution Predictor", layout="centered")

st.markdown(
    """
    <style>
    .centered-title {
        text-align: center;
        color: #1f77b4;
        font-size: 3em;
        font-weight: bold;
        margin-bottom: 0.2em;
    }
    .centered-subtitle {
        text-align: center;
        font-size: 1.2em;
        color: #FFFF;
        margin-bottom: 1em;
    }
    </style>
    <div class="centered-title">💧 Water Pollution Predictor</div>
    <div class="centered-subtitle">Enter a year and station ID to predict pollution levels and assess water quality.</div>
    """,
    unsafe_allow_html=True,
)
st.markdown("---")

st.markdown("### 📊 Input Parameters")

col1, col2 = st.columns(2)
year_input = col1.number_input("📅 Enter Year", min_value=2000, max_value=2025, value=2022)
station_id = col2.text_input("🏷️ Enter Station ID", value="1")

if st.button("🔍 Predict"):
    if not station_id:
        st.warning("Please enter a valid Station ID")
    else:
        input_data = pd.DataFrame({'year': [year_input], 'id': [station_id]})
        input_encoded = pd.get_dummies(input_data, columns=['id'])

        for col in model_cols:
            if col not in input_encoded.columns:
                input_encoded[col] = 0
        input_encoded = input_encoded[model_cols]

        prediction = model.predict(input_encoded)[0]
        pollutants = ['O2', 'NO3', 'NO2', 'SO4', 'PO4', 'CL']

        st.markdown("### 🧪 Predicted Pollutant Levels")
        predicted_values = {}
        for p, value in zip(pollutants, prediction):
            st.markdown(f"**{p}**: {value:.2f}")
            predicted_values[p] = value

        limits = {
            'O2': 5,
            'NO3': 10,
            'NO2': 0.1,
            'SO4': 250,
            'PO4': 0.1,
            'CL': 250
        }

        st.markdown("### 🧾 Parameter-wise Assessment")
        unsafe_count = 0
        for p in pollutants:
            val = predicted_values[p]
            if p == 'O2':
                if val < limits[p]:
                    st.markdown(f"<span style='color:red;'>❌ {p} is too low ({val:.2f} &lt; {limits[p]})</span>", unsafe_allow_html=True)
                    unsafe_count += 1
                else:
                    st.markdown(f"<span style='color:white;'>✅ {p} is good ({val:.2f} ≥ {limits[p]})</span>", unsafe_allow_html=True)
            else:
                if val > limits[p]:
                    st.markdown(f"<span style='color:red;'>❌ {p} is too high ({val:.2f} &gt; {limits[p]})</span>", unsafe_allow_html=True)
                    unsafe_count += 1
                else:
                    st.markdown(f"<span style='color:white;'>✅ {p} is within safe limit ({val:.2f} ≤ {limits[p]})</span>", unsafe_allow_html=True)

        st.markdown("### 🧠 Final Verdict")
        if unsafe_count == 0:
            st.success("✅ Water is SAFE for drinking")
        elif unsafe_count <= 3:
            st.warning("⚠️ Water is MODERATELY SAFE – Use with caution")
        else:
            st.error("❌ Water is UNSAFE for drinking")

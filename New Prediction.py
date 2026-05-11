import streamlit as st
import pandas as pd
import numpy as np
import joblib

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Drug Safety Prediction",
    page_icon="💊",
    layout="wide"
)

st.title("💊 Drug Safety & Pharmacovigilance Dashboard")
st.markdown(
    "Predict adverse drug reaction seriousness using the trained ML pipeline."
)

# =========================
# LOAD MODEL
# =========================
@st.cache_resource
def load_model():
    model = joblib.load("models/task1_xgboost_model.pkl")
    return model

model = load_model()

# =========================
# SIDEBAR
# =========================
st.sidebar.header("Patient & Drug Information")

# =========================
# USER INPUTS
# =========================

age = st.sidebar.number_input(
    "Patient Age",
    min_value=0,
    max_value=120,
    value=35
)

sex = st.sidebar.selectbox(
    "Sex",
    ["M", "F", "Unknown"]
)

route = st.sidebar.selectbox(
    "Drug Route",
    [
        "ORAL",
        "INTRAVENOUS",
        "TOPICAL",
        "SUBCUTANEOUS",
        "INHALATION",
        "UNKNOWN"
    ]
)

indication = st.sidebar.text_input(
    "Indication",
    value="Pain"
)

action_taken = st.sidebar.selectbox(
    "Action Taken",
    [
        "Drug Withdrawn",
        "Dose Reduced",
        "Dose Increased",
        "No Change",
        "Unknown"
    ]
)

num_reactions = st.sidebar.number_input(
    "Number of Reactions",
    min_value=1,
    max_value=20,
    value=1
)

drug_freq = st.sidebar.number_input(
    "Drug Frequency",
    min_value=1,
    max_value=10000,
    value=1
)

# =========================
# CREATE INPUT DATAFRAME
# =========================

X = pd.DataFrame([{
    "age": age,
    "sex": sex,
    "route": route,
    "indication": indication,
    "action_taken": action_taken,
    "num_reactions": num_reactions,
    "drug_freq": drug_freq
}])

# =========================
# SHOW INPUT DATA
# =========================

with st.expander("🔍 View Input Data"):
    st.dataframe(X)

# =========================
# PREDICTION
# =========================

if st.button("🚨 Predict Seriousness Risk"):

    try:
        probs = model.predict_proba(X)[:, 1]
        prediction = model.predict(X)[0]

        risk_score = round(float(probs[0]) * 100, 2)

        st.subheader("Prediction Result")

        if prediction == 1:
            st.error(f"⚠️ High Seriousness Risk Detected")
        else:
            st.success("✅ Low Seriousness Risk")

        st.metric(
            label="Seriousness Probability",
            value=f"{risk_score}%"
        )

    except Exception as e:
        st.error(f"Prediction Error: {e}")

# =========================
# DEBUG SECTION
# =========================

with st.expander("🛠 Debug Information"):

    st.write("### Model Expected Features")
    
    try:
        st.write(model.feature_names_in_)
    except:
        st.write("feature_names_in_ not available")

    st.write("### Input Columns")
    st.write(X.columns.tolist())

    st.write("### Input Shape")
    st.write(X.shape)
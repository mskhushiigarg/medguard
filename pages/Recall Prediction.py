import streamlit as st
import pandas as pd
import joblib
import numpy as np

# Load models and supporting files
reg_serious = joblib.load("models/seriousness_model.pkl")
reg_death = joblib.load("models/death_model.pkl")
clf_recall = joblib.load("models/recall_model.pkl")
scaler = joblib.load("models/cluster_scaler.pkl")
kmeans = joblib.load("models/cluster_model.pkl")
model_features = joblib.load("models/model_features.pkl") 

df = pd.read_csv("final_merged_dataset.csv") 

st.title("Drug Safety & Recall Prediction Section")

# Dropdown for drug selection
drug_names = df["drug_name"].unique()
selected_drug = st.selectbox("🔍 Select a Drug", drug_names)

if st.button("🔎 Predict Drug Risk & Recall"):

    # Get the full original row for clustering
    original_row = df[df["drug_name"] == selected_drug].copy()

    if original_row.empty:
        st.error("Drug not found in dataset.")
    else:
        # Prepare input for model prediction
        model_row = original_row.copy()
        for col in model_features:
            if col not in model_row.columns:
                model_row[col] = 0
        model_row = model_row[model_features]

        # Predictions
        pred_serious = reg_serious.predict(model_row)[0]
        pred_death = reg_death.predict(model_row)[0]
        pred_recall = clf_recall.predict(model_row)[0]

        # Clustering (original row with required features)
        clust_cols = ["serious", "seriousnessdeath", "num_reactions", "boxed_warning", "contraindications_len", "indications_len"]
        cluster_input = scaler.transform(original_row[clust_cols])
        cluster_id = kmeans.predict(cluster_input)[0]
        risk_label = {0: "Low Risk", 1: "Medium Risk", 2: "High Risk"}.get(cluster_id, "Unknown")

        # Show results
        st.subheader("Prediction Results")
        st.write(f"**Serious side effects Likelihood**: {pred_serious:.2f}")
        st.write(f"**Death Likelihood**: {pred_death:.2f}")
        st.write(f"**Recall Prediction**: {'🔴 Will be Recalled' if pred_recall else '🟢 Safe (Not Recalled)'}")
        st.write(f"**Drug Risk Cluster**: {risk_label}")

        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        col1.metric("⚠️ Serious Side Effects", f"{pred_serious:.2f}")
        col2.metric("☠️ Death Likelihood", f"{pred_death:.2f}")
        col3.metric("📦 Recall", "Yes" if pred_recall else "No", delta="High" if pred_recall else "Low")

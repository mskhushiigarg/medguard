# 1 --------------------------- predict

import joblib
import numpy as np

model = joblib.load("models/task1_xgboost_model.pkl")

def predict_risk(df, drug_name):

    drug_df = df[df["drug_name"] == drug_name]

    if len(drug_df) == 0:
        return None, None, None

    # IMPORTANT: drop non-features safely
    X = drug_df.drop(columns=["serious_event", "reaction_text"], errors="ignore")

    probs = model.predict_proba(X)[:, 1]

    mean_risk = float(np.mean(probs))

    lower = float(np.percentile(probs, 5))
    upper = float(np.percentile(probs, 95))

    ci = (lower, upper)

    return mean_risk, ci, X


# 2 ---------------------------------------- data

import pandas as pd

def load_data():
    df = pd.read_parquet("data_cleaned.parquet")
    ror = pd.read_csv("ror_signals.csv")
    clusters = pd.read_csv("drug_clusters.csv")
    return df, ror, clusters


def get_top_reactions(ror_df, drug_name):
    top = ror_df[ror_df["drug"] == drug_name]
    top = top.sort_values(by="ROR", ascending=False).head(10)
    return top


# 3 ------------------------------- shap

import shap
import matplotlib.pyplot as plt

def get_shap_plot(model, X):
    explainer = shap.Explainer(model.named_steps["classifier"])
    X_transformed = model.named_steps["preprocessor"].transform(X)

    shap_values = explainer(X_transformed)

    fig, ax = plt.subplots()
    shap.plots.waterfall(shap_values[0], show=False)

    return fig
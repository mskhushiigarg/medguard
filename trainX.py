import pandas as pd
import numpy as np
import joblib
import json

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
import xgboost as xgb

# -----------------------
# LOAD DATA
# -----------------------
df = pd.read_parquet("data_cleaned.parquet")

target = "serious_event"

features = [
    "drug_name",
    "age",
    "sex",
    "route",
    "indication",
    "action_taken",
    "num_reactions"
]

X = df[features].copy()
y = df[target]

# -----------------------
# SPLIT FIRST (NO LEAKAGE)
# -----------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# -----------------------
# DRUG FREQUENCY (TRAIN ONLY)
# -----------------------
drug_freq = X_train["drug_name"].value_counts()

X_train["drug_freq"] = X_train["drug_name"].map(drug_freq)
X_test["drug_freq"] = X_test["drug_name"].map(drug_freq).fillna(0)

X_train = X_train.drop(columns=["drug_name"])
X_test = X_test.drop(columns=["drug_name"])

# -----------------------
# PREPROCESSOR
# -----------------------
categorical = ["sex", "route", "indication", "action_taken"]
numeric = ["age", "num_reactions", "drug_freq"]

preprocessor = ColumnTransformer([
    ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
    ("num", "passthrough", numeric)
])

# -----------------------
# MODEL
# -----------------------
model = xgb.XGBClassifier(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    eval_metric="logloss",
    random_state=42
)

# -----------------------
# PIPELINE (FINAL SAFE ARTIFACT)
# -----------------------
pipeline = Pipeline([
    ("preprocess", preprocessor),
    ("model", model)
])

pipeline.fit(X_train, y_train)

# -----------------------
# SAVE MODEL
# -----------------------
joblib.dump(pipeline, "models/pipeline.joblib")

# -----------------------
# SAVE FEATURE SCHEMA (IMPORTANT FOR DEBUGGING)
# -----------------------
metadata = {
    "features": features,
    "categorical": categorical,
    "numeric": numeric
}

with open("models/metadata.json", "w") as f:
    json.dump(metadata, f)

print("✅ Production pipeline saved successfully")
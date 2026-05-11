import joblib
feature_names = joblib.load("models/feature_names.pkl")
print("Model expects:", len(feature_names), "features")
print(feature_names[:10])
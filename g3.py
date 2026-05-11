import requests
import pandas as pd

# ----------- RECALL DATA COLLECTION -----------
def fetch_recall_data(limit=1000):
    url = f"https://api.fda.gov/drug/enforcement.json?limit={limit}"
    response = requests.get(url)
    data = response.json().get("results", [])
    df = pd.DataFrame(data)
    
    df["recalled"] = 1
    df["drug_name"] = df["product_description"].str.extract(r'([A-Za-z0-9\s\-]+)')[0].str.lower().str.strip()
    
    return df[["drug_name", "recall_initiation_date", "reason_for_recall", "status", "recalled"]]

recall_df = fetch_recall_data()


# ----------- ADVERSE EVENT DATA COLLECTION -----------
def fetch_adverse_event_data(limit=1000):
    url = f"https://api.fda.gov/drug/event.json?limit={limit}"
    response = requests.get(url)
    data = response.json().get("results", [])
    
    records = []
    for item in data:
        drugs = item.get("patient", {}).get("drug", [])
        reactions = item.get("patient", {}).get("reaction", [])
        
        for drug in drugs:
            name = drug.get("medicinalproduct", "").lower().strip()
            records.append({
                "drug_name": name,
                "serious": item.get("serious", 0),
                "seriousnessdeath": item.get("seriousnessdeath", 0),
                "num_reactions": len(reactions)
            })
    
    df = pd.DataFrame(records)

    # Ensure numeric types for aggregation
    df["serious"] = pd.to_numeric(df["serious"], errors="coerce").fillna(0).astype(int)
    df["seriousnessdeath"] = pd.to_numeric(df["seriousnessdeath"], errors="coerce").fillna(0).astype(int)
    df["num_reactions"] = pd.to_numeric(df["num_reactions"], errors="coerce").fillna(0)

    # Group and summarize
    ae_summary = df.groupby("drug_name").agg({
        "serious": "sum",
        "seriousnessdeath": "sum",
        "num_reactions": "mean"
    }).reset_index()
    
    return ae_summary
ae_df = fetch_adverse_event_data()


# ----------- LABEL DATA COLLECTION -----------
def fetch_label_data(limit=1000):
    url = f"https://api.fda.gov/drug/label.json?limit={limit}"
    response = requests.get(url)
    data = response.json().get("results", [])
    
    records = []
    for item in data:
        name = item.get("openfda", {}).get("generic_name", [""])[0].lower().strip()
        records.append({
            "drug_name": name,
            "boxed_warning": 1 if "boxed_warning" in item else 0,
            "contraindications_len": len(item.get("contraindications", [""])[0].split()),
            "indications_len": len(item.get("indications_and_usage", [""])[0].split()),
            "manufacturer": item.get("openfda", {}).get("manufacturer_name", ["Unknown"])[0]
        })
    
    return pd.DataFrame(records)

label_df = fetch_label_data()


# ----------- SAVE FILES FOR ML -----------
recall_df.to_csv("recall_data.csv", index=False)
ae_df.to_csv("adverse_event_data.csv", index=False)
label_df.to_csv("label_data.csv", index=False)

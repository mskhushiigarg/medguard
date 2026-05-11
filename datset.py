import pandas as pd

# Load the CSVs
recall_df = pd.read_csv("recall_data.csv")
ae_df = pd.read_csv("adverse_event_data.csv")
label_df = pd.read_csv("label_data.csv")

# STEP 1: Normalize drug_name column in all 3 DataFrames
def clean_drug_name(df):
    df["drug_name"] = df["drug_name"].astype(str).str.lower().str.strip()
    return df

recall_df = clean_drug_name(recall_df)
ae_df = clean_drug_name(ae_df)
label_df = clean_drug_name(label_df)

# STEP 2: Drop unnecessary recall text fields (we only want binary target now)
recall_df = recall_df[["drug_name", "recalled"]]  # keep only what's needed

# STEP 3: Merge all dataframes
merged_df = recall_df.merge(ae_df, on="drug_name", how="outer")
merged_df = merged_df.merge(label_df, on="drug_name", how="outer")

# STEP 4: Handle missing values
merged_df["recalled"] = merged_df["recalled"].fillna(0)  # unrecalled drugs are labeled 0
merged_df["boxed_warning"] = merged_df["boxed_warning"].fillna(0)
merged_df["contraindications_len"] = merged_df["contraindications_len"].fillna(0)
merged_df["indications_len"] = merged_df["indications_len"].fillna(0)
merged_df["serious"] = merged_df["serious"].fillna(0)
merged_df["seriousnessdeath"] = merged_df["seriousnessdeath"].fillna(0)
merged_df["num_reactions"] = merged_df["num_reactions"].fillna(0)
merged_df["manufacturer"] = merged_df["manufacturer"].fillna("unknown")

# STEP 5: One-hot encode manufacturer
merged_df = pd.get_dummies(merged_df, columns=["manufacturer"], drop_first=True)

# STEP 6: Save merged dataset
merged_df.to_csv("final_merged_dataset.csv", index=False)
print("✅ Final merged dataset saved as 'final_merged_dataset.csv'")

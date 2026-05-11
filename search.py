import streamlit as st
import requests

# Page Title
st.title("OpenFDA Drug Info Dashboard")

# Text input for drug name
drug_name = st.text_input("Enter the drug name (e.g., ibuprofen):")

# Button to fetch data
if st.button("Get Drug Info"):
    if drug_name:  # if input is not empty
        with st.spinner("Fetching data..."):
            # API endpoint and parameters
            url = "https://api.fda.gov/drug/label.json"
            params = {
                "search": f"openfda.brand_name:{drug_name}",
                "limit": 1
            }

            response = requests.get(url, params=params)

            if response.status_code == 200:
                data = response.json()

                if "results" in data:
                    result = data["results"][0]
                    
                    # Extract some fields to show
                    brand_name = result.get("openfda", {}).get("brand_name", ["N/A"])[0]
                    manufacturer = result.get("openfda", {}).get("manufacturer_name", ["N/A"])[0]
                    usage = result.get("indications_and_usage", ["N/A"])[0]
                    warnings = result.get("warnings", ["N/A"])[0]

                    # Display data in a clean format
                    st.subheader("Drug Information")
                    st.write(f"**Brand Name:** {brand_name}")
                    st.write(f"**Manufacturer:** {manufacturer}")
                    st.write(f"**Indications and Usage:** {usage}")
                    st.write(f"**Warnings:** {warnings}")
                else:
                    st.warning("No data found for this drug.")
            else:
                st.error(f"Error: {response.status_code}")
    else:
        st.warning("Please enter a drug name to search.")

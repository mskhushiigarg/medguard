import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# page configuration
st.set_page_config(
    page_title="MEDGUARD",
    page_icon="💊",
    layout="wide"
)

st.sidebar.success("Select the page you want to view.")

# Title Section
st.markdown("""
# 💊 MEDGUARD

Welcome! Explore drug safety data and learn about side effects, dosage forms, interactions, recalls, and more. 
This tool is designed to help you understand medication safety trends and make informed health decisions.
""", unsafe_allow_html=True)

st.markdown("---")

# Title and Graph Switcher
st.title("FDA Adverse Event Section")
st.markdown("Use the **switcher below** to explore 3 different graphs:")

graph_options1 = {
    "SIDE EFFECTS REPORTED OVER TIME": ":red-background[SIDE EFFECTS REPORTED OVER TIME]",
    "TOP SIDE EFFECTS": ":red-background[TOP SIDE EFFECTS]",
    "TOP CONDITIONS TREATED BY DRUGS": ":red-background[TOP CONDITIONS TREATED BY DRUGS]"
}
selected_graph_display = st.radio(
    "Select Graph to Display:",
    list(graph_options1.values()),
    horizontal=True,
    key="graph_switcher1",
    label_visibility="collapsed"
)
selected_graph = [k for k, v in graph_options1.items() if v == selected_graph_display][0]

# Helper Functions
def fetch_data(api_url):
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        st.error(f"API request failed with status code: {response.status_code}")
        return None

def general_reports_graph(search_query):
    api_url = f"https://api.fda.gov/drug/event.json?search={search_query}&count=receivedate"
    data = fetch_data(api_url)
    if data and "results" in data:
        df = pd.DataFrame(data["results"])
        df["time"] = pd.to_datetime(df["time"], format="%Y%m%d")
        df = df.sort_values(by="time")
        fig = px.line(
            df, x="time", y="count", markers=True,
            title="General Adverse Event Reports Over Time",
            labels={"time": "Year", "count": "Number of Reports"},
            color_discrete_sequence=["#FF5722"]
        )
        fig.update_traces(line=dict(width=3))
        fig.update_layout(
            plot_bgcolor="white",
            xaxis=dict(dtick="M12", tickformat="%Y")
        )
        return fig, api_url
    return None, api_url

def top_reactions_graph(search_query):
    api_url = f"https://api.fda.gov/drug/event.json?search={search_query}&count=patient.reaction.reactionmeddrapt.exact"
    data = fetch_data(api_url)
    if data and "results" in data:
        df = pd.DataFrame(data["results"]).sort_values(by="count", ascending=False).head(15)
        fig = px.bar(
            df, x="count", y="term", orientation="h", color="count", text="count",
            title="Top 15 Reported Drug Reactions",
            color_continuous_scale="Plasma"
        )
        fig.update_layout(
            plot_bgcolor="white",
            xaxis=dict(showgrid=True, gridcolor="lightgrey"),
            yaxis=dict(autorange="reversed", showgrid=False)
        )
        return fig, api_url
    return None, api_url

def top_indications_graph(search_query):
    api_url = f"https://api.fda.gov/drug/event.json?search={search_query}&count=patient.drug.drugindication.exact"
    data = fetch_data(api_url)
    if data and "results" in data:
        df = pd.DataFrame(data["results"])
        df = df[~df["term"].isin(["Product used for unknown indication", "PRODUCT USED FOR UNKNOWN INDICATION"])]
        df = df.sort_values(by="count", ascending=False).head(15)
        fig = px.bar(
            df, x="count", y="term", orientation="h", color="count", text="count",
            title="Top 15 Reported Drug Indications",
            color_continuous_scale="Viridis"
        )
        fig.update_layout(
            plot_bgcolor="white",
            xaxis=dict(showgrid=True, gridcolor="lightgrey"),
            yaxis=dict(autorange="reversed", showgrid=False)
        )
        return fig, api_url
    return None, api_url

# Main Layout for Graph 1
col1, col2 = st.columns([1, 3])
with col1:
    st.markdown("### Filters and Search")

    if selected_graph == "SIDE EFFECTS REPORTED OVER TIME":
        filters = [
            "All adverse event reports",
            "Reported through manufacturers",
            "Reported directly by public",
            "Where indication for drug use was hypertension"
        ]
    else:
        filters = [
            "All",
            "Nonsteroidal anti-inflammatory drug class",
            "Females",
            "Females, age 5 to 17",
            "Females, age 55 to 90",
            "Males",
            "Males, age 5 to 17",
            "Males, age 55 to 90"
        ]

    selected_filter = st.radio("Select a filter:", filters, key=f"filter_{selected_graph}")
    custom_search = st.text_input("Enter a drug name or search parameter:", key=f"search_{selected_graph}")

    search_query = "(receivedate:[20040101+TO+20250530])"
    if selected_graph == "SIDE EFFECTS REPORTED OVER TIME":
        if selected_filter == "Reported through manufacturers":
            search_query += "+AND+_exists_:companynumb"
        elif selected_filter == "Reported directly by public":
            search_query += "+AND+_missing_:companynumb"
        elif selected_filter == "Where indication for drug use was hypertension":
            search_query += "+AND+patient.drug.drugindication:hypertension"
    else:
        if selected_filter == "Nonsteroidal anti-inflammatory drug class":
            search_query += "+AND+patient.drug.openfda.pharm_class_epc:nonsteroidal+anti-inflammatory+drug"
        elif selected_filter == "Females":
            search_query += "+AND+patient.patientsex:2"
        elif selected_filter == "Females, age 5 to 17":
            search_query += "+AND+patient.patientsex:2+AND+patient.patientonsetage:[5+TO+17]"
        elif selected_filter == "Females, age 55 to 90":
            search_query += "+AND+patient.patientsex:2+AND+patient.patientonsetage:[55+TO+90]"
        elif selected_filter == "Males":
            search_query += "+AND+patient.patientsex:1"
        elif selected_filter == "Males, age 5 to 17":
            search_query += "+AND+patient.patientsex:1+AND+patient.patientonsetage:[5+TO+17]"
        elif selected_filter == "Males, age 55 to 90":
            search_query += "+AND+patient.patientsex:1+AND+patient.patientonsetage:[55+TO+90]"

    if custom_search:
        search_query += f"+AND+{custom_search}"

with col2:
    if selected_graph == "SIDE EFFECTS REPORTED OVER TIME":
        fig, api_url = general_reports_graph(search_query)
    elif selected_graph == "TOP SIDE EFFECTS":
        fig, api_url = top_reactions_graph(search_query)
    else:
        fig, api_url = top_indications_graph(search_query)

    if fig:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data found for the given filters or search term.")

# Second Graph Section
st.markdown("---")
st.title("Drug Safety Visualization Section")
st.markdown("Switch between different views to explore FDA drug data by dosage routes and interaction labels.")

# Display-friendly names for second graph switcher
graph_options2 = {
    "Common Drugs' Dosage Forms": ":red-background[Common Drugs' Dosage Forms]",
    "Drug Interactions by Substance": ":red-background[Drug Interactions by Substance]"
}
selected_graph2_display = st.radio(
    "Select Graph to Display:",
    list(graph_options2.values()),
    horizontal=True,
    key="graph_switcher2",
    label_visibility="collapsed"
)
selected_graph2 = [k for k, v in graph_options2.items() if v == selected_graph2_display][0]

col1, col2 = st.columns([1, 3])

if selected_graph2 == "Common Drugs' Dosage Forms":
    route_filters = [
        "All drug labeling submissions",
        "Over-the-counter drug labeling",
        "Prescription drug labeling",
        "Indication or purpose notes the word migraine",
        "Labeling has a Boxed Warning with the word bleeding in it"
    ]

    with col1:
        st.subheader("Filters for Dosage Forms")
        selected_filter = st.radio("Choose a filter:", route_filters, key="route_filter")
        custom_search = st.text_input("Custom search parameter:", key="route_search")

        search_query = ""
        if selected_filter == "Over-the-counter drug labeling":
            search_query = "openfda.product_type:otc"
        elif selected_filter == "Prescription drug labeling":
            search_query = "openfda.product_type:prescription"
        elif selected_filter == "Indication or purpose notes the word migraine":
            search_query = "(indications_and_usage:migraine+OR+purpose:migraine)"
        elif selected_filter == "Labeling has a Boxed Warning with the word bleeding in it":
            search_query = "boxed_warning:bleeding"

        if custom_search:
            search_query += f"+AND+{custom_search}" if search_query else custom_search

    def get_route_data(api_url):
        r = requests.get(api_url)
        if r.status_code == 200:
            data = r.json()
            if "results" in data:
                df = pd.DataFrame(data["results"])
                return df.sort_values(by="count", ascending=False)
        return None

    base_url = "https://api.fda.gov/drug/label.json"
    url = f"{base_url}?search={search_query}&count=openfda.route.exact" if search_query else f"{base_url}?count=openfda.route.exact"

    with col2:
        df = get_route_data(url)
        if df is not None:
            fig = px.bar(
                df, x="count", y="term", orientation="h", color="count",
                title="Drug Route of Administration",
                labels={"term": "Route", "count": "Number of Records"},
                color_continuous_scale="Teal"
            )
            fig.update_layout(yaxis=dict(autorange="reversed"), plot_bgcolor="white")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No results found for this filter.")

elif selected_graph2 == "Drug Interactions by Substance":
    interaction_filters = [
        "Interaction with caffeine",
        "Interaction with grapefruit juice",
        "Interaction with alcohol",
        "Interaction with nicotine",
        "Interaction with antibiotics"
    ]

    with col1:
        st.subheader("Filters for Interactions")
        selected_filter = st.radio("Choose a filter:", interaction_filters, key="interaction_filter")
        custom_search = st.text_input("Enter a drug name or search parameter:", key="interaction_search")

        search_query = ""
        if selected_filter == "Interaction with caffeine":
            search_query = "drug_interactions:caffeine"
        elif selected_filter == "Interaction with grapefruit juice":
            search_query = "drug_interactions:grapefruit"
        elif selected_filter == "Interaction with alcohol":
            search_query = "drug_interactions:alcohol"
        elif selected_filter == "Interaction with nicotine":
            search_query = "drug_interactions:nicotine"
        elif selected_filter == "Interaction with antibiotics":
            search_query = "drug_interactions:antibiotic"

        if custom_search:
            search_query += f"+AND+{custom_search}" if search_query else custom_search

    def get_substance_data(api_url):
        r = requests.get(api_url)
        if r.status_code == 200:
            data = r.json()
            if "results" in data:
                df = pd.DataFrame(data["results"])
                return df.sort_values(by="count", ascending=False)
        return None

    base_url = "https://api.fda.gov/drug/label.json"
    url = f"{base_url}?search={search_query}&count=openfda.substance_name.exact" if search_query else f"{base_url}?count=openfda.substance_name.exact"

    with col2:
        df = get_substance_data(url)
        if df is not None:
            fig = px.bar(
                df, x="count", y="term", orientation="h", color="count",
                title="Top Drug Substances (Active Ingredients)",
                labels={"term": "Substance Name", "count": "Number of Records"},
                color_continuous_scale="Blues"
            )
            fig.update_layout(yaxis=dict(autorange="reversed"), plot_bgcolor="white")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No results found for this filter.")

st.markdown("---")

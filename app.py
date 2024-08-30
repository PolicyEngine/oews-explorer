import streamlit as st
import pandas as pd

st.set_page_config(page_title="Wage Explorer", page_icon="💼", layout="wide")


# Load data
@st.cache_data
def load_data():
    return pd.read_parquet("data/all_data_M_2023.parquet")


df = load_data()

st.title("Wage Percentiles Explorer")

# Sidebar for user input
st.sidebar.header("Select Filters")

# Geography selection
geo_level = st.sidebar.selectbox(
    "Geographic Level", ["National", "State", "Metropolitan"]
)

if geo_level == "National":
    selected_geo = "National"
elif geo_level == "State":
    selected_geo = st.sidebar.selectbox(
        "Select State", sorted(df["PRIM_STATE"].unique())
    )
else:
    selected_geo = st.sidebar.selectbox(
        "Select Metropolitan Area", sorted(df["AREA_TITLE"].unique())
    )

# Job selection
selected_job = st.sidebar.selectbox(
    "Select Occupation", sorted(df["OCC_TITLE"].unique())
)

# Filter data
if geo_level == "National":
    filtered_df = df[
        (df["OCC_TITLE"] == selected_job) & (df["AREA_TITLE"] == "U.S.")
    ]
elif geo_level == "State":
    filtered_df = df[
        (df["OCC_TITLE"] == selected_job) & (df["PRIM_STATE"] == selected_geo)
    ]
else:
    filtered_df = df[
        (df["OCC_TITLE"] == selected_job) & (df["AREA_TITLE"] == selected_geo)
    ]

# Display results
st.header(f"{selected_job} in {selected_geo}")

if not filtered_df.empty:
    # Display percentiles
    st.subheader("Wage Percentiles")
    percentiles = [
        "H_PCT10",
        "H_PCT25",
        "H_MEDIAN",
        "H_PCT75",
        "H_PCT90",
        "A_PCT10",
        "A_PCT25",
        "A_MEDIAN",
        "A_PCT75",
        "A_PCT90",
    ]
    percentile_labels = ["10th", "25th", "50th (Median)", "75th", "90th"]

    wage_data = filtered_df[percentiles].iloc[0]
    wage_df = pd.DataFrame(
        {
            "Percentile": percentile_labels,
            "Hourly Wage": wage_data[percentiles[:5]].values,
            "Annual Wage": wage_data[percentiles[5:]].values,
        }
    )

    wage_df["Hourly Wage"] = wage_df["Hourly Wage"].apply(
        lambda x: f"${x:.2f}" if pd.notnull(x) else "N/A"
    )
    wage_df["Annual Wage"] = wage_df["Annual Wage"].apply(
        lambda x: f"${x:,.0f}" if pd.notnull(x) else "N/A"
    )

    st.table(wage_df.set_index("Percentile"))

    # Display additional information
    st.subheader("Additional Information")
    info_columns = ["TOT_EMP", "JOBS_1000", "LOC_QUOTIENT"]
    info_labels = ["Total Employment", "Jobs per 1,000", "Location Quotient"]

    info_data = filtered_df[info_columns].iloc[0]
    info_df = pd.DataFrame({"Metric": info_labels, "Value": info_data.values})
    info_df["Value"] = info_df["Value"].apply(
        lambda x: f"{x:,.2f}" if pd.notnull(x) else "N/A"
    )
    st.table(info_df.set_index("Metric"))

else:
    st.warning(
        "No data available for the selected combination of job and geography."
    )

# Data source and notes
st.sidebar.markdown("---")
st.sidebar.info(
    "Data Source: Bureau of Labor Statistics, Occupational Employment and Wage Statistics"
    "\n\nNote: 'N/A' indicates missing or unavailable data."
    "\n\nFor questions or feedback, please contact [Max Ghenis](mailto:max@policyengine.org)."
)

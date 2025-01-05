import streamlit as st
import pandas as pd

st.set_page_config(page_title="Wage Explorer", page_icon="💼", layout="wide")


# Load data
@st.cache_data
def load_data():
    return pd.read_parquet("data/all_data_M_2023.parquet")


df = load_data()

st.title("Wage Percentiles Explorer")


# Helper function to get unique sorted values
def get_unique_sorted(column):
    return sorted(df[column].unique())


# Initialize query parameters
if "geo_level" not in st.query_params:
    st.query_params["geo_level"] = "National"
if "selected_geo" not in st.query_params:
    st.query_params["selected_geo"] = "National"
if "selected_job" not in st.query_params:
    st.query_params["selected_job"] = get_unique_sorted("OCC_TITLE")[0]

# Sidebar for user input
st.sidebar.header("Select Filters")

# Geography selection
geo_level = st.sidebar.selectbox(
    "Geographic Level",
    ["National", "State", "Metropolitan"],
    index=["National", "State", "Metropolitan"].index(
        st.query_params["geo_level"]
    ),
)

if geo_level == "National":
    selected_geo = "National"
elif geo_level == "State":
    selected_geo = st.sidebar.selectbox(
        "Select State",
        get_unique_sorted("PRIM_STATE"),
        index=(
            get_unique_sorted("PRIM_STATE").index(
                st.query_params["selected_geo"]
            )
            if st.query_params["selected_geo"]
            in get_unique_sorted("PRIM_STATE")
            else 0
        ),
    )
else:
    selected_geo = st.sidebar.selectbox(
        "Select Metropolitan Area",
        get_unique_sorted("AREA_TITLE"),
        index=(
            get_unique_sorted("AREA_TITLE").index(
                st.query_params["selected_geo"]
            )
            if st.query_params["selected_geo"]
            in get_unique_sorted("AREA_TITLE")
            else 0
        ),
    )

# Job selection
selected_job = st.sidebar.selectbox(
    "Select Occupation",
    get_unique_sorted("OCC_TITLE"),
    index=get_unique_sorted("OCC_TITLE").index(
        st.query_params["selected_job"]
    ),
)

# Update query parameters
st.query_params["geo_level"] = geo_level
st.query_params["selected_geo"] = selected_geo
st.query_params["selected_job"] = selected_job

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
if geo_level == "National":
    st.header(f"{selected_job} in the United States")
else:
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
            "Hourly": wage_data[percentiles[:5]].values,
            "Annual": wage_data[percentiles[5:]].values,
        }
    )

    wage_df["Hourly"] = wage_df["Hourly"].apply(
        lambda x: f"${x:.2f}" if pd.notnull(x) else "N/A"
    )
    wage_df["Annual"] = wage_df["Annual"].apply(
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
    "Data Source: [Bureau of Labor Statistics, Occupational Employment and Wage Statistics 2023](https://www.bls.gov/oes/)"
    "\n\nNote: 'N/A' indicates missing or unavailable data."
    "\n\nCreated by [Max Ghenis](https://maxghenis.com)",
)

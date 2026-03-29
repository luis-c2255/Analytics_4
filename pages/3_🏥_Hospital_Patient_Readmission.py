import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.theme import Components

st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🏥 :violet[Hospital Patient Readmission Analysis]", text_alignment="center")

@st.cache_data
def load_data():
    df = pd.read_csv("hospital_readmission_dataset.csv")
    # Convert admission_date to datetime
    df['admission_date'] = pd.to_datetime(df['admission_date'])
    
    # Basic cleaning: Handle duplicates
    df.drop_duplicates(inplace=True)
    
    # Create month-year for time series analysis
    df['admission_month'] = df['admission_date'].dt.to_period('M').astype(str)
    
    # Create age groups
    bins = [0, 40, 60, 75, 100]
    labels = ['<40', '40-59', '60-74', '75+']
    df['age_group'] = pd.cut(df['age'], bins=bins, labels=labels, right=False)

    return df

df = load_data()

# --- Sidebar Filters ---
st.sidebar.header("Filter Options")

# Date range slider for admission_date
min_date = df['admission_date'].min().to_pydatetime()
max_date = df['admission_date'].max().to_pydatetime()
selected_date_range = st.sidebar.slider(
    "Admission Date Range",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date),
    format="YYYY-MM-DD"
)
df_filtered_date = df[(df['admission_date'] >= selected_date_range[0]) & (df['admission_date'] <= selected_date_range[1])]

# Multiselect for categorical filters
selected_seasons = st.sidebar.multiselect(
    "Select Season(s)",
    options=df_filtered_date['season'].unique(),
    default=df_filtered_date['season'].unique()
)
selected_genders = st.sidebar.multiselect(
    "Select Gender(s)",
    options=df_filtered_date['gender'].unique(),
    default=df_filtered_date['gender'].unique()
)
selected_regions = st.sidebar.multiselect(
    "Select Region(s)",
    options=df_filtered_date['region'].unique(),
    default=df_filtered_date['region'].unique()
)
selected_diagnoses = st.sidebar.multiselect(
    "Select Primary Diagnosis(es)",
    options=df_filtered_date['primary_diagnosis'].unique(),
    default=df_filtered_date['primary_diagnosis'].unique()
)
selected_insurance_types = st.sidebar.multiselect(
    "Select Insurance Type(s)",
    options=df_filtered_date['insurance_type'].unique(),
    default=df_filtered_date['insurance_type'].unique()
)
selected_discharge_dispositions = st.sidebar.multiselect(
    "Select Discharge Disposition(s)",
    options=df_filtered_date['discharge_disposition'].unique(),
    default=df_filtered_date['discharge_disposition'].unique()
)

# Apply filters
df_filtered = df_filtered_date[
    df_filtered_date['season'].isin(selected_seasons) &
    df_filtered_date['gender'].isin(selected_genders) &
    df_filtered_date['region'].isin(selected_regions) &
    df_filtered_date['primary_diagnosis'].isin(selected_diagnoses) &
    df_filtered_date['insurance_type'].isin(selected_insurance_types) &
    df_filtered_date['discharge_disposition'].isin(selected_discharge_dispositions)
]

if df_filtered.empty:
    st.warning("No data matches the selected filters. Please adjust your selections.")
    st.stop()

# --- Key Metrics Section ---
st.subheader(":rainbow[Key Metrics]", divider="rainbow")

# Calculate metrics
total_patients = df_filtered.shape[0]
readmission_rate = df_filtered['label'].mean() * 100
avg_length_of_stay = df_filtered['length_of_stay'].mean()
avg_readmission_risk_score = df_filtered['readmission_risk_score'].mean()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        Components.metric_card(
            title="Total Patients",
            value=f"{total_patients:,}",
            delta="+150 (MoM)",
            card_type="info"
        ), unsafe_allow_html=True
    )
with col2:
    st.markdown(
        Components.metric_card(
            title="Overall Readmission Rate",
            value=f"{readmission_rate:.1f}%",
            delta="+0.5% (WoW)",
            card_type="error" if readmission_rate > 15 else "success"
        ), unsafe_allow_html=True
    )
with col3:
    st.markdown(
        Components.metric_card(
            title="Avg. Length of Stay",
            value=f"{avg_length_of_stay:.1f} days",
            delta="-0.2 days (YoY)",
            card_type="success" if avg_length_of_stay < 7 else "warning"
        ), unsafe_allow_html=True
    )
with col4:
    st.markdown(
        Components.metric_card(
            title="Avg. Risk Score",
            value=f"{avg_readmission_risk_score:.2f}",
            delta="-0.03 (MoM)",
            card_type="success"
        ), unsafe_allow_html=True
    )
    
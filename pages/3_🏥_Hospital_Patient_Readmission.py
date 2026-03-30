import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.theme import Components, Colors, init_page

init_page("Hospital Patient Readmission Analysis", "🏥")

try:
    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
except FileNotFoundError:
    pass

st.markdown(
    Components.page_header("🏥  Hospital Patient Readmission Analysis"), unsafe_allow_html=True
)

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
            delta_positive=False,
            card_type="error" if readmission_rate > 15 else "success"
        ), unsafe_allow_html=True
    )
with col3:
    st.markdown(
        Components.metric_card(
            title="Avg. Length of Stay",
            value=f"{avg_length_of_stay:.1f} days",
            delta="-0.2 days (YoY)",
            delta_positive=False,
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

st.subheader(":blue[Overview]", divider="blue")
st.markdown("   ")
readmission_counts = df_filtered['label'].value_counts(normalize=True).reset_index()
readmission_counts['label'] = readmission_counts['label'].map({0: 'No Readmission', 1: 'Readmission'})
fig_pie = px.pie(
    readmission_counts,
    names='label',
    values='proportion',
    title='Proportion of Readmissions',
    color_discrete_sequence=px.colors.qualitative.Pastel
)
st.plotly_chart(fig_pie, width="stretch")
st.markdown("   ")

fig_hist = px.histogram(
    df_filtered,
    x='readmission_risk_score',
    nbins=20,
    title='Readmission Risk Score Distribution',
    color_discrete_sequence=['#636EFA']
)
st.plotly_chart(fig_hist, width="stretch")
st.markdown("   ")

st.subheader(":red[Risk Factors]", divider="red")
st.markdown("   ")
top_n_diagnoses = df_filtered['primary_diagnosis'].value_counts().nlargest(10).index
df_top_diagnoses = df_filtered[df_filtered['primary_diagnosis'].isin(top_n_diagnoses)]
readmission_by_diagnosis = df_top_diagnoses.groupby('primary_diagnosis')['label'].mean().reset_index()
readmission_by_diagnosis['readmission_rate'] = readmission_by_diagnosis['label'] * 100

fig_diag = px.bar(
    readmission_by_diagnosis.sort_values('readmission_rate', ascending=False),
    x='readmission_rate',
    y='primary_diagnosis', 
    orientation='h',
    title='Readmission Rate by Top Primary Diagnosis',
    labels={'readmission_rate': 'Readmission Rate (%)', 'primary_diagnosis': 'Primary Digaagnosis'},
    text_auto=True,
    color_discrete_sequence=px.colors.sequential.Viridis
)
st.plotly_chart(fig_diag, width="stretch")
st.markdown("   ")

fig_box_los = px.box(
    df_filtered,
    x='label',
    y='length_of_stay',
    title='Length of Stay by Readmission Status',
    labels={'label': 'Readmission Status (0: No, 1: Yes)', 'length': 'Length  of Stay (days)'},
    color='label',
    color_discrete_map={0: 'salmon', 1: 'lightgreen'}
)
st.plotly_chart(fig_box_los, width="stretch")
st.markdown("   ")

readmission_by_comorbid = df_filtered.groupby('comorbidities_count')['label'].mean().reset_index()
readmission_by_comorbid['readmission_rate'] = readmission_by_comorbid['label'] * 100

fig_comorbid = px.bar(
    readmission_by_comorbid,
    x='comorbidities_count',
    y='readmission_rate',
    title='Readmission Rate by Number of Comorbidities',
    labels={'comorbidities_count': 'Number of Comorbidities', 'readmission_rate': 'Readmission Rate (%)'},
    color_discrete_sequence=['#EF553B']
)
st.plotly_chart(fig_comorbid, width="stretch")
st.markdown("   ")

st.subheader(":green[Demographics & Operations]", divider="green")
st.markdown("   ")
readmission_by_gender = df_filtered.groupby('gender')['label'].mean().reset_index()
readmission_by_gender['readmission_rate'] = readmission_by_gender['label'] * 100

fig_gender = px.bar(
    readmission_by_gender,
    x='gender',
    y='readmission_rate',
    title='Readmission Rate by Gender',
    text_auto=True,
    labels={'gender': 'Gender', 'readmission_rate': 'Readmission Rate (%)'},
    color_discrete_sequence=px.colors.qualitative.G10
)
st.plotly_chart(fig_gender, width="stretch")
st.markdown("   ")

readmission_by_season = df_filtered.groupby('season')['label'].mean().reset_index()
readmission_by_season['readmission_rate'] = readmission_by_season['label'] * 100

fig_season = px.bar(
    readmission_by_season,
    x='season',
    y='readmission_rate',
    title='Readmission Rate by Season',
    text_auto=True,
    labels={'season': 'Season', 'readmission_rate': 'Readmission Rate (%)'},
    color_discrete_sequence=px.colors.qualitative.Set2
)
st.plotly_chart(fig_season, width="stretch")
st.markdown("   ")

readmission_by_region = df_filtered.groupby('region')['label'].mean().reset_index()
readmission_by_region['readmission_rate'] = readmission_by_region['label'] * 100

fig_region = px.bar(
    readmission_by_region.sort_values('readmission_rate', ascending=False),
    x='readmission_rate',
    y='region',
    orientation='h',
    title='Readmission Rate by Region',
    text_auto=True,
    labels={'region': 'Region', 'readmission_rate': 'Readmission Rate (%)'},
    color_discrete_sequence=px.colors.qualitative.Bold
)
st.plotly_chart(fig_region, width="stretch")
st.markdown("   ")

readmission_by_insurance = df_filtered.groupby('insurance_type')['label'].mean().reset_index()
readmission_by_insurance['readmission_rate'] = readmission_by_insurance['label'] * 100
fig_insurance = px.bar(readmission_by_insurance.sort_values('readmission_rate', ascending=False),
                        x='readmission_rate', y='insurance_type', orientation='h',
                        title='Readmission Rate by Insurance Type',
                        labels={'insurance_rate': 'Insurance Type', 'readmission_rate': 'Readmission Rate (%)'},
                        text_auto=True,
                        color_discrete_sequence=px.colors.qualitative.Vivid
                    )
st.plotly_chart(fig_insurance, width="stretch")
st.markdown("   ")

st.subheader(":yellow[Advanced Insights]", divider="yellow")
st.markdown("   ")
monthly_readmission = df_filtered.groupby('admission_month')['label'].mean().reset_index()
monthly_readmission['readmission_rate'] = monthly_readmission['label'] * 100
monthly_readmission['admission_month'] = pd.to_datetime(monthly_readmission['admission_month'])
monthly_readmission = monthly_readmission.sort_values('admission_month')

fig_trend = px.line(monthly_readmission, x='admission_month', y='readmission_rate',
                        title='Monthly Readmission Rate Over Time',
                        labels={'admission_month': 'Admission Month', 'readmission_rate': 'Readmission Rate (%)'},
                        markers=True, line_shape="spline")
fig_trend.update_xaxes(dtick="M1", tickformat="%b\n%Y") # Format x-axis for months
st.plotly_chart(fig_trend, width="stretch")
st.markdown("   ")

readmission_by_age_group = df_filtered.groupby('age_group')['label'].mean().reset_index()
readmission_by_age_group['readmission_rate'] = readmission_by_age_group['label'] * 100
fig_age_group = px.bar(readmission_by_age_group.sort_values('readmission_rate', ascending=False),
                               x='age_group', y='readmission_rate',
                               title='Readmission Rate by Age Group',
                               labels={'age_group': 'Age Group', 'readmission_rate': 'Readmission Rate (%)'},
                               color_discrete_sequence=px.colors.qualitative.Plotly)
st.plotly_chart(fig_age_group, width="stretch")
st.markdown("   ")

readmission_by_discharge = df_filtered.groupby('discharge_disposition')['label'].mean().reset_index()
readmission_by_discharge['readmission_rate'] = readmission_by_discharge['label'] * 100
fig_discharge = px.bar(readmission_by_discharge.sort_values('readmission_rate', ascending=False),
                               x='readmission_rate', y='discharge_disposition', orientation='h',
                               title='Readmission Rate by Discharge Disposition',
                               labels={'discharge_disposition': 'Discharge Disposition', 'readmission_rate': 'Readmission Rate (%)'},
                               color_discrete_sequence=px.colors.qualitative.T10)
st.plotly_chart(fig_discharge, width="stretch")
st.markdown("   ")

fig_violin_risk = px.violin(df_filtered, x='label', y='readmission_risk_score', color='label',
                                title='Readmission Risk Score Distribution (0: No Readmission, 1: Readmission)',
                                labels={'label': 'Actual Readmission Status', 'readmission_risk_score': 'Readmission Risk Score'},
                                box=True, # show box plot inside violin
                                points="outliers", # show all points but highlight outliers
                                color_discrete_map={0: 'lightblue', 1: 'pink'})
st.plotly_chart(fig_violin_risk, width="stretch")
# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p><strong>🏥 Hospital Patient Readmission Analysis</strong></p>
    <p>Explore key metrics, risk factors, demographics and operations.</p>
    <p style='font-size: 0.9rem;'>Navigate using the sidebar to explore different datasets</p>
</div>
""", unsafe_allow_html=True)
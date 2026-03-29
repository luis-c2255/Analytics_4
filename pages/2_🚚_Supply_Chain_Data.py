import streamlit as st
import pandas as pd
import plotly.express as px
import io
from utils.theme import Components

st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🚚 :orange[Supply Chain Data Analysis]", text_alignment="center")

# --- Data Loading ---
@st.cache_data
def load_data():
    df = pd.read_csv("supply_chain_data.csv")
    # Basic cleaning: Convert column names to a consistent format (snake_case)
    df.columns = df.columns.str.lower().str.replace(' ', '_').str.replace('[^a-z0-9_]', '', regex=True)
    return df
df = load_data()

# Ensure numeric types and handle missing values
numeric_cols = ['price', 'availability', 'number_of_products_sold', 'revenue_generated',
                'stock_levels', 'lead_times', 'order_quantities', 'shipping_times',
                'shipping_costs', 'production_volumes', 'manufacturing_lead_time',
                'manufacturing_costs', 'defect_rates', 'costs']
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        
# Drop rows where critical metrics are missing
df.dropna(subset=['revenue_generated', 'number_of_products_sold', 'price', 
                  'stock_levels', 'manufacturing_costs', 'shipping_costs', 
                  'defect_rates', 'lead_times', 'manufacturing_lead_time',
                  'production_volumes'], inplace=True)
df.drop_duplicates(inplace=True)

# Calculate overall (unfiltered) metrics for delta comparison
overall_total_revenue = df['revenue_generated'].sum()
overall_avg_defect_rate = df['defect_rates'].mean()
overall_total_products_sold = df['number_of_products_sold'].sum()
overall_avg_shipping_cost = df['shipping_costs'].mean()
overall_avg_manufacturing_cost = df['manufacturing_costs'].mean()

# --- Sidebar Filters ---
st.sidebar.header("Filter Data")

# Product Type Filter
product_types = ['All'] + df['product_type'].unique().tolist()
selected_product_type = st.sidebar.selectbox("Select Product Type", product_types)

# Location Filter
locations = ['All'] + df['location'].unique().tolist()
selected_location = st.sidebar.selectbox("Select Location", locations)

# Shipping Carrier Filter
carriers = ['All'] + df['shipping_carriers'].unique().tolist()
selected_carrier = st.sidebar.selectbox("Select Shipping Carrier", carriers)

# Apply filters
filtered_df = df.copy()
if selected_product_type != 'All':
    filtered_df = filtered_df[filtered_df['product_type'] == selected_product_type]
if selected_location != 'All':
    filtered_df = filtered_df[filtered_df['location'] == selected_location]
if selected_carrier != 'All':
    filtered_df = filtered_df[filtered_df['shipping_carriers'] == selected_carrier]
    
# Check if filtered_df is empty after filtering
if filtered_df.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

# --- METRICS SECTION ---
st.subheader(":rainbow[Key Metrics]", divider="rainbow")

# Calculate metrics for the current filtered view
total_revenue = filtered_df['revenue_generated'].sum()
avg_defect_rate = filtered_df['defect_rates'].mean()
total_products_sold = filtered_df['number_of_products_sold'].sum()
avg_shipping_cost = filtered_df['shipping_costs'].mean()
avg_manufacturing_cost = filtered_df['manufacturing_costs'].mean()


col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.markdown(
        Components.metric_card(
        title="Total Revenue",
        value=f"${total_revenue:,.2f}",
        delta="",
        card_type="info"
    ), unsafe_allow_html=True
)
with col2:
    st.markdown(
        Components.metric_card(
        title="Avg. Defect Rate",
        value=f"{avg_defect_rate:.2f}%",
        delta="",
        card_type="info"
    ), unsafe_allow_html=True
)
with col3:
    st.markdown(
        Components.metric_card(
        title="Products Sold",
        value=f"{int(total_products_sold):,}",
        delta="",
        card_type="info"
    ), unsafe_allow_html=True
)
with col4:
    st.markdown(
        Components.metric_card(
        title="Avg. Manufacturing Cost",
        value=f"${avg_manufacturing_cost:.2f}",
        delta="",
        card_type="info"
    ), unsafe_allow_html=True
)
with col5:
    st.markdown(
        Components.metric_card(
        title="Avg. Shipping Cost",
        value=f"${avg_shipping_cost:.2f}",
        delta="",
        card_type="info"
    ), unsafe_allow_html=True
)
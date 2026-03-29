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
        delta="💲",
        card_type="success"
    ), unsafe_allow_html=True
)
with col2:
    st.markdown(
        Components.metric_card(
        title="Avg. Defect Rate",
        value=f"{avg_defect_rate:.2f}%",
        delta="💱",
        card_type="success"
    ), unsafe_allow_html=True
)
with col3:
    st.markdown(
        Components.metric_card(
        title="Products Sold",
        value=f"{int(total_products_sold):,}",
        delta="🪙",
        card_type="info"
    ), unsafe_allow_html=True
)
with col4:
    st.markdown(
        Components.metric_card(
        title="Avg. Manufacturing",
        value=f"${avg_manufacturing_cost:.2f}",
        delta="💶",
        card_type="info"
    ), unsafe_allow_html=True
)
with col5:
    st.markdown(
        Components.metric_card(
        title="Avg. Shipping Cost",
        value=f"${avg_shipping_cost:.2f}",
        delta="💷",
        card_type="info"
    ), unsafe_allow_html=True
)

st.subheader("📊 :green[Overview]", divider="green")
st.markdown("   ")
revenue_by_product = filtered_df.groupby('product_type')['revenue_generated'].sum().sort_values(ascending=False).reset_index()
fig1 = px.bar(revenue_by_product, x='product_type', y='revenue_generated',
              title='Total Revenue by Product Type',
                  labels={'product_type': 'Product Type', 'revenue_generated': 'Total Revenue'},
                  hover_data={'revenue_generated': ':$,.2f'},
                  text_auto=True,
                  color='product_type')
st.plotly_chart(fig1, width="stretch")
st.markdown("   ")
fig2 = px.histogram(filtered_df, x='price', nbins=20,
                        title='Distribution of Product Prices',
                        labels={'price': 'Price'},
                        marginal='box', # Shows box plot on top
                        color_discrete_sequence=px.colors.sequential.Plasma_r)
st.plotly_chart(fig2, width="stretch")

st.subheader("📈 :blue[Product Performance]", divider="blue")
st.markdown("   ")
fig3 = px.scatter(filtered_df, x='price', y='revenue_generated',
                      color='product_type', size='number_of_products_sold',
                      hover_name='sku',
                      title='Price vs. Revenue Generated',
                      labels={'price': 'Price', 'revenue_generated': 'Revenue Generated'},
                      log_x=True, size_max=60)
st.plotly_chart(fig3, width="stretch")
st.markdown("   ")

revenue_by_supplier = filtered_df.groupby('supplier_name')['revenue_generated'].sum().sort_values(ascending=False).head(10).reset_index()
fig4 = px.bar(revenue_by_supplier, x='supplier_name', y='revenue_generated',
                  title='Top 10 Suppliers by Revenue',
                  labels={'supplier_name': 'Supplier Name', 'revenue_generated': 'Total Revenue'},
                  hover_data={'revenue_generated': ':$,.2f'},
                  color='supplier_name',
                  orientation='v')
st.plotly_chart(fig4, width="stretch")
st.markdown("   ")

st.subheader("🔗 :yellow[Supply Chain Efficiency]", divider="yellow")
st.markdown("   ")
shipping_costs_by_carrier = filtered_df.groupby('shipping_carriers')['shipping_costs'].sum().reset_index()
fig5 = px.pie(shipping_costs_by_carrier, values='shipping_costs', names='shipping_carriers',
                  title='Shipping Cost Distribution by Carrier',
                  hole=.3,
                  color_discrete_sequence=px.colors.sequential.Agsunset)
st.plotly_chart(fig5, width="stretch")
st.markdown("   ")

fig6 = px.box(filtered_df, x='product_type', y='manufacturing_costs',
                  title='Manufacturing Costs Distribution per Product Type',
                  labels={'product_type': 'Product Type', 'manufacturing_costs': 'Manufacturing Costs'},
                  color='product_type')
st.plotly_chart(fig6, width="stretch")
st.markdown("   ")

fig7 = px.bar(filtered_df.groupby(['supplier_name', 'inspection_results'])['defect_rates'].mean().reset_index(),
                  x='supplier_name', y='defect_rates', color='inspection_results',
                  barmode='group',
                  title='Average Defect Rates by Supplier and Inspection Result',
                  labels={'supplier_name': 'Supplier Name', 'defect_rates': 'Average Defect Rate', 'inspection_results': 'Inspection Result'},
                  hover_data={'defect_rates': ':.2f'})
st.plotly_chart(fig7, width="stretch")
st.markdown("   ")

st.subheader("🚚 :red[Logistics & Inventory Deep Dive]", divider="red")
st.markdown("   ")
avg_lead_times = filtered_df.groupby('supplier_name')[['lead_times', 'manufacturing_lead_time']].mean().reset_index()
fig8 = px.bar(avg_lead_times.melt(id_vars='supplier_name', var_name='Lead Time Type', value_name='Average Days'),
                  x='supplier_name', y='Average Days', color='Lead Time Type', barmode='group',
                  title='Average General & Manufacturing Lead Times by Supplier',
                  labels={'supplier_name': 'Supplier Name', 'Average Days': 'Average Lead Time (Days)'})
st.plotly_chart(fig8, width="stretch")
st.markdown("   ")

fig9 = px.scatter(filtered_df, x='production_volumes', y='manufacturing_costs',
                      color='product_type', size='revenue_generated',
                      hover_name='sku',
                      title='Production Volume vs. Manufacturing Costs',
                      labels={'production_volumes': 'Production Volume', 'manufacturing_costs': 'Manufacturing Costs', 'product_type': 'Product Type'},
                      log_x=True, log_y=True, size_max=60)
st.plotly_chart(fig9, width="stretch")
st.markdown("   ")

# Aggregate to product type level to get a clearer picture for this relationship
stock_sales_agg = filtered_df.groupby('product_type').agg(
        avg_stock_levels=('stock_levels', 'mean'),
        total_products_sold=('number_of_products_sold', 'sum')
).reset_index()
fig10 = px.scatter(stock_sales_agg, x='total_products_sold', y='avg_stock_levels',
                       color='product_type', size='avg_stock_levels',
                       hover_name='product_type',
                       title='Average Stock Levels vs. Total Products Sold by Product Type',
                       labels={'total_products_sold': 'Total Products Sold', 'avg_stock_levels': 'Average Stock Levels'},
                       size_max=60)
st.plotly_chart(fig10, width="stretch")
st.markdown("   ")

st.sidebar.markdown("---")
st.sidebar.info("Analyze your supply chain data for better decision-making!")
# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p><strong>🚚 Supply Chain Data Analysis</strong></p>
    <p>Explore key metrics, product performance, supply chain efficiency, logistics and iventory.</p>
    <p style='font-size: 0.9rem;'>Navigate using the sidebar to explore different datasets</p>
</div>
""", unsafe_allow_html=True)
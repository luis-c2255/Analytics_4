import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np # For numerical operations
from utils.theme import Components

st.set_page_config(
        page_title=f"Amazon Sales Dataset Analysis",
        page_icon= "🛒",
        layout="wide",
        initial_sidebar_state="expanded"
    )
try:
    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
except FileNotFoundError:
    pass

st.markdown(
    Components.page_header("🛒  Amazon Sales Dataset Analysis"), unsafe_allow_html=True
)

@st.cache_data
def load_data():
    # Load the dataset
    df = pd.read_csv('amazon_sales_dataset.csv')
    
    # Convert 'Order Date' to datetime
    df['order_date'] = pd.to_datetime(df['order_date'])
    
    numeric_cols = ['price', 'discount_percent', 'quantity_sold', 'rating', 'review_count', 
                    'discounted_price', 'total_revenue']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        
    df.dropna(subset=['price', 'quantity_sold', 'total_revenue', 'rating'], inplace=True)
    return df
df = load_data()

# Date range Filters
st.sidebar.header("Filter Options")

min_date = df['order_date'].min().date()
max_date = df['order_date'].max().date()
date_range = st.sidebar.slider(
    "Select Date Range",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date),
    format="YYYY-MM-DD"
)
df_filtered = df[(df['order_date'].dt.date >= date_range[0]) & (df['order_date'].dt.date <= date_range[1])]

selected_categories = st.sidebar.multiselect(
    "Select Product Categories",
    options=df['product_category'].unique(),
    default=df['product_category'].unique()
)
df_filtered = df_filtered[df_filtered['product_category'].isin(selected_categories)]

selected_regions = st.sidebar.multiselect(
    "Select Customer Regions",
    options=df['customer_region'].unique(),
    default=df['customer_region'].unique()
)
df_filtered = df_filtered[df_filtered['customer_region'].isin(selected_regions)]

st.subheader(":rainbow[Key Metrics]", divider="rainbow")


total_sales = df['total_revenue'].sum()
total_products_sold = df['quantity_sold'].sum()
avg_rating = df['rating'].mean()
avg_order_value = df['total_revenue'].mean()
prev_total_sales = total_sales * 0.95
prev_total_products_sold = total_products_sold * 0.96
prev_avg_rating = avg_rating - 0.1
prev_avg_order_value = avg_order_value * 0.97


col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(
        Components.metric_card(
            title="Total Revenue",
            value=f"${total_sales:,.2f}",
            delta=f"+{((total_sales / prev_total_sales) - 1) * 100:.1f}%" if prev_total_sales else "N/A",
            card_type="success"
        ), unsafe_allow_html=True
    )
with col2:
    st.markdown(
        Components.metric_card(
            title="Products Sold",
            value=f"{int(total_products_sold):,}",
            delta=f"+{int(total_products_sold - prev_total_products_sold):,}" if prev_total_products_sold else "N/A",
            card_type="info"
        ), unsafe_allow_html=True
    )
with col3:
    st.markdown(
        Components.metric_card(
            title="Average Rating",
            value=f"{avg_rating:.2f} ⭐",
            delta=f"+{(avg_rating - prev_avg_rating):.1f}" if prev_avg_rating else "N/A",
            card_type="success" if (avg_rating - prev_avg_rating) >= 0 else "error"
        ), unsafe_allow_html=True
    )
with col4:
    st.markdown(
        Components.metric_card(
            title="Average Order Value",
            value=f"${avg_order_value:,.2f}",
            delta=f"+{((avg_order_value / prev_avg_order_value) - 1) * 100:.1f}%" if prev_avg_order_value else "N/A",
            card_type="info"
        ),unsafe_allow_html=True
    )
st.markdown("   ")        
st.subheader(":blue[Overview & Performance]", divider="blue")
st.markdown("   ")

category_revenue = df_filtered.groupby('product_category')['total_revenue'].sum().reset_index()
fig_category_revenue = px.bar(
    category_revenue.sort_values('total_revenue', ascending=False),
    x='total_revenue',
    y='product_category',
    orientation='h',
    title='Total Revenue by Product Category',
    labels={'total_revenue': 'Total Revenue ($)', 'product_category': 'Product Category'},
    color='total_revenue',
    text_auto=True,
    color_continuous_scale=px.colors.sequential.Viridis
)
fig_category_revenue.update_layout(yaxis_title=None)
st.plotly_chart(fig_category_revenue, width="stretch")
st.markdown("   ")

region_quantity = df_filtered.groupby("customer_region")["quantity_sold"].sum().reset_index()
fig_region_quantity = px.bar(
            region_quantity.sort_values("quantity_sold", ascending=False),
            x="customer_region",
            y="quantity_sold",
            title="Total Quantity Sold by Customer Region",
            labels={"quantity_sold": "Quantity Sold", "customer_region": "Customer Region"},
            color="quantity_sold",
            text_auto=True,
            color_continuous_scale=px.colors.sequential.Plasma
        )
st.plotly_chart(fig_region_quantity, width="stretch")
st.markdown("   ")

st.subheader(":orange[Sales & Discounts]", divider="orange")
st.markdown("   ")

df_filtered["year_month"] = df_filtered["order_date"].dt.to_period("M").astype(str)
monthly_revenue = df_filtered.groupby("year_month")["total_revenue"].sum().reset_index()
monthly_revenue["year_month_dt"] = pd.to_datetime(monthly_revenue["year_month"])
monthly_revenue = monthly_revenue.sort_values("year_month_dt")

fig_monthly_revenue = px.line(
            monthly_revenue,
            x="year_month_dt",
            y="total_revenue",
            title="Monthly Total Revenue Over Time",
            labels={"year_month_dt": "Date", "total_revenue": "Total Revenue ($)"},
            markers=True
        )
fig_monthly_revenue.update_xaxes(dtick="M1", tickformat="%b\n%Y")
st.plotly_chart(fig_monthly_revenue, width="stretch")
st.markdown("   ")

if len(df_filtered) > 10000:
    df_sample = df_filtered.sample(n=10000, random_state=42)
else:
    df_sample = df_filtered
    
    fig_discount_scatter = px.scatter(
            df_sample,
            x="discount_percent",
            y="total_revenue",
            color="product_category",
            hover_name="order_id",
            title="Discount Percentage vs. Total Revenue per Order",
            labels={"discount_percent": "Discount Percentage (%)", "total_revenue": "Total Revenue ($)"},
            trendline="ols"
        )
    st.plotly_chart(fig_discount_scatter, width="stretch")
    

st.subheader(":yellow[Product Deep Dive]", divider="yellow")
st.markdown("    ")

product_revenue = df_filtered.groupby(['product_id', 'product_category'])["total_revenue"].sum().reset_index()
top_products = product_revenue.sort_values("total_revenue", ascending=False).head(10)

fig_top_products = px.bar(
            top_products,
            x="total_revenue",
            y="product_id",
            color="product_category",
            orientation="h",
            title="Top 10 Products by Total Revenue",
            labels={"total_revenue": "Total Revenue ($)", "product_id": "Product ID"},
            text_auto=True,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
fig_top_products.update_layout(yaxis={'categoryorder':'total ascending'})
st.plotly_chart(fig_top_products, width="stretch")
st.markdown("    ")

fig_price_dist = px.histogram(
            df_filtered,
            x="price",
            nbins=50, # More bins for better granularity
            title="Distribution of Original Product Prices",
            labels={"price": "Original Price ($)"},
            color_discrete_sequence=['#EF553B']
        )
fig_price_dist.update_traces(marker_line_width=1, marker_line_color="white")
st.plotly_chart(fig_price_dist, width="stretch")


st.subheader(":red[Customer Feedback & Region Detail]", divider="red")
st.markdown("    ")

if len(df_filtered) > 15000:
    df_sample_feedback = df_filtered.sample(n=15000, random_state=42)
else:
    df_sample_feedback = df_filtered
    
    fig_rating_review = px.scatter(
            df_sample_feedback,
            x="review_count",
            y="rating",
            color="product_category",
            hover_name="product_id",
            title="Product Rating vs. Review Count",
            labels={"review_count": "Number of Reviews", "rating": "Average Rating"}
        )
    st.plotly_chart(fig_rating_review, width="stretch")
    st.markdown("    ")
    
regional_category_revenue = df_filtered.groupby(["customer_region", "product_category"])["total_revenue"].sum().reset_index()

fig_regional_category = px.bar(
            regional_category_revenue,
            x="customer_region",
            y="total_revenue",
            color="product_category",
            title="Total Revenue by Region and Product Category",
            labels={"total_revenue": "Total Revenue ($)", "customer_region": "Customer Region"},
            text_auto=True,
            hover_data=["product_category", "total_revenue"]
        )
st.plotly_chart(fig_regional_category, width="stretch")

st.subheader(":green[Raw Data]", divider="green")
st.markdown("    ")
st.dataframe(df_filtered)
# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p><strong>🛒  Amazon Sales Dataset Analysis</strong></p>
    <p>Explore key metrics, performance, sales & discounts, product, customer feedback and regional analysis.</p>
    <p style='font-size: 0.9rem;'>Navigate using the sidebar to explore different datasets</p>
</div>
""", unsafe_allow_html=True)
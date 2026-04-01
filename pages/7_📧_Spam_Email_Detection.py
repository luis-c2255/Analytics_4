import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np # For correlation matrix
from utils.theme import Components

st.set_page_config(
        page_title=f"Spam Email Detection Analysis",
        page_icon= "📧",
        layout="wide",
        initial_sidebar_state="expanded"
    )
try:
    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
except FileNotFoundError:
    pass

st.markdown(
    Components.page_header("📧  Spam Email Detection Analysis"), unsafe_allow_html=True
)

@st.cache_data
def load_data():
    df = pd.read_csv("spam_email_dataset.csv")
    df['is_spam_text'] = df['label'].apply(lambda x: "Spam" if x == 1 else "Not Spam")
    return df

df = load_data()

st.sidebar.header("Filter Options")

label_filter = st.sidebar.multiselect(
    "Select Email Type",
    options=df['label'].unique(),
    default=df['label'].unique(),
    format_func=lambda x: "Spam" if x == 1 else "Not Spam"
)

top_n_domains = st.sidebar.slider("Show Top N Sender Domains (for analysis)", 5, 30, 10)
all_top_domains = df['sender_domain'].value_counts().nlargest(top_n_domains).index.tolist()
domain_filter = st.sidebar.multiselect(
    "Select Sender Domain (for charts)",
    options=all_top_domains,
    default=all_top_domains
)

min_rep_score, max_rep_score = st.sidebar.slider(
    "Sender Reputation Score Range",
    float(df['sender_reputation_score'].min()),
    float(df['sender_reputation_score'].max()),
    (float(df['sender_reputation_score'].min()), float(df['sender_reputation_score'].max()))
)

filtered_df = df[df['label'].isin(label_filter)]
filtered_df = filtered_df[filtered_df['sender_domain'].isin(domain_filter)]
filtered_df = filtered_df[
    (filtered_df['sender_reputation_score'] >= min_rep_score) &
    (filtered_df['sender_reputation_score'] <= max_rep_score)
]

st.subheader(":rainbow[Key Metrics (Overall Dataset)]", divider="rainbow")
st.markdown("   ")
col1, col2, col3 = st.columns(3)
with col1:
    total_emails = df.shape[0]
    st.markdown(
        Components.metric_card(
            title="Total Emails Analyzed",
            value=f"{total_emails:,}",
            delta="+5% (est.)",
            card_type="info"
        ), unsafe_allow_html=True
    )
with col2:
    spam_emails = df[df['label'] == 1].shape[0]
    ham_emails = df[df['label'] == 0].shape[0]
    st.markdown(
        Components.metric_card(
            title="Spam Emails Count",
            value=f"{spam_emails:,}",
            delta="+12% (est.)",
            card_type="error"
        ), unsafe_allow_html=True
    )
with col3:
    spam_rate = (spam_emails / total_emails) * 100 if total_emails > 0 else 0
    st.markdown(
        Components.metric_card(
            title="Overall Spam Rate",
            value=f"{spam_rate:.2f}%",
            delta="+1.5% (est.)",
            card_type="error"
        ), unsafe_allow_html=True
    )
st.markdown("   ")
col4, col5 = st.columns(2)    
with col4:
    avg_spam_rep = df[df['label'] == 1]['sender_reputation_score'].mean() if spam_emails > 0 else 0
    st.markdown(
        Components.metric_card(
            title="Avg Sender Rep (Spam)",
            value=f"{avg_spam_rep:.2f}",
            delta="-0.05 (est.)",
            card_type="error"
        ), unsafe_allow_html=True
    )
with col5:
    avg_ham_rep = df[df['label'] == 0]['sender_reputation_score'].mean() if ham_emails > 0 else 0
    st.markdown(
        Components.metric_card(
            title="Avg. Sender Rep. (Not Spam)",
            value=f"{avg_ham_rep:.2f}",
            delta="+0.02 (est.)",
            card_type="success"
        ), unsafe_allow_html=True
    )
st.markdown("   ")


st.subheader(":green[Overview & Distributions]", divider="green")
st.markdown("   ")
st.markdown(":green-background['Key Metrics']")
total_filtered = filtered_df.shape[0]
spam_filtered = filtered_df[filtered_df['label'] == 1].shape[0]
spam_rate_filtered = (spam_filtered / total_filtered) * 100 if total_filtered > 0 else 0

col1, col2, col3 = st.columns(3)
with col1: 
    st.markdown(
        Components.metric_card(
            title="Filtered Emails",
            value=f"{total_filtered:,}",
            delta="- (based on filters)",
            card_type="info"
        ), unsafe_allow_html=True
    )
with col2: 
    st.markdown(
        Components.metric_card(
            title="Filtered Spam Rate",
            value=f"{spam_rate_filtered:.2f}%",
            delta="+/- (varies by filter)",
            card_type="warning"
        ), unsafe_allow_html=True
    )
with col3: 
    st.markdown(
        Components.metric_card(
            title="Avg. Words (All)",
            value=f"{filtered_df['num_words'].mean():.1f}",
            delta="+/- (varies by filter)",
            card_type="info"
        ), unsafe_allow_html=True
    )
st.markdown("   ")

st.markdown(":green-background[Email Type Distribution]")
email_type_counts = filtered_df['is_spam_text'].value_counts().reset_index()
email_type_counts.columns = ['Email Type', 'count']

fig_pie = px.pie(
    email_type_counts, 
    values='count', 
    names='Email Type',
    title='Distribution of Email Types (Filtered)',
    color_discrete_map={"Spam": "salmon", "Not Spam": "lightgreen"}
)
st.plotly_chart(fig_pie, width="stretch")
st.markdown("   ")

st.markdown(":green-background[Distribution of Email Lengths (Words)]")

fig_hist_words = px.histogram(
    filtered_df, 
    x='num_words', 
    color='is_spam_text',
    title='Distribution of Number of Words by Email Type (Filtered)',
    labels={'is_spam_text': 'Email Type'},
    nbins=50,
    color_discrete_map={"Not Spam": 'lightgreen', "Spam": 'salmon'}
)
fig_hist_words.update_layout(xaxis_title="Number of Words", yaxis_title="Count")
st.plotly_chart(fig_hist_words, width="stretch")
st.markdown("   ")

st.markdown(":green-background[Sender Reputation Score by Email Type]")

fig_box_rep = px.box(
    filtered_df, 
    y='sender_reputation_score', 
    x='is_spam_text',
    title='Sender Reputation Score Distribution by Email Type (Filtered)',
    labels={'is_spam_text': 'Email Type'},
    color='is_spam_text',
    color_discrete_map={"Not Spam": 'lightgreen', "Spam": 'salmon'}
)
fig_box_rep.update_layout(xaxis_title="Email Type", yaxis_title="Reputation Score")
st.plotly_chart(fig_box_rep, width="stretch")

st.subheader(":orange[Spam Feature Breakdown]", divider="orange")
st.markdown("   ")

spam_only_df = filtered_df[filtered_df['label'] == 1]
spam_with_susp_link = spam_only_df['has_suspicious_link'].sum()
spam_with_money_terms = spam_only_df['contains_money_terms'].sum()
avg_spam_links = spam_only_df['num_links'].mean() if not spam_only_df.empty else 0

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(
        Components.metric_card(
            title="Spam with Susp. Link",
            value=f"{spam_with_susp_link:,}",
            delta="+ (high indicator)",
            card_type="error"
        ), unsafe_allow_html=True
    )
with col2:
    st.markdown(
        Components.metric_card(
            title="Spam with Money Terms",
            value=f"{spam_with_money_terms:,}",
            delta="+ (high indicator)",
            card_type="error"
        ), unsafe_allow_html=True
    )
with col3:
    st.markdown(
        Components.metric_card(
            title="Avg. Links in Spam",
            value=f"{avg_spam_links:.1f}",
            delta="+0.5 (est.)",
            card_type="warning"
        ), unsafe_allow_html=True
    )
st.markdown("   ")
st.markdown(":orange-background[Contains Suspicious Links]")
susp_link_counts = spam_only_df['has_suspicious_link'].value_counts().reset_index()
susp_link_counts.columns = ['has_suspicious_link', 'count']
susp_link_counts['label_text'] = susp_link_counts['has_suspicious_link'].apply(lambda x: "Yes" if x == 1 else "No")
fig_susp_link = px.pie(
    susp_link_counts, 
    values='count', 
    names='label_text',
    title='Spam: Has Suspicious Link?',
    color_discrete_map={"Yes": "salmon", "No": "lightgrey"}
)
st.plotly_chart(fig_susp_link, width="stretch")
st.markdown("   ")
st.markdown(":orange-background[Contains Money Terms]")

money_terms_counts = spam_only_df['contains_money_terms'].value_counts().reset_index()
money_terms_counts.columns = ['contains_money_terms', 'count']
money_terms_counts['label_text'] = money_terms_counts['contains_money_terms'].apply(lambda x: "Yes" if x == 1 else "No")

fig_money_terms = px.pie(
    money_terms_counts, 
    values='count', 
    names='label_text',
    title='Spam: Contains Money Terms?',
    color_discrete_map={"Yes": "darkorange", "No": "lightgrey"}
)
st.plotly_chart(fig_money_terms, width="stretch")
st.markdown("   ")
st.markdown(":orange-background[Contains Urgency Terms]")
urgency_terms_counts = spam_only_df['contains_urgency_terms'].value_counts().reset_index()
urgency_terms_counts.columns = ['contains_urgency_terms', 'count']
urgency_terms_counts['label_text'] = urgency_terms_counts['contains_urgency_terms'].apply(lambda x: "Yes" if x == 1 else "No")

fig_urgency_terms = px.pie(
    urgency_terms_counts, 
    values='count', 
    names='label_text',
    title='Spam: Contains Urgency Terms?',
    color_discrete_map={"Yes": "red", "No": "lightgrey"}
)
st.plotly_chart(fig_urgency_terms, width="stretch")
st.markdown("   ")

st.subheader(":orange-background[Number of Links in Spam Emails]")
fig_links = px.histogram(
    spam_only_df, 
    x='num_links',
    title='Distribution of Number of Links in Spam Emails',
    nbins=20,
    color_discrete_sequence=['salmon']
)
st.plotly_chart(fig_links, width="stretch")
st.markdown("   ")
st.subheader(":orange-background[Number of Exclamation Marks in Spam Emails]")

fig_exclamations = px.histogram(
    spam_only_df, 
    x='num_exclamation_marks',
    title='Distribution of Exclamation Marks in Spam Emails',
    nbins=10,
    color_discrete_sequence=['purple']
)
st.plotly_chart(fig_exclamations, width="stretch")
st.markdown("   ")
st.subheader(":orange-background[Number of Attachments in Spam Emails]")

attachments_counts = spam_only_df['num_attachments'].value_counts().reset_index()
attachments_counts.columns = ['num_attachments', 'count']
fig_attachments = px.bar(
    attachments_counts.sort_values('num_attachments'), 
    x='num_attachments', 
    y='count',
    title='Distribution of Number of Attachments in Spam Emails',
    color_discrete_sequence=['teal']
)
st.plotly_chart(fig_attachments, width="stretch")
st.markdown("   ")

st.subheader(":violet[Temporal Patterns]", divider="violet")
st.markdown("   ")

most_common_hour_spam = filtered_df[filtered_df['label'] == 1]['email_hour'].mode()[0] if not filtered_df[filtered_df['label'] == 1].empty else 'N/A'
most_common_day_spam = filtered_df[filtered_df['label'] == 1]['email_day_of_week'].mode()[0] if not filtered_df[filtered_df['label'] == 1].empty else 'N/A'
day_of_week_map_for_metrics = {0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu', 4: 'Fri', 5: 'Sat', 6: 'Sun'}

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(
        Components.metric_card(
            title="Peak Spam Hour",
            value=f"{most_common_hour_spam}:00",
            delta="+ (consistent)",
            card_type="warning"
        ), unsafe_allow_html=True
    )
with col2:
    st.markdown(
        Components.metric_card(
            title="Peak Spam Day",
            value=f"{day_of_week_map_for_metrics.get(most_common_day_spam, 'N/A')}",
            delta="+ (consistent)",
            card_type="warning"
        ), unsafe_allow_html=True
    )
with col3:
    st.markdown(
        Components.metric_card(
            title="Weekend Spam Rate",
            value=f"{filtered_df[filtered_df['is_weekend'] == 1]['label'].mean()*100:.1f}%" if not filtered_df[filtered_df['is_weekend'] == 1].empty else "0%",
            delta="+/- (varies)",
            card_type="info"
        ), unsafe_allow_html=True
    )
st.markdown("   ")
st.subheader(":violet-background[Email Activity by Day of Week (Spam vs. Not Spam)]")

day_of_week_map = {0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu', 4: 'Fri', 5: 'Sat', 6: 'Sun'}
day_of_week_counts = filtered_df.groupby(['email_day_of_week', 'is_spam_text']).size().reset_index(name='count')
day_of_week_counts['day_name'] = day_of_week_counts['email_day_of_week'].map(day_of_week_map)
        
fig_day = px.bar(
    day_of_week_counts, 
    x='day_name', 
    y='count', 
    color='is_spam_text',
    title='Email Activity by Day of Week (Filtered)',
    labels={'day_name': 'Day of Week', 'count': 'Number of Emails'},
    category_orders={'day_name': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']},
    color_discrete_map={"Spam": "salmon", "Not Spam": "lightgreen"}
)
st.plotly_chart(fig_day, width="stretch")
st.markdown("   ")
st.subheader(":violet-background[Email Activity by Hour of Day (Spam vs. Not Spam)]")

hourly_counts = filtered_df.groupby(['email_hour', 'is_spam_text']).size().reset_index(name='count')
fig_hour = px.line(
    hourly_counts, 
    x='email_hour', 
    y='count', 
    color='is_spam_text',
    title='Email Activity by Hour of Day (Filtered)',
    labels={'email_hour': 'Hour of Day (24-hour)', 'count': 'Number of Emails'},
    markers=True,
    color_discrete_map={"Spam": "salmon", "Not Spam": "lightgreen"}
)
st.plotly_chart(fig_hour, width="stretch")

st.subheader(":red[Feature Relationships & Domains]", divider="red")
st.markdown("   ")
num_links_spam = filtered_df[filtered_df['label']==1]['num_links'].max() if not filtered_df[filtered_df['label']==1].empty else 0
num_excl_marks_spam = filtered_df[filtered_df['label']==1]['num_exclamation_marks'].max() if not filtered_df[filtered_df['label']==1].empty else 0
spam_domains_count = filtered_df[filtered_df['label'] == 1]['sender_domain'].nunique()

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(
        Components.metric_card(
            title="Max Links in Spam (Filtered)",
            value=f"{num_links_spam:,}",
            delta="+ (high alert)",
            card_type="error"
        ), unsafe_allow_html=True
    )
with col2:
    st.markdown(
        Components.metric_card(
            title="Max Excl. Marks in Spam",
            value=f"{num_excl_marks_spam:,}",
            delta="+ (high alert)",
            card_type="error"
        ), unsafe_allow_html=True
    )
with col3:
    st.markdown(
        Components.metric_card(
            title="Unique Spam Domains (Filtered)",
            value=f"{spam_domains_count:,}",
            delta="- (more consolidation)",
            card_type="info"
        ), unsafe_allow_html=True
    )
st.subheader(":red-background[Relationship: Number of Words vs. Number of Characters]")
fig_scatter_words_chars = px.scatter(
    filtered_df, 
    x='num_words', 
    y='num_characters', 
    color='is_spam_text',
    title='Number of Words vs. Characters by Email Type (Filtered)',
    labels={'is_spam_text': 'Email Type'},
    hover_data=['subject'],
    color_discrete_map={"Not Spam": 'lightgreen', "Spam": 'salmon'}
)
st.plotly_chart(fig_scatter_words_chars, width="stretch")
st.markdown("   ")

st.subheader(":red-background[Relationship: Number of Links vs. Number of Exclamation Marks]")
fig_scatter_links_excl = px.scatter(
    filtered_df, 
    x='num_links', 
    y='num_exclamation_marks', 
    color='is_spam_text',
    title='Number of Links vs. Exclamation Marks by Email Type (Filtered)',
    labels={'is_spam_text': 'Email Type'},
    hover_data=['subject'],
    color_discrete_map={"Not Spam": 'lightgreen', "Spam": 'salmon'}
)
st.plotly_chart(fig_scatter_links_excl, width="stretch")
st.markdown("   ")
st.subheader(":red-background[Distribution of Number of Recipients by Email Type]")
fig_violin_recipients = px.violin(
    filtered_df, 
    x='is_spam_text', 
    y='num_recipients', 
    color='is_spam_text',
    title='Number of Recipients Distribution by Email Type (Filtered)',
    labels={'is_spam_text': 'Email Type', 'num_recipients': 'Number of Recipients'},
    box=True, # show box plot inside violin
    color_discrete_map={"Not Spam": 'lightgreen', "Spam": 'salmon'}
)
st.plotly_chart(fig_violin_recipients, width="stretch")
st.markdown("   ")
st.subheader(":red-background[Correlation Matrix of Numerical Features]")
numerical_df = filtered_df[['num_words', 'num_characters', 'num_exclamation_marks',
                            'num_links', 'num_attachments', 'sender_reputation_score',
                            'num_recipients', 'label']].copy()
numerical_df.rename(columns={'label': 'is_spam'}, inplace=True)

correlation_matrix = numerical_df.corr()
fig_heatmap = px.heatmap(
    correlation_matrix,
    text_auto=True,
    color_continuous_scale=px.colors.sequential.Viridis,
    title='Correlation Matrix of Numerical Features (Filtered)')
st.plotly_chart(fig_heatmap,  width="stretch")
st.markdown("   ")

st.subheader(":red-background[Top Sender Domains by Spam Count]")

spam_domain_counts = filtered_df[filtered_df['label'] == 1]['sender_domain'].value_counts().nlargest(top_n_domains).reset_index()
spam_domain_counts.columns = ['Sender Domain', 'Spam Count']

fig_domain_bar = px.bar(
    spam_domain_counts.sort_values('Spam Count', ascending=True), 
    y='Sender Domain', 
    x='Spam Count',
    title=f'Top {top_n_domains} Sender Domains by Spam Count (Filtered)',
    color_discrete_sequence=['darkred']
)
st.plotly_chart(fig_domain_bar, width="stretch")
st.markdown("   ")


# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p><strong>📧  Spam Email Detection Analysis</strong></p>
    <p>Explore key metrics, population trends, distribution, composition and growth.</p>
    <p style='font-size: 0.9rem;'>Navigate using the sidebar to explore different datasets</p>
</div>
""", unsafe_allow_html=True)
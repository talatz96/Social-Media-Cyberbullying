import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Social Media Bullying Trends", layout="wide")

# Load dataset
df = pd.read_csv("labeled_reddit.csv")
df['Platform'] = "Reddit"
df = df.rename(columns={'CyberHate': 'Bullying'})  
df = df.rename(columns={'Title': 'Topic'}) 
df['Timestamp (UTC)'] = pd.to_datetime(df['Timestamp (UTC)'])
df['Date'] = df['Timestamp (UTC)'].dt.date  # extract date only
df['Bullying'] = df['Bullying'].astype(int)

st.title("📊 Social Media Bullying Trends Dashboard")

# === Sidebar Filters ===
st.sidebar.header("🔍 Filter Data")
date_range = st.sidebar.date_input(
    "Select Date Range",
    [df['Date'].min(), df['Date'].max()]
)

platforms = st.sidebar.multiselect("Platforms", df['Platform'].unique(), default=df['Platform'].unique())
subreddits = st.sidebar.multiselect("Subreddits", df['Subreddit'].unique(), default=df['Subreddit'].unique())
bullying_only = st.sidebar.checkbox("Show only bullying posts")

# === Filter Logic ===
start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
mask = (
    (df['Timestamp (UTC)'] >= start_date) &
    (df['Timestamp (UTC)'] <= end_date) &
    (df['Platform'].isin(platforms)) &
    (df['Subreddit'].isin(subreddits))
)
if bullying_only:
    mask &= df['Bullying'] == 1

filtered_df = df[mask]

# === KPIs ===
st.markdown("### 📌 Key Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Posts", len(filtered_df))
col2.metric("% Bullying Posts", f"{(filtered_df['Bullying'].mean()) * 100:.1f}%")
col3.metric("Most Active Subreddit", filtered_df['Subreddit'].mode().values[0] if not filtered_df.empty else "N/A")
col4.metric("Top Platform", filtered_df['Platform'].mode().values[0] if not filtered_df.empty else "N/A")

# === Trend Over Time ===
st.markdown("### 📈 Bullying Trend Over Time")
trend = filtered_df.groupby('Date')['Bullying'].sum().reset_index()
fig_trend = px.line(trend, x='Date', y='Bullying', title="Bullying Posts per Day")
st.plotly_chart(fig_trend, use_container_width=True)

# === Top Subreddits ===
st.markdown("### 📊 Top Subreddits by Bullying Posts")
subreddit_stats = filtered_df[filtered_df['Bullying'] == 1]['Subreddit'].value_counts().reset_index()
subreddit_stats.columns = ['Subreddit', 'Bullying Posts']
fig_subreddit = px.bar(subreddit_stats, x='Subreddit', y='Bullying Posts')
st.plotly_chart(fig_subreddit, use_container_width=True)

# === Engagement Chart ===
st.markdown("### 🔥 Engagement by Score vs Comments")
fig_engagement = px.scatter(
    filtered_df,
    x='Score',
    y='Comments',
    color=filtered_df['Bullying'].map({1: 'Bullying', 0: 'Non-Bullying'}),
    hover_data=['Topic', 'Subreddit', 'URL'],
    title="Score vs Comments Engagement"
)
st.plotly_chart(fig_engagement, use_container_width=True)

# === Data Table ===
st.markdown("### 📄 Raw Data")
st.dataframe(filtered_df[['Timestamp (UTC)', 'Topic', 'Subreddit', 'Score', 'Comments', 'Bullying', 'Platform', 'URL']])

import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Sample set of bullying-related keywords (expand as needed)
BULLYING_KEYWORDS = ['hate', 'attack', 'abuse', 'bully', 'harassment', 'violence', 'troll']

st.set_page_config(page_title="Social Media Bullying Trends", layout="wide")

# Load dataset
df = pd.read_csv("labeled_reddit.csv")
df['Platform'] = "Reddit"
df = df.rename(columns={'CyberHate': 'Bullying'})  
df = df.rename(columns={'Title': 'Topic'}) 
df['Timestamp (UTC)'] = pd.to_datetime(df['Timestamp (UTC)'])
df['Date'] = df['Timestamp (UTC)'].dt.date  # extract date only
df['Hour'] = df['Timestamp (UTC)'].dt.hour  # extract hour for more granular trend
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

# === Input Section for User to Classify Bullying or Not ===
st.markdown("### 📝 Enter a Post Title or Comment to Check for Bullying")
user_input = st.text_area("Enter text here:")

def is_bullying(text):
    """ Simple keyword-based classification for bullying detection """
    # Convert the input text to lowercase for case-insensitive comparison
    text = text.lower()
    for keyword in BULLYING_KEYWORDS:
        if keyword in text:
            return True
    return False

if user_input:
    # Check if the input text contains any bullying-related keywords
    if is_bullying(user_input):
        st.success("✅ This is likely bullying.")
    else:
        st.info("🔍 This doesn't appear to be bullying.")

# === KPIs ===
st.markdown("### 📌 Key Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Posts", len(filtered_df))
col2.metric("% Bullying Posts", f"{(filtered_df['Bullying'].mean()) * 100:.1f}%")
col3.metric("Most Active Subreddit", filtered_df['Subreddit'].mode().values[0] if not filtered_df.empty else "N/A")
col4.metric("Top Platform", filtered_df['Platform'].mode().values[0] if not filtered_df.empty else "N/A")

# === Bullying Trend by Month and Year ===
st.markdown("### 📈 Bullying Trend by Month and Year")
filtered_df['Year-Month'] = filtered_df['Timestamp (UTC)'].dt.to_period('M').astype(str)
trend_monthly = filtered_df[filtered_df['Bullying'] == 1].groupby('Year-Month').size().reset_index(name='Bullying Posts')
fig_trend_monthly = px.line(trend_monthly, x='Year-Month', y='Bullying Posts', 
                            title="Bullying Posts per Month and Year", 
                            labels={'Year-Month': 'Month and Year', 'Bullying Posts': 'Number of Bullying Posts'})
fig_trend_monthly.update_layout(xaxis_title="Month and Year", yaxis_title="Bullying Posts")
st.plotly_chart(fig_trend_monthly, use_container_width=True)

# === Top Subreddits ===
st.markdown("### 📊 Top Subreddits by Bullying Posts")
subreddit_stats = filtered_df[filtered_df['Bullying'] == 1]['Subreddit'].value_counts().reset_index()
subreddit_stats.columns = ['Subreddit', 'Bullying Posts']
fig_subreddit = px.bar(subreddit_stats, x='Subreddit', y='Bullying Posts', title="Top Subreddits with Bullying Posts")
st.plotly_chart(fig_subreddit, use_container_width=True)

# === Engagement by Score vs Comments (Bar Chart) ===
st.markdown("### 🔥 Engagement by Score vs Comments")
fig_engagement_bar = px.bar(
    filtered_df,
    x='Score',
    y='Comments',
    color=filtered_df['Bullying'].map({1: 'Bullying', 0: 'Non-Bullying'}),
    hover_data=['Topic', 'Subreddit', 'URL'],
    title="Score vs Comments Engagement (Bar Chart)"
)
st.plotly_chart(fig_engagement_bar, use_container_width=True)

# === Word Cloud for Topics ===
st.markdown("### 🧠 Word Cloud of Topics")
wordcloud_data = ' '.join(filtered_df['Topic'].dropna().astype(str))  # Join all topics into a single string
wordcloud = WordCloud(width=800, height=400, background_color='white').generate(wordcloud_data)

# Plot the WordCloud image
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
st.pyplot(plt)

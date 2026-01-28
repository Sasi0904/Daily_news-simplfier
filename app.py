import streamlit as st
from news_paper_summarizer import (
    NewsConfig,
    NewsFetcher,
    NewsSummarizer,
    VoiceReader
)

# Page config
st.set_page_config(
    page_title="Daily News Simplifier",
    page_icon="📰",
    layout="wide"
)

# Title
st.title("📰 Daily News Simplifier")
st.caption("Fast • Clean • Easy-to-read news summaries")

# Sidebar controls
st.sidebar.header("🔧 Settings")

category = st.sidebar.selectbox(
    "Select Category",
    ["tech", "sports", "politics", "entertainment", "business", "health", "science"]
)

country = st.sidebar.selectbox(
    "Select Country",
    ["us", "in", "uk", "ca", "au"]
)

enable_voice = st.sidebar.checkbox("🔊 Read Aloud")

fetch_button = st.sidebar.button("🔄 Fetch News")

# Initialize backend
config = NewsConfig()
fetcher = NewsFetcher(config)
summarizer = NewsSummarizer()
voice = VoiceReader()

# Fetch and display news
if fetch_button:
    with st.spinner("Fetching latest news..."):
        articles = fetcher.fetch_news(category, country)

    if not articles:
        st.error("❌ No news articles found.")
    else:
        st.success(f"✅ Found {len(articles)} articles")

        for i, article in enumerate(articles, 1):
            with st.container():
                st.markdown(f"## {i}. {article.get('title','No Title')}")
                
                if article.get("url"):
                    st.markdown(f"[🔗 Read full article]({article['url']})")

                summary = summarizer.summarize_article(article)

                for bullet in summary:
                    st.markdown(bullet)

                if enable_voice and voice.engine:
                    if st.button(f"🔊 Read Article {i}", key=i):
                        voice.speak(article.get("title", ""))
                        for b in summary:
                            voice.speak(b)

                st.divider()

import streamlit as st
from news_paper_summarizer import (
    NewsConfig,
    NewsFetcher,
    NewsSummarizer
)
from gtts import gTTS
from deep_translator import GoogleTranslator
import io


def speak_text(text, lang):
    try:
        if lang != "en":
            translated = GoogleTranslator(source="auto", target=lang).translate(text)
        else:
            translated = text
    except:
        translated = text

    tts = gTTS(text=translated, lang=lang)

    audio_bytes = io.BytesIO()
    tts.write_to_fp(audio_bytes)
    audio_bytes.seek(0)

    st.audio(audio_bytes, format="audio/mp3")


st.set_page_config(
    page_title="Daily News Simplifier",
    page_icon="📰",
    layout="wide"
)

st.title("📰 Daily News Simplifier")
st.caption("Fast • Clean • Easy-to-read news summaries")


st.sidebar.header("Settings")

category = st.sidebar.selectbox(
    "Category",
    ["tech", "sports", "politics", "entertainment", "business", "health", "science"]
)

country = st.sidebar.selectbox(
    "Country",
    ["us", "in", "uk", "ca", "au"]
)

language_map = {
    "English": "en",
    "Hindi": "hi",
    "Telugu": "te",
    "Tamil": "ta",
    "Kannada": "kn"
}

selected_language = st.sidebar.selectbox(
    "Language",
    list(language_map.keys())
)

language = language_map[selected_language]

enable_voice = st.sidebar.checkbox("Enable voice")


config = NewsConfig()
fetcher = NewsFetcher(config)
summarizer = NewsSummarizer()


if "articles" not in st.session_state:
    st.session_state.articles = []


if st.sidebar.button("Fetch News"):
    with st.spinner("Fetching news..."):
        st.session_state.articles = fetcher.fetch_news(category, country)


articles = st.session_state.articles

if articles:
    st.success(f"Found {len(articles)} articles")

    for i, article in enumerate(articles, 1):
        with st.container():

            st.markdown(f"## {i}. {article.get('title', 'No Title')}")

            if article.get("url"):
                st.markdown(f"[Read full article]({article['url']})")

            summary = summarizer.summarize_article(article)

            for bullet in summary:
                st.markdown(bullet)

            if enable_voice:
                if st.button(f"Read Article {i}", key=f"read_{i}"):

                    full_text = article.get("title", "") + ". "
                    full_text += " ".join(summary)

                    speak_text(full_text, language)

            st.divider()

    if enable_voice:
        if st.button("Read All News"):

            full_text = ""
            for article in articles:
                summary = summarizer.summarize_article(article)
                full_text += article.get("title", "") + ". "
                full_text += " ".join(summary) + ". "

            speak_text(full_text, language)

else:
    st.info("Click 'Fetch News' to load articles.")

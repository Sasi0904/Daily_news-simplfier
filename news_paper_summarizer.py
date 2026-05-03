import os
import sys
import json
import time
import requests
from datetime import datetime
from typing import List, Dict
import argparse

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

try:
    from rich.console import Console
    from rich.panel import Panel
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class NewsConfig:
    def __init__(self):
        self.api_key = os.getenv("NEWSAPI_KEY", "")
        self.base_url = "https://newsapi.org/v2/top-headlines"

        self.categories = {
            "tech": "technology",
            "sports": "sports",
            "politics": "general",
            "entertainment": "entertainment",
            "business": "business",
            "health": "health",
            "science": "science"
        }

        self.countries = {
            "us": "United States",
            "in": "India",
            "uk": "United Kingdom",
            "ca": "Canada",
            "au": "Australia"
        }

        self.default_country = "us"
        self.default_category = "tech"
        self.max_articles = 10
        self.timeout = 15


class NewsFetcher:
    def __init__(self, config: NewsConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Daily News Simplifier/1.0'
        })

    def fetch_news(self, category: str = None, country: str = None) -> List[Dict]:
        if not self.config.api_key:
            return self._get_demo_news()

        category = category or self.config.default_category
        country = country or self.config.default_country

        params = {
            'category': self.config.categories.get(category, category),
            'country': country,
            'pageSize': self.config.max_articles,
            'apiKey': self.config.api_key
        }

        try:
            response = self.session.get(
                self.config.base_url,
                params=params,
                timeout=self.config.timeout
            )
            response.raise_for_status()
            data = response.json()

            if data.get('status') == 'ok':
                return data.get('articles', [])
            else:
                print(f"API Error: {data.get('message', 'Unknown error')}")
                return []

        except requests.RequestException as e:
            print(f"Network Error: {e}")
            return []
        except Exception as e:
            print(f"Unexpected Error: {e}")
            return []

    def _get_demo_news(self) -> List[Dict]:
        return [
            {
                "title": "Demo: AI Breakthrough in Healthcare",
                "description": "Researchers developed an AI system that can diagnose diseases with high accuracy.",
                "url": "https://example.com",
                "publishedAt": datetime.now().isoformat()
            }
        ]


class NewsSummarizer:
    @staticmethod
    def summarize_article(article: Dict) -> List[str]:
        text = article.get('description') or article.get('title') or ""

        if len(text) < 50:
            return [f"• {text}"]

        sentences = [s.strip() for s in text.split(".") if s.strip()]

        if len(sentences) <= 3:
            return [f"• {s}." for s in sentences]

        return [
            f"• {sentences[0]}.",
            f"• {sentences[len(sentences)//2]}.",
            f"• {sentences[-1]}."
        ]


class VoiceReader:
    def __init__(self):
        self.engine = None
        if TTS_AVAILABLE:
            try:
                self.engine = pyttsx3.init()
                self._configure_voice()
            except Exception:
                self.engine = None

    def _configure_voice(self):
        if not self.engine:
            return

        try:
            voices = self.engine.getProperty('voices')
            if voices:
                self.engine.setProperty('voice', voices[0].id)

            self.engine.setProperty('rate', 180)
            self.engine.setProperty('volume', 0.8)
        except Exception:
            pass

    def speak(self, text: str):
        if not self.engine:
            return

        try:
            clean_text = text.replace('•', '').strip()
            if clean_text:
                self.engine.say(clean_text)
                self.engine.runAndWait()
        except Exception:
            pass


class NewsDisplay:
    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None

    def display_header(self, category: str, country: str):
        title = f"Daily News - {category.title()}"
        subtitle = f"{country.upper()} | {datetime.now().strftime('%B %d, %Y')}"

        if self.console:
            self.console.print(Panel(f"{title}\n{subtitle}"))
        else:
            print(f"\n{title}")
            print(subtitle)

    def display_article(self, index: int, article: Dict, summary: List[str]):
        title = article.get('title', 'Untitled')

        if self.console:
            self.console.print(f"\n{index}. {title}")
        else:
            print(f"\n{index}. {title}")

        for bullet in summary:
            print(f"  {bullet}")

    def display_footer(self):
        print("\nDone.")


class DailyNewsApp:
    def __init__(self):
        self.config = NewsConfig()
        self.fetcher = NewsFetcher(self.config)
        self.summarizer = NewsSummarizer()
        self.voice_reader = VoiceReader()
        self.display = NewsDisplay()

    def run(self, category: str = None, country: str = None, voice: bool = False):
        category = category or self.config.default_category
        country = country or self.config.default_country

        self.display.display_header(category, country)

        print("Fetching news...")
        articles = self.fetcher.fetch_news(category, country)

        if not articles:
            print("No news found.")
            return

        for i, article in enumerate(articles, 1):
            summary = self.summarizer.summarize_article(article)
            self.display.display_article(i, article, summary)

            if voice and self.voice_reader.engine:
                self.voice_reader.speak(article.get('title', ''))

        self.display.display_footer()


def main():
    parser = argparse.ArgumentParser(description="Daily News Simplifier")

    parser.add_argument("-c", "--category",
                        choices=["tech", "sports", "politics", "entertainment", "business", "health", "science"],
                        default="tech")

    parser.add_argument("-country", "--country",
                        choices=["us", "in", "uk", "ca", "au"],
                        default="us")

    parser.add_argument("-v", "--voice", action="store_true")

    args = parser.parse_args()

    app = DailyNewsApp()
    app.run(category=args.category, country=args.country, voice=args.voice)


if __name__ == "__main__":
    main()

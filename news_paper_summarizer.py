import os
import sys
import json
import time
import requests
from datetime import datetime
from typing import List, Dict, Optional
import argparse

# Optional dependencies with graceful fallbacks
try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    print("ℹ️  pyttsx3 not installed. Voice reading will be disabled.")
    print("   Install with: pip install pyttsx3")

try:
    from rich.console import Console
    from rich.panel import Panel
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("ℹ️  rich not installed. Using basic console output.")
    print("   Install with: pip install rich")

# Configuration
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
        """Fetch news articles from NewsAPI"""
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
                print(f"❌ API Error: {data.get('message', 'Unknown error')}")
                return []
                
        except requests.RequestException as e:
            print(f"❌ Network Error: {e}")
            return []
        except Exception as e:
            print(f"❌ Unexpected Error: {e}")
            return []

    def _get_demo_news(self) -> List[Dict]:
        """Return demo news when API key is not available"""
        return [
            {
                "title": "🚀 Demo: AI Breakthrough in Healthcare",
                "description": "Researchers develop new AI system that can diagnose diseases with 95% accuracy, potentially revolutionizing medical diagnosis worldwide.",
                "url": "https://example.com/ai-healthcare",
                "publishedAt": datetime.now().isoformat()
            },
            {
                "title": "⚡ Demo: Renewable Energy Milestone Reached",
                "description": "Solar and wind power now account for over 50% of electricity generation in several countries, marking a historic shift toward clean energy.",
                "url": "https://example.com/renewable-energy",
                "publishedAt": datetime.now().isoformat()
            },
            {
                "title": "🌍 Demo: Climate Summit Reaches Historic Agreement",
                "description": "World leaders agree on ambitious new climate targets, including carbon neutrality by 2050 and massive investment in green technology.",
                "url": "https://example.com/climate-summit",
                "publishedAt": datetime.now().isoformat()
            }
        ]

class NewsSummarizer:
    @staticmethod
    def summarize_article(article: Dict) -> List[str]:
        """Create 3 bullet point summary from article content"""
        title = article.get('title', '')
        description = article.get('description', '')
        content = description or title
        
        if not content:
            return ["No content available for this article."]
        
        # Clean and prepare text
        text = content.strip()
        if len(text) < 50:
            return [f"📰 {text}"]
        
        # Simple but effective summarization
        sentences = NewsSummarizer._split_into_sentences(text)
        
        if len(sentences) <= 3:
            return [f"• {s.strip()}" for s in sentences if s.strip()]
        
        # Take most important sentences (first, middle, last)
        important_sentences = []
        if sentences:
            important_sentences.append(sentences[0])  # First sentence
        if len(sentences) > 2:
            important_sentences.append(sentences[len(sentences)//2])  # Middle
        if len(sentences) > 1:
            important_sentences.append(sentences[-1])  # Last sentence
        
        # Format as bullet points
        bullets = []
        for sentence in important_sentences[:3]:
            clean_sentence = sentence.strip()
            if clean_sentence and not clean_sentence.endswith('.'):
                clean_sentence += '.'
            bullets.append(f"• {clean_sentence}")
        
        return bullets if bullets else ["• Content could not be summarized."]

    @staticmethod
    def _split_into_sentences(text: str) -> List[str]:
        """Split text into sentences"""
        import re
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]

class VoiceReader:
    def __init__(self):
        self.engine = None
        if TTS_AVAILABLE:
            try:
                self.engine = pyttsx3.init()
                self._configure_voice()
            except Exception as e:
                print(f"⚠️  TTS initialization failed: {e}")
                self.engine = None

    def _configure_voice(self):
        """Configure TTS voice settings"""
        if not self.engine:
            return
        
        try:
            voices = self.engine.getProperty('voices')
            if voices:
                # Prefer female voice if available
                for voice in voices:
                    if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                        self.engine.setProperty('voice', voice.id)
                        break
            
            # Set speech rate and volume
            self.engine.setProperty('rate', 180)  # Speed
            self.engine.setProperty('volume', 0.8)  # Volume
        except Exception:
            pass  # Use defaults if configuration fails

    def speak(self, text: str):
        """Convert text to speech"""
        if not self.engine:
            return
        
        try:
            # Clean text for better speech
            clean_text = text.replace('•', '').replace('📰', '').strip()
            if clean_text:
                self.engine.say(clean_text)
                self.engine.runAndWait()
        except Exception as e:
            print(f"⚠️  TTS Error: {e}")

class NewsDisplay:
    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None

    def display_header(self, category: str, country: str):
        """Display app header"""
        title = f"📰 Daily News Simplifier - {category.title()} News"
        subtitle = f"Country: {country.upper()} | {datetime.now().strftime('%B %d, %Y')}"
        
        if self.console:
            self.console.print(Panel(
                f"{title}\n{subtitle}",
                style="bold blue",
                padding=(1, 2)
            ))
        else:
            print(f"\n{'='*60}")
            print(f"📰 {title}")
            print(f"   {subtitle}")
            print(f"{'='*60}")

    def display_article(self, index: int, article: Dict, summary: List[str], voice_reader: VoiceReader = None):
        """Display a single article with summary"""
        title = article.get('title', 'Untitled')
        url = article.get('url', '')
        
        if self.console:
            # Rich display
            self.console.print(f"\n[bold cyan]{index}.[/bold cyan] [bold]{title}[/bold]")
            if url:
                self.console.print(f"[dim]🔗 {url}[/dim]")
            
            for bullet in summary:
                self.console.print(f"  {bullet}")
        else:
            # Basic display
            print(f"\n{index}. {title}")
            if url:
                print(f"   🔗 {url}")
            for bullet in summary:
                print(f"   {bullet}")

    def display_footer(self):
        """Display app footer"""
        if self.console:
            self.console.print("\n[dim]Press Ctrl+C to stop voice reading[/dim]")
        else:
            print("\nPress Ctrl+C to stop voice reading")

class DailyNewsApp:
    def __init__(self):
        self.config = NewsConfig()
        self.fetcher = NewsFetcher(self.config)
        self.summarizer = NewsSummarizer()
        self.voice_reader = VoiceReader()
        self.display = NewsDisplay()

    def run(self, category: str = None, country: str = None, voice: bool = False):
        """Main application loop"""
        category = category or self.config.default_category
        country = country or self.config.default_country
        
        # Display header
        self.display.display_header(category, country)
        
        # Fetch news
        print("🔄 Fetching news...")
        articles = self.fetcher.fetch_news(category, country)
        
        if not articles:
            print("❌ No news articles found.")
            return
        
        print(f"✅ Found {len(articles)} articles\n")
        
        # Display articles
        for i, article in enumerate(articles, 1):
            summary = self.summarizer.summarize_article(article)
            self.display.display_article(i, article, summary)
            
            # Voice reading
            if voice and self.voice_reader.engine:
                try:
                    title = article.get('title', '')
                    self.voice_reader.speak(f"Article {i}: {title}")
                    for bullet in summary:
                        self.voice_reader.speak(bullet)
                    time.sleep(0.5)  # Brief pause between articles
                except KeyboardInterrupt:
                    print("\n⏹️  Voice reading stopped by user.")
                    break
        
        self.display.display_footer()

def main():
    parser = argparse.ArgumentParser(description="Daily News Simplifier")
    parser.add_argument("-c", "--category", 
                       choices=["tech", "sports", "politics", "entertainment", "business", "health", "science"],
                       default="tech", help="News category")
    parser.add_argument("-country", "--country",
                       choices=["us", "in", "uk", "ca", "au"],
                       default="us", help="Country for news")
    parser.add_argument("-v", "--voice", action="store_true",
                       help="Enable voice reading mode")
    parser.add_argument("--setup", action="store_true",
                       help="Show setup instructions")
    
    args = parser.parse_args()
    
    if args.setup:
        print_setup_instructions()
        return
    
    app = DailyNewsApp()
    app.run(category=args.category, country=args.country, voice=args.voice)

def print_setup_instructions():
    """Print setup instructions"""
    instructions = """
🚀 Daily News Simplifier - Setup Instructions

1. Get a free NewsAPI key:
   • Visit: https://newsapi.org/
   • Sign up for a free account
   • Copy your API key

2. Set your API key:
   Windows: set NEWSAPI_KEY=your_api_key_here
   Linux/Mac: export NEWSAPI_KEY=your_api_key_here

3. Install optional dependencies:
   pip install pyttsx3 rich

4. Run the app:
   python daily_news_simplifier.py --category tech --voice

Available categories: tech, sports, politics, entertainment, business, health, science
Available countries: us, in, uk, ca, au

Examples:
   python daily_news_simplifier.py -c sports -country us -v
   python daily_news_simplifier.py --category politics --country in
"""
    print(instructions)

if __name__ == "__main__":
    main()

# core/news_fetcher.py
import os
import requests
import logging
from datetime import datetime, timezone

# Load .env automatically
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logger = logging.getLogger(__name__)

API_KEY = os.getenv("NEWSDATA_API_KEY")

def fetch_recent_news(max_articles: int = 12) -> list:
    """Fetch recent news from NewsData.io with short, valid query."""
    if not API_KEY:
        logger.error("NEWSDATA_API_KEY not set! Add to .env or environment variables.")
        return []

    base_url = "https://newsdata.io/api/1/latest"

    # SHORT query: must be ≤100 characters
    query = "supply chain OR disruption OR tariff OR China OR Taiwan"

    params = {
        "apikey": API_KEY,
        "q": query,
        "language": "en",
        "size": min(max_articles, 10),  # Free plan max = 10 per call
    }

    try:
        response = requests.get(base_url, params=params, timeout=15)
        response.raise_for_status()

        data = response.json()

        if data.get("status") != "success":
            logger.error(f"NewsData.io error: {data.get('message', 'Unknown')}")
            logger.debug(f"Full API response: {data}")
            return []

        articles = data.get("results", [])[:max_articles]

        formatted = []
        for article in articles:
            formatted.append({
                "title": article.get("title", "No title"),
                "published": article.get("pubDate", datetime.now(timezone.utc).isoformat()),
                "source": article.get("source_id", "Unknown"),
                "url": article.get("link", ""),
                "summary": article.get("description", ""),
                "relevance_score": 0.85
            })

        logger.info(f"Collected {len(formatted)} real news items from NewsData.io")
        return formatted

    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP {e.response.status_code}: {e.response.text}")
        return []
    except Exception as e:
        logger.error(f"NewsData.io fetch failed: {str(e)}")
        return []
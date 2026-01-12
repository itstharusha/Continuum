"""
Ingestion Agent - Collects supplier master data and global risk-related news
"""

from typing import Dict, Any, List
import logging
import pandas as pd
import requests
from datetime import datetime, timezone   # ← add timezone here
from newspaper import Article, ArticleException

logger = logging.getLogger(__name__)

# For demo: we'll use a few public RSS feeds that are usually open
# In production → use NewsAPI.org with key or GNews, etc.
RSS_FEEDS = [
    "http://feeds.bbci.co.uk/news/world/rss.xml",                          # BBC World - very reliable
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",             # NYTimes World - active
    "https://www.supplychaindive.com/feed/",                               # Supply Chain Dive - industry specific
    "https://feeds.feedburner.com/logisticsmgmt/latest",                   # Logistics Management (via Feedburner)
    "https://www.joc.com/rss",                                             # Journal of Commerce - main feed
]
KEYWORDS = [
    "supply chain", "disruption", "shortage", "strike", "tariff", "sanction",
    "earthquake", "flood", "typhoon", "port", "factory", "outage", "cyberattack",
    "China", "Taiwan", "Red Sea", "Suez", "semiconductor", "steel", "trade war",
    "tariff", "freight", "logistics", "shipping delay", "winter weather", "Chinese New Year"
]

class IngestionAgent:
    """Handles data collection from multiple sources."""

    def __init__(self):
        import os
        PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.suppliers_path = os.path.join(PROJECT_ROOT, "data", "suppliers.csv")
        logger.info("IngestionAgent initialized")

    def load_suppliers(self) -> List[Dict[str, Any]]:
        """Load and validate supplier master data from CSV."""
        try:
            df = pd.read_csv(self.suppliers_path)
            # Basic cleaning & type conversion
            df = df.dropna(subset=["supplier_id", "name", "country", "material"])
            df["risk_country_score"] = pd.to_numeric(df["risk_country_score"], errors="coerce").fillna(0.3)
            suppliers = df.to_dict("records")
            logger.info(f"Loaded {len(suppliers)} suppliers from {self.suppliers_path}")
            return suppliers
        except FileNotFoundError:
            logger.error(f"Suppliers file not found: {self.suppliers_path}")
            return []
        except Exception as e:
            logger.error(f"Error loading suppliers: {e}")
            return []

    def fetch_recent_news(self, max_articles: int = 12) -> list:
        """Fetch real relevant news from RSS feeds."""
        from core.news_fetcher import fetch_recent_news

        try:
            articles = fetch_recent_news(max_articles=max_articles)  # ← Change 'max_total' to 'max_articles'
            logger.info(f"Collected {len(articles)} relevant real news items from RSS")
            return articles
        except Exception as e:
            logger.error(f"News fetching failed: {e}")
            return []
    def run(self, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Main execution method.
        Returns structured output ready for downstream agents.
        """
        config = config or {}
        max_news = config.get("max_news_articles", 8)

        suppliers = self.load_suppliers()
        news_items = self.fetch_recent_news(max_articles=max_news)

        result = {
            "suppliers": suppliers,
            "news_items": news_items,
            "ingestion_timestamp": datetime.utcnow().isoformat(),
            "sources_checked": len(RSS_FEEDS),
            "suppliers_count": len(suppliers),
            "news_count": len(news_items)
        }

        logger.info(f"Ingestion complete | {result['suppliers_count']} suppliers | {result['news_count']} news items")
        return result


# ─── Standalone Test ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    agent = IngestionAgent()
    output = agent.run()
    import json
    print(json.dumps(output, indent=2))
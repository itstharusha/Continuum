# core/llm_analyzer.py
from typing import List, Dict, Any
import logging
from transformers import pipeline

logger = logging.getLogger(__name__)

# Load small models once (lazy loading)
sentiment_pipeline = None
zero_shot_pipeline = None

def get_sentiment_pipeline():
    global sentiment_pipeline
    if sentiment_pipeline is None:
        logger.info("Loading sentiment analysis model...")
        sentiment_pipeline = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment-latest")
    return sentiment_pipeline

def get_zero_shot_pipeline():
    global zero_shot_pipeline
    if zero_shot_pipeline is None:
        logger.info("Loading zero-shot classification model...")
        zero_shot_pipeline = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
    return zero_shot_pipeline

def analyze_news_item(news: Dict[str, Any]) -> Dict[str, Any]:
    """
    Use LLM to:
    - Get sentiment score
    - Classify risk type
    - Extract potential affected entities (country/material)
    """
    title = news.get("title", "")
    summary = news.get("summary", "")
    text = title + " " + summary

    result = {
        "original_relevance_score": news.get("relevance_score", 0.85),
        "llm_sentiment": "NEUTRAL",
        "llm_risk_types": [],
        "llm_confidence": 0.5,
        "affected_entities": {"countries": [], "materials": []}
    }

    try:
        # Sentiment
        sent = get_sentiment_pipeline()(text[:512])[0]
        result["llm_sentiment"] = sent["label"]
        result["llm_confidence"] = sent["score"]

        # Zero-shot risk classification
        candidate_labels = ["high supply chain risk", "geopolitical risk", "natural disaster risk", "economic risk", "low risk"]
        zs = get_zero_shot_pipeline()(text[:512], candidate_labels, multi_label=True)
        top_risks = [label for label, score in zip(zs["labels"], zs["scores"]) if score > 0.4]
        result["llm_risk_types"] = top_risks[:2]

        # Simple entity extraction (keyword-based for now - can improve later)
        if "China" in text or "Chinese" in text:
            result["affected_entities"]["countries"].append("China")
        if "Taiwan" in text:
            result["affected_entities"]["countries"].append("Taiwan")
        if "semiconductor" in text.lower():
            result["affected_entities"]["materials"].append("Semiconductors")
        if "steel" in text.lower():
            result["affected_entities"]["materials"].append("Steel")

    except Exception as e:
        logger.warning(f"LLM analysis failed for news item: {e}")
        result["llm_confidence"] = 0.0

    return result
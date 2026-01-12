"""
Risk Agent - Detects supply chain risks by matching news to graph entities
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timezone
import re

import networkx as nx

from core.memory import memory

logger = logging.getLogger(__name__)

# Simple risk keyword mapping (expandable)
RISK_PATTERNS = {
    "geopolitical": ["tariff", "sanction", "trade war", "embargo", "ban", "restriction"],
    "disaster": ["earthquake", "flood", "typhoon", "hurricane", "drought", "storm", "weather"],
    "strike": ["strike", "protest", "labor dispute", "shutdown", "walkout"],
    "outage": ["power outage", "blackout", "fire", "explosion", "cyberattack", "hack"],
    "shortage": ["shortage", "supply constraint", "capacity reduction", "delay", "backlog"],
}

# Country → risk multiplier (higher = more sensitive)
COUNTRY_RISK_BASE = {
    "China": 0.75,
    "Taiwan": 0.85,
    "Brazil": 0.45,
    "Sweden": 0.15,
    "Germany": 0.20,
    # Add more as needed (from your suppliers)
}

# Material sensitivity to certain risk types
MATERIAL_SENSITIVITY = {
    "Semiconductors": ["outage", "geopolitical", "shortage", "cyberattack"],
    "Steel": ["tariff", "geopolitical", "strike", "shortage"],
    "Paper pulp": ["strike", "disaster"],
    "Nuts & oils": ["disaster", "shortage"],
    "Precision bearings": ["outage", "shortage"],
}

class RiskAgent:
    """Detects and scores risks based on news & graph context."""

    def __init__(self):
        logger.info("RiskAgent initialized")

    def extract_risk_types(self, text: str) -> List[str]:
        """Identify main risk categories from news text (title + summary)."""
        text_lower = text.lower()
        detected = set()
        for rtype, words in RISK_PATTERNS.items():
            if any(re.search(r'\b' + re.escape(word) + r'\b', text_lower) for word in words):
                detected.add(rtype)
        return list(detected) if detected else ["general"]

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Simple entity extraction for countries and materials."""
        text_lower = text.lower()
        entities = {"countries": [], "materials": []}

        # Countries (expand as needed)
        country_patterns = {
            "China": r'\bchina\b|\bchinese\b',
            "Taiwan": r'\btaiwan\b',
            "Brazil": r'\bbrazil\b|\bbrasil\b',
            "Sweden": r'\bsweden\b|\bswedish\b',
            "Germany": r'\bgermany\b|\bgerman\b',
        }
        for country, pattern in country_patterns.items():
            if re.search(pattern, text_lower):
                entities["countries"].append(country)

        # Materials (from your suppliers)
        material_patterns = {
            "Semiconductors": r'\bsemiconductor|chip|semicon',
            "Steel": r'\bsteel|iron',
            "Paper pulp": r'\bpulp|paper',
            "Nuts & oils": r'\bnuts|oils|oil',
            "Precision bearings": r'\bbearing|bearings',
        }
        for mat, pattern in material_patterns.items():
            if re.search(pattern, text_lower):
                entities["materials"].append(mat)

        return entities

    def score_risk(self, news_item: Dict, node_data: Dict) -> float:
        """Calculate risk score 0.0–1.0 for a specific node given a news item."""
        base = 0.0

        # 1. Country risk (baseline)
        country = node_data.get("country", "").strip()
        base += COUNTRY_RISK_BASE.get(country, 0.3)

        # 2. Material sensitivity
        material = node_data.get("material", "")
        full_text = (news_item.get("title", "") + " " + news_item.get("summary", "")).lower()
        risk_types = self.extract_risk_types(full_text)

        for rtype in risk_types:
            if material in MATERIAL_SENSITIVITY and rtype in MATERIAL_SENSITIVITY[material]:
                base += 0.25

        # 3. News relevance (from API or calculated)
        base += news_item.get("relevance_score", 0.5) * 0.3

        # 4. Entity match boost (stronger if direct match)
        entities = self.extract_entities(full_text)
        if country in entities["countries"]:
            base += 0.15
        if material in entities["materials"]:
            base += 0.20

        # Cap at 1.0 and round
        final_score = min(round(base, 2), 1.0)

        # Log for debugging
        if final_score > 0.7:
            logger.debug(f"High risk score {final_score} for {node_data.get('name')} "
                         f"from news: {news_item.get('title')[:60]}...")

        return final_score

    def find_affected_nodes(self, G: nx.DiGraph, news_item: Dict) -> List[Dict]:
        """Match news to graph nodes (focus on suppliers)."""
        title = str(news_item.get("title") or "").lower()
        summary = str(news_item.get("summary") or "").lower()
        full_text = title + " " + summary
        affected = []

        for node, data in G.nodes(data=True):
            if data.get("type") != "supplier":
                continue  # Focus on suppliers for now

            country = data.get("country", "").lower()
            material = data.get("material", "").lower()
            name = data.get("name", "").lower()

            # Match if any direct keyword appears in news text
            country_match = any(c.lower() in full_text for c in [country, country + 'ese'])  # e.g. "Chinese"
            material_match = any(m.lower() in full_text for m in [material, material.lower().replace(" ", ""),
                                                                  material.split()[
                                                                      0]])  # e.g. "semi conductor" → "semiconductor"
            name_match = name.lower() in full_text or any(word in full_text for word in name.lower().split())

            if country_match or material_match or name_match:
                score = self.score_risk(news_item, data)
                affected.append({
                    "node_id": node,
                    "name": data.get("name"),
                    "country": data.get("country"),
                    "material": data.get("material"),
                    "risk_score": score,
                    "risk_types": self.extract_risk_types(full_text),
                    "news_title": news_item.get("title"),
                    "news_summary": news_item.get("summary", ""),
                    "news_url": news_item.get("url", ""),
                })

        return affected

    def run(self, news_items: List[Dict[str, Any]], graph_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main execution method.
        Returns structured list of detected risks.
        """
        logger.info("RiskAgent running...")

        G: nx.DiGraph = memory.get("supply_chain_graph")
        if G is None or G.number_of_nodes() == 0:
            logger.error("No valid graph found in memory")
            return {"risks_detected": [], "max_severity": 0.0}

        all_risks = []
        max_severity = 0.0

        for news in news_items:
            affected_nodes = self.find_affected_nodes(G, news)
            for aff in affected_nodes:
                all_risks.append(aff)
                max_severity = max(max_severity, aff["risk_score"])

        # Sort by severity descending
        all_risks.sort(key=lambda x: x["risk_score"], reverse=True)

        result = {
            "risks_detected": all_risks,
            "max_severity": round(max_severity, 2),
            "total_risks_found": len(all_risks),
            "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
            "news_analyzed": len(news_items)
        }

        memory.set("risk_result", result)

        logger.info(f"Risk analysis complete | {result['total_risks_found']} risks | "
                    f"max severity {result['max_severity']}")
        return result


# ─── Standalone Test ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Simulate previous agents
    from agents.ingestion_agent import IngestionAgent
    from agents.graph_agent import GraphAgent

    ing = IngestionAgent()
    ingest_result = ing.run()

    graph_agent = GraphAgent()
    graph_agent.run(ingest_result["suppliers"])

    # Now run risk agent
    risk_agent = RiskAgent()
    risk_result = risk_agent.run(
        news_items=ingest_result["news_items"],
        graph_info=memory.get("graph_result")
    )

    import json
    print(json.dumps(risk_result, indent=2))
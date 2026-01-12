"""
Decision Agent - Makes autonomous recommendations based on risks & simulations
"""

from typing import Dict, Any, List, Tuple
import logging
from datetime import datetime, timezone

from core.memory import memory

logger = logging.getLogger(__name__)

# Decision thresholds (tuned for real-world supply chain impact)
CRITICAL_RISK_THRESHOLD = 0.85
HIGH_RISK_THRESHOLD = 0.65
MEDIUM_RISK_THRESHOLD = 0.40

# Delay & impact thresholds
CRITICAL_DELAY_DAYS = 14        # >2 weeks is critical
HIGH_DELAY_DAYS = 7             # 1-2 weeks is high
CRITICAL_SERVICE_IMPACT = 60    # >60% service loss is critical
HIGH_SERVICE_IMPACT = 40        # 40-60% is high
MEDIUM_SERVICE_IMPACT = 20      # 20-40% is medium

# Material criticality scores (1-5, higher = more critical to supply chain)
MATERIAL_CRITICALITY = {
    "Semiconductors": 5,        # Mission-critical, long lead times
    "Steel": 4,                 # High volume, structural
    "Paper pulp": 2,            # Moderate impact
    "Nuts & oils": 3,           # Perishable, supply-dependent
    "Precision bearings": 4,    # Long lead times, low redundancy
}

# Country geopolitical risk factors (1-5, higher = more at risk)
COUNTRY_GEOPOLITICAL_RISK = {
    "China": 4,                 # Trade tensions, geopolitical
    "Taiwan": 5,                # High tension zones, strategic
    "Brazil": 2,                # Moderate political risk
    "Sweden": 1,                # Stable
    "Germany": 1,               # Stable
    "South Korea": 3,           # Regional tensions
    "Japan": 2,                 # Natural disaster risk
    "Vietnam": 2,               # Emerging but stable
    "India": 2,                 # Moderate economic volatility
}

# Action templates with urgency (1-5, higher = more urgent)
ACTION_LIBRARY = {
    "do_nothing": {
        "description": "No immediate action required - monitor only",
        "urgency": 1,
        "confidence_threshold": 0.0,
        "lead_time_days": 0
    },
    "increase_monitoring": {
        "description": "Increase monitoring frequency and alert thresholds for this supplier",
        "urgency": 2,
        "confidence_threshold": 0.35,
        "lead_time_days": 1
    },
    "notify_procurement": {
        "description": "Notify procurement team to review alternatives and contracts",
        "urgency": 3,
        "confidence_threshold": 0.50,
        "lead_time_days": 2
    },
    "activate_alternative_source": {
        "description": "Activate pre-qualified alternative supplier(s)",
        "urgency": 4,
        "confidence_threshold": 0.65,
        "lead_time_days": 3
    },
    "increase_safety_stock": {
        "description": "Immediately increase safety stock levels for affected materials",
        "urgency": 4,
        "confidence_threshold": 0.60,
        "lead_time_days": 1
    },
    "expedite_shipment": {
        "description": "Expedite current shipments and negotiate priority delivery",
        "urgency": 5,
        "confidence_threshold": 0.70,
        "lead_time_days": 0
    },
    "diversify_suppliers": {
        "description": "Initiate long-term supplier diversification project for this material/country",
        "urgency": 2,
        "confidence_threshold": 0.40,
        "lead_time_days": 180
    }
}


class DecisionAgent:
    """Makes autonomous decisions and recommendations based on real-world supply chain factors."""

    def __init__(self):
        logger.info("DecisionAgent initialized")

    def calculate_confidence(self, risk: Dict, sim: Dict) -> float:
        """
        Calculate decision confidence based on multiple factors.
        Real-world confidence incorporates: severity, delay, impact, material criticality, country risk.
        Capped at 1.0 (100%).
        """
        severity = risk["risk_score"]
        delay_days = sim["estimated_delay_days"]
        service_impact = sim["service_level_impact_pct"]
        material = risk.get("material", "Unknown")
        country = risk.get("country", "Unknown")
        
        # Base confidence from risk severity
        base_confidence = min(severity, 1.0)
        
        # Delay impact factor (0 to 0.2)
        delay_factor = min(delay_days / CRITICAL_DELAY_DAYS, 1.0) * 0.2
        
        # Service impact factor (0 to 0.2)
        service_factor = min(service_impact / CRITICAL_SERVICE_IMPACT, 1.0) * 0.2
        
        # Material criticality factor (0 to 0.2)
        material_criticality = MATERIAL_CRITICALITY.get(material, 2)
        criticality_factor = (material_criticality / 5.0) * 0.2
        
        # Country geopolitical risk factor (0 to 0.2)
        country_risk = COUNTRY_GEOPOLITICAL_RISK.get(country, 2)
        country_factor = (country_risk / 5.0) * 0.2
        
        # Total confidence (base + factors, capped at 1.0)
        total_confidence = min(base_confidence + delay_factor + service_factor + criticality_factor + country_factor, 1.0)
        
        return round(total_confidence, 2)

    def decide_for_scenario(self, risk: Dict, sim: Dict) -> Dict:
        """
        Determine best action(s) for one risk + simulation pair.
        Uses multi-factor decision logic based on real-world supply chain practices.
        """
        severity = risk["risk_score"]
        delay_days = sim["estimated_delay_days"]
        service_impact = sim["service_level_impact_pct"]
        affected_count = sim["affected_nodes_count"]
        material = risk.get("material", "Unknown")
        country = risk.get("country", "Unknown")
        disruption_type = sim.get("disruption_type", "Unknown")
        
        confidence = self.calculate_confidence(risk, sim)
        actions = []
        
        # ──── CRITICAL RISK: Severe impact, immediate action ────
        if severity >= CRITICAL_RISK_THRESHOLD or \
           delay_days >= CRITICAL_DELAY_DAYS or \
           service_impact >= CRITICAL_SERVICE_IMPACT:
            
            # Expedite if node failure (structural disruption)
            if disruption_type == "node_failure":
                actions.append("expedite_shipment")
                actions.append("activate_alternative_source")
            else:
                # Capacity reduction → increase stock and activate alternatives
                actions.append("increase_safety_stock")
                actions.append("activate_alternative_source")
            
            # If material is critical, diversify for long-term
            material_criticality = MATERIAL_CRITICALITY.get(material, 2)
            if material_criticality >= 4 and country in ["China", "Taiwan"]:
                actions.append("diversify_suppliers")
        
        # ──── HIGH RISK: Significant risk, proactive measures ────
        elif severity >= HIGH_RISK_THRESHOLD or \
             delay_days >= HIGH_DELAY_DAYS or \
             service_impact >= HIGH_SERVICE_IMPACT:
            
            # If near-term delay, increase stock
            if delay_days > 0 and delay_days < HIGH_DELAY_DAYS:
                actions.append("increase_safety_stock")
            
            # If affected nodes are many (>3), activate alternative
            if affected_count >= 3:
                actions.append("activate_alternative_source")
            else:
                actions.append("notify_procurement")
            
            # Monitor if geopolitical risk
            country_risk = COUNTRY_GEOPOLITICAL_RISK.get(country, 2)
            if country_risk >= 3:
                actions.append("diversify_suppliers")
        
        # ──── MEDIUM RISK: Monitor and contingency plan ────
        elif severity >= MEDIUM_RISK_THRESHOLD or service_impact >= MEDIUM_SERVICE_IMPACT:
            actions.append("notify_procurement")
            actions.append("increase_monitoring")
        
        # ──── LOW RISK: Monitor only ────
        else:
            actions.append("increase_monitoring")
        
        # ──── DOWNGRADE for minimal delay/impact ────
        if delay_days < 3 and service_impact < 20 and severity < MEDIUM_RISK_THRESHOLD:
            actions = ["do_nothing"]
        
        # ──── UPGRADE if material is critical ────
        material_criticality = MATERIAL_CRITICALITY.get(material, 2)
        if material_criticality >= 4 and "increase_monitoring" in actions:
            actions.remove("increase_monitoring")
            actions.append("notify_procurement")
        
        # Remove duplicates & maintain urgency order
        unique_actions = []
        seen = set()
        for act in actions:
            if act not in seen:
                unique_actions.append(act)
                seen.add(act)
        
        # Sort by urgency descending
        sorted_actions = sorted(
            [(act, ACTION_LIBRARY[act]) for act in unique_actions],
            key=lambda x: x[1]["urgency"],
            reverse=True
        )
        
        # Build recommendations with confidence thresholds
        recommendations = [
            {
                "action": act,
                "description": info["description"],
                "urgency": info["urgency"],
                "estimated_confidence": round(min(confidence, 1.0), 2),  # Cap at 100%
                "lead_time_days": info["lead_time_days"]
            }
            for act, info in sorted_actions
        ]
        
        # Log decision rationale
        if severity >= HIGH_RISK_THRESHOLD:
            logger.info(
                f"High-risk decision for {risk['node_id']}: "
                f"severity={severity:.2f}, delay={delay_days}d, impact={service_impact:.1f}%, "
                f"actions={[r['action'] for r in recommendations[:2]]}"
            )
        
        return {
            "node_id": risk["node_id"],
            "name": risk.get("name", risk["node_id"]),
            "material": material,
            "country": country,
            "risk_score": severity,
            "delay_days": delay_days,
            "service_impact_pct": service_impact,
            "affected_nodes_count": affected_count,
            "recommended_actions": recommendations,
            "primary_action": recommendations[0]["action"] if recommendations else "do_nothing",
            "confidence": confidence
        }

    def run(self,
            risks: Dict[str, Any],
            simulation_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main execution method.
        Produces prioritized list of recommended actions with real-world decision logic.
        """
        logger.info("DecisionAgent running...")

        # Handle null/empty inputs
        if risks is None:
            risks = {}
        if simulation_results is None:
            simulation_results = {}

        risk_list = risks.get("risks_detected", [])
        scenarios = simulation_results.get("scenarios", [])

        if not risk_list or not scenarios:
            logger.warning("Missing input data for decision making")
            return {
                "recommended_actions": [],
                "overall_confidence": 0.0,
                "decision_count": 0,
                "decision_timestamp": datetime.now(timezone.utc).isoformat(),
                "top_recommendation": "do_nothing"
            }

        # Match risks to their simulations (by node_id)
        decisions = []
        for sim in scenarios:
            node_id = sim["node_id"]
            # Find corresponding risk
            risk = next((r for r in risk_list if r["node_id"] == node_id), None)
            if risk:
                decision = self.decide_for_scenario(risk, sim)
                decisions.append(decision)

        # Sort by confidence descending (most confident decisions first)
        decisions.sort(
            key=lambda d: d["confidence"],
            reverse=True
        )

        # Calculate overall confidence (average of top decision confidences, capped at 1.0)
        if decisions:
            top_confidences = [d["confidence"] for d in decisions[:3]]
            overall_confidence = round(min(sum(top_confidences) / len(top_confidences), 1.0), 2)
        else:
            overall_confidence = 0.0

        result = {
            "recommended_actions": decisions,
            "overall_confidence": overall_confidence,
            "decision_count": len(decisions),
            "decision_timestamp": datetime.now(timezone.utc).isoformat(),
            "top_recommendation": decisions[0]["primary_action"] if decisions else "do_nothing"
        }

        memory.set("decision_result", result)

        logger.info(
            f"Decision process complete | {result['decision_count']} recommendations | "
            f"overall confidence {overall_confidence:.0%} | "
            f"top action: {result['top_recommendation']}"
        )
        return result


# ─── Standalone Test ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Run full chain
    from agents.ingestion_agent import IngestionAgent
    from agents.graph_agent import GraphAgent
    from agents.risk_agent import RiskAgent
    from agents.simulation_agent import SimulationAgent

    ing = IngestionAgent()
    ingest = ing.run()

    graph = GraphAgent()
    graph.run(ingest["suppliers"])

    risk = RiskAgent()
    risk.run(ingest["news_items"], memory.get("graph_result"))

    sim = SimulationAgent()
    sim.run(memory.get("graph_result"), memory.get("risk_result"))

    # Now decide
    decision = DecisionAgent()
    result = decision.run(
        risks=memory.get("risk_result"),
        simulation_results=memory.get("simulation_result")
    )

    import json
    print(json.dumps(result, indent=2))
"""
Simulation Agent - Performs what-if failure simulations on the supply chain graph
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timezone

import networkx as nx

from core.memory import memory

logger = logging.getLogger(__name__)

# Simulation parameters (tunable)
DEFAULT_DELAY_DAYS_PER_LEVEL = 3      # days added per hop downstream
CAPACITY_REDUCTION_SEVERE = 0.8       # 80% capacity loss for severe risks
CAPACITY_REDUCTION_MODERATE = 0.4     # 40% for moderate


class SimulationAgent:
    """Performs failure simulations on the supply chain graph."""

    def __init__(self):
        self.G: Optional[nx.DiGraph] = None
        logger.info("SimulationAgent initialized")

    def load_graph(self):
        """Load the current supply chain graph from memory."""
        self.G = memory.get("supply_chain_graph")
        if self.G is None or self.G.number_of_nodes() == 0:
            raise ValueError("No valid graph found in memory for simulation")

    def simulate_single_risk(self, risk: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate impact of one specific risk event."""
        if self.G is None:
            self.load_graph()

        node_id = risk["node_id"]
        severity = risk["risk_score"]

        # Determine disruption strength
        if severity >= 0.8:
            capacity_loss = CAPACITY_REDUCTION_SEVERE
            delay_multiplier = 1.5
        elif severity >= 0.5:
            capacity_loss = CAPACITY_REDUCTION_MODERATE
            delay_multiplier = 1.0
        else:
            capacity_loss = 0.2
            delay_multiplier = 0.7

        # Create a temporary copy for simulation
        sim_G = self.G.copy()

        # Apply disruption: reduce capacity or remove node if severe
        if severity >= 0.9 and node_id in sim_G:
            sim_G.remove_node(node_id)
            disruption_type = "node_failure"
        else:
            # Reduce capacity on affected node
            if "capacity" in sim_G.nodes[node_id]:
                orig_cap = sim_G.nodes[node_id]["capacity"]
                sim_G.nodes[node_id]["capacity"] = max(0, orig_cap * (1 - capacity_loss))
            disruption_type = "capacity_reduction"

        # Find all downstream affected nodes (including the disrupted one)
        try:
            affected = list(nx.descendants(sim_G, node_id)) + [node_id]
        except nx.NetworkXError:
            # Node already removed or not present
            affected = [node_id]

        # Estimate delay propagation
        max_delay = 0
        for target in affected:
            try:
                path_len = nx.shortest_path_length(self.G, node_id, target)
                delay = path_len * DEFAULT_DELAY_DAYS_PER_LEVEL * delay_multiplier
                max_delay = max(max_delay, delay)
            except nx.NetworkXNoPath:
                continue

        # Rough service level impact (percentage of downstream nodes still reachable)
        original_reachable = len(list(nx.descendants(self.G, node_id))) + 1
        sim_reachable = len(affected) if disruption_type == "capacity_reduction" else 1
        service_impact_pct = round((1 - sim_reachable / original_reachable) * 100, 1) if original_reachable > 0 else 100.0

        return {
            "node_id": node_id,
            "disruption_type": disruption_type,
            "severity_used": severity,
            "capacity_loss_pct": round(capacity_loss * 100),
            "estimated_delay_days": round(max_delay, 1),
            "affected_nodes_count": len(affected),
            "service_level_impact_pct": service_impact_pct,
            "news_title": risk.get("news_title", "Unknown"),
            "simulated_at": datetime.now(timezone.utc).isoformat()
        }

    def run(self,
            graph_info: Dict[str, Any],
            risks: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main execution method.
        Runs simulations for top risks → aggregates results.
        """
        logger.info("SimulationAgent running...")

        risk_list = risks.get("risks_detected", [])
        if not risk_list:
            logger.warning("No risks to simulate")
            return {"scenarios": [], "worst_case_delay_days": 0}

        self.load_graph()

        scenarios = []
        worst_delay = 0
        total_affected = set()

        # Simulate only top 5 most severe risks (to keep it fast)
        for risk in sorted(risk_list, key=lambda x: x["risk_score"], reverse=True)[:5]:
            scenario = self.simulate_single_risk(risk)
            scenarios.append(scenario)

            worst_delay = max(worst_delay, scenario["estimated_delay_days"])
            total_affected.update([scenario["node_id"]])

        result = {
            "scenarios": scenarios,
            "worst_case_delay_days": round(worst_delay, 1),
            "worst_case_affected_nodes": len(total_affected),
            "number_of_simulations": len(scenarios),
            "simulation_timestamp": datetime.now(timezone.utc).isoformat()
        }

        memory.set("simulation_result", result)

        logger.info(f"Simulation complete | {len(scenarios)} scenarios | "
                    f"worst delay {result['worst_case_delay_days']} days")
        return result


# ─── Standalone Test ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Run previous agents to populate memory
    from agents.ingestion_agent import IngestionAgent
    from agents.graph_agent import GraphAgent
    from agents.risk_agent import RiskAgent

    ing = IngestionAgent()
    ingest = ing.run()

    graph = GraphAgent()
    graph.run(ingest["suppliers"])

    risk = RiskAgent()
    risk.run(ingest["news_items"], memory.get("graph_result"))

    # Now simulate
    sim = SimulationAgent()
    result = sim.run(
        graph_info=memory.get("graph_result"),
        risks=memory.get("risk_result")
    )

    import json
    print(json.dumps(result, indent=2))
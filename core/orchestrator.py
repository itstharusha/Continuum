"""
Orchestrator - Coordinates the full multi-agent workflow in correct order
"""

import logging
import time
from typing import Dict, Any, Optional

from agents.ingestion_agent import IngestionAgent
from agents.graph_agent import GraphAgent
from agents.risk_agent import RiskAgent
from agents.simulation_agent import SimulationAgent
from agents.decision_agent import DecisionAgent
from core.memory import memory
from core.persistence import persistence

logger = logging.getLogger(__name__)


class Orchestrator:
    """Main coordinator of the Supply Chain Risk Sentinel system."""

    def __init__(self):
        self.ingestion = IngestionAgent()
        self.graph = GraphAgent()
        self.risk = RiskAgent()
        self.simulation = SimulationAgent()
        self.decision = DecisionAgent()
        logger.info("Orchestrator initialized – all agents ready")

    def run_single_cycle(self, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute one complete analysis cycle.
        Returns summary of results + status.
        """
        config = config or {}
        cycle_start = time.time()

        try:
            logger.info("=" * 80)
            logger.info("STARTING NEW ANALYSIS CYCLE")
            logger.info("=" * 80)

            # 1. Ingestion
            logger.info("→ Step 1: Ingestion")
            ingest_result = self.ingestion.run(config)
            memory.set("ingestion_result", ingest_result)

            # 2. Graph Building
            logger.info("→ Step 2: Graph Construction")
            graph_result = self.graph.run(ingest_result.get("suppliers", []))
            memory.set("graph_result", graph_result)

            # 3. Risk Detection
            logger.info("→ Step 3: Risk Detection")
            risk_result = self.risk.run(
                ingest_result.get("news_items", []),
                graph_result
            )
            memory.set("risk_result", risk_result)

            # 4. Simulation
            logger.info("→ Step 4: Impact Simulation")
            sim_result = self.simulation.run(graph_result, risk_result)
            memory.set("simulation_result", sim_result)

            # 5. Decision Making
            logger.info("→ Step 5: Decision & Recommendations")
            decision_result = self.decision.run(risk_result, sim_result)
            memory.set("decision_result", decision_result)

            duration = round(time.time() - cycle_start, 2)
            logger.info("=" * 80)
            logger.info(f"CYCLE COMPLETED SUCCESSFULLY in {duration}s")
            logger.info(f"Overall confidence: {decision_result.get('overall_confidence', 'N/A')}")
            logger.info(f"Top recommendation: {decision_result.get('top_recommendation', 'None')}")
            logger.info("=" * 80)

            # Save cycle to history
            save_result = persistence.save_cycle(memory.dump())
            if save_result["status"] == "success":
                logger.info(f"Cycle persisted: {save_result['filename']}")
            else:
                logger.warning(f"Failed to persist cycle: {save_result.get('error')}")

            return {
                "status": "success",
                "cycle_duration_seconds": duration,
                "persisted": save_result["status"] == "success",
                "persistence_filename": save_result.get("filename"),
                "summary": {
                    "suppliers": ingest_result.get("suppliers_count", 0),
                    "news_items": ingest_result.get("news_count", 0),
                    "risks_detected": risk_result.get("total_risks_found", 0),
                    "max_risk_severity": risk_result.get("max_severity", 0.0),
                    "worst_delay_days": sim_result.get("worst_case_delay_days", 0),
                    "decisions_count": decision_result.get("decision_count", 0),
                    "top_action": decision_result.get("top_recommendation", "do_nothing")
                }
            }

        except Exception as e:
            logger.error("CRITICAL ERROR DURING CYCLE", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "partial_results": memory.dump()  # dump what's available for debugging
            }


# For manual testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    orch = Orchestrator()
    result = orch.run_single_cycle()
    print("\nCycle Summary:")
    print(result)
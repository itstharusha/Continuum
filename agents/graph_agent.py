"""
Graph Agent - Builds and maintains the supply chain dependency graph using NetworkX
"""

from typing import Dict, Any, List
import logging
import networkx as nx
from datetime import datetime, timezone

from core.memory import memory

logger = logging.getLogger(__name__)


class GraphAgent:
    """Builds and maintains the supply chain dependency graph."""

    def __init__(self):
        self.G: nx.DiGraph = nx.DiGraph()  # Directed graph: flow of materials/supply
        logger.info("GraphAgent initialized")

    def build_graph_from_suppliers(self, suppliers: List[Dict[str, Any]]) -> None:
        """Create nodes and edges from supplier data."""
        if not suppliers:
            logger.warning("No suppliers provided → empty graph")
            return

        # Add supplier nodes
        for sup in suppliers:
            node_id = sup["supplier_id"]
            self.G.add_node(
                node_id,
                type="supplier",
                name=sup["name"],
                country=sup["country"],
                material=sup["material"],
                capacity=sup["capacity_tons_per_month"],
                risk_score=sup["risk_country_score"],
                color="#4CAF50"  # green for suppliers
            )

        # Add fictional downstream nodes (for realistic chain)
        downstream = [
            {"id": "F001", "type": "factory", "name": "Main Assembly Factory", "color": "#2196F3"},
            {"id": "W001", "type": "warehouse", "name": "Central Distribution Warehouse", "color": "#FF9800"},
            {"id": "C001", "type": "customer", "name": "Global Retail Customer", "color": "#9C27B0"},
        ]

        for ds in downstream:
            self.G.add_node(ds["id"], type=ds["type"], name=ds["name"], color=ds["color"])

        # Create realistic dependencies (directed edges: supplier → consumer)
        # For simplicity: most suppliers → factory, factory → warehouse, warehouse → customer
        for sup in suppliers:
            sup_id = sup["supplier_id"]

            # 80% go directly to factory
            if sup["material"] in ["Steel", "Semiconductors", "Precision bearings"]:
                self.G.add_edge(sup_id, "F001", material=sup["material"], weight=1.0)

            # Some go to warehouse directly (e.g. packaging/nuts)
            if sup["material"] in ["Paper pulp", "Nuts & oils"]:
                self.G.add_edge(sup_id, "W001", material=sup["material"], weight=0.8)

        # Factory → Warehouse → Customer (core chain)
        self.G.add_edge("F001", "W001", material="Assembled Products", weight=1.0)
        self.G.add_edge("W001", "C001", material="Finished Goods", weight=1.0)

        logger.info(f"Graph built: {self.G.number_of_nodes()} nodes, {self.G.number_of_edges()} edges")

    def get_graph_stats(self) -> Dict[str, Any]:
        """Compute basic graph metrics."""
        if self.G.number_of_nodes() == 0:
            return {"valid": False}

        return {
            "valid": True,
            "node_count": self.G.number_of_nodes(),
            "edge_count": self.G.number_of_edges(),
            "supplier_count": len([n for n, d in self.G.nodes(data=True) if d["type"] == "supplier"]),
            "has_cycles": nx.is_directed_acyclic_graph(self.G) is False,
            "critical_nodes": self._find_critical_nodes(),
            "avg_degree": sum(d for n, d in self.G.degree()) / self.G.number_of_nodes() if self.G.number_of_nodes() else 0
        }

    def _find_critical_nodes(self) -> List[str]:
        """Simple heuristic: nodes with high out-degree or on longest path."""
        try:
            longest_path = nx.dag_longest_path(self.G)
            return longest_path[:3]  # first few are usually most critical upstream
        except:
            # Fallback: high degree nodes
            return [n for n, d in sorted(self.G.out_degree(), key=lambda x: x[1], reverse=True)[:3]]

    def run(self, suppliers_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Main execution method.
        Builds graph → computes stats → stores in memory
        """
        logger.info("GraphAgent running...")

        self.build_graph_from_suppliers(suppliers_data)

        stats = self.get_graph_stats()

        result = {
            "graph_built": stats["valid"],
            "node_count": stats["node_count"],
            "edge_count": stats["edge_count"],
            "supplier_count": stats["supplier_count"],
            "critical_nodes": stats["critical_nodes"],
            "graph_stats": stats,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        # Store the actual graph object in shared memory for downstream agents
        memory.set("supply_chain_graph", self.G)
        memory.set("graph_result", result)

        logger.info(f"Graph construction complete | {result['node_count']} nodes | {result['edge_count']} edges")
        return result


# ─── Standalone Test ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Get suppliers from memory (simulate ingestion)
    from agents.ingestion_agent import IngestionAgent
    ing = IngestionAgent()
    ingestion_result = ing.run()
    suppliers = ingestion_result["suppliers"]

    agent = GraphAgent()
    output = agent.run(suppliers)

    import json
    print(json.dumps(output, indent=2))

    # Optional: print basic graph summary
    print("\nNodes:")
    for node, data in agent.G.nodes(data=True):
        print(f"  {node}: {data.get('name', 'N/A')} ({data.get('type', '?')})")
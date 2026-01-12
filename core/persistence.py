# core/persistence.py
"""
Data Persistence Module - Saves and loads analysis cycle results
Maintains timestamped history of all analyses in JSON format
"""

import json
import os
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# Default history directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HISTORY_DIR = os.path.join(PROJECT_ROOT, "data", "history")


class DataPersistence:
    """Handles saving and loading analysis cycle results."""

    def __init__(self, history_dir: str = HISTORY_DIR):
        """Initialize persistence layer with history directory."""
        self.history_dir = history_dir
        self._ensure_history_dir()
        logger.info(f"DataPersistence initialized | History dir: {self.history_dir}")

    def _ensure_history_dir(self):
        """Create history directory if it doesn't exist."""
        try:
            Path(self.history_dir).mkdir(parents=True, exist_ok=True)
            logger.debug(f"History directory ready: {self.history_dir}")
        except Exception as e:
            logger.error(f"Failed to create history directory: {e}")
            raise

    def _get_timestamp_filename(self) -> str:
        """Generate timestamped filename: YYYYMMDD_HHMMSS.json"""
        now = datetime.now(timezone.utc)
        return now.strftime("%Y%m%d_%H%M%S")

    def save_cycle(self, memory_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save complete analysis cycle to timestamped JSON file.
        
        Args:
            memory_state: Full memory dump from orchestrator
            
        Returns:
            Dict with save status, filename, and metadata
        """
        timestamp = self._get_timestamp_filename()
        filepath = os.path.join(self.history_dir, f"{timestamp}.json")
        
        try:
            # Extract key cycle data
            cycle_data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "ingestion_result": memory_state.get("ingestion_result", {}),
                "graph_result": self._serialize_graph(memory_state.get("graph_result")),
                "risk_result": memory_state.get("risk_result", {}),
                "simulation_result": memory_state.get("simulation_result", {}),
                "decision_result": memory_state.get("decision_result", {}),
            }
            
            # Save to file
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(cycle_data, f, indent=2, default=str)
            
            logger.info(f"Cycle saved to {filepath}")
            
            return {
                "status": "success",
                "filename": timestamp,
                "filepath": filepath,
                "timestamp": cycle_data["timestamp"],
                "summary": {
                    "suppliers": len(cycle_data["ingestion_result"].get("suppliers", [])),
                    "news_items": len(cycle_data["ingestion_result"].get("news_items", [])),
                    "risks_detected": len(cycle_data["risk_result"].get("risks_detected", [])),
                    "scenarios": len(cycle_data["simulation_result"].get("scenarios", [])),
                    "decisions": len(cycle_data["decision_result"].get("recommended_actions", [])),
                }
            }
        
        except Exception as e:
            logger.error(f"Failed to save cycle: {e}")
            return {
                "status": "error",
                "error": str(e),
                "filename": timestamp
            }

    def _serialize_graph(self, graph_result: Optional[Dict]) -> Dict:
        """
        Serialize graph result for JSON storage.
        Converts NetworkX graph to nodes/edges format.
        """
        if not graph_result:
            return {}
        
        try:
            import networkx as nx
            
            graph = graph_result.get("graph")
            if not isinstance(graph, nx.DiGraph):
                return graph_result
            
            # Convert to node-link format (JSON-serializable)
            nodes = []
            edges = []
            
            for node, data in graph.nodes(data=True):
                node_entry = {"id": node}
                node_entry.update(data)
                nodes.append(node_entry)
            
            for source, target, data in graph.edges(data=True):
                edge_entry = {"source": source, "target": target}
                edge_entry.update(data)
                edges.append(edge_entry)
            
            return {
                "graph": {
                    "nodes": nodes,
                    "edges": edges,
                    "node_count": len(nodes),
                    "edge_count": len(edges)
                },
                **{k: v for k, v in graph_result.items() if k != "graph"}
            }
        
        except Exception as e:
            logger.warning(f"Failed to serialize graph: {e}")
            return graph_result or {}

    def list_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        List all saved analysis cycles, newest first.
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of history entries with metadata
        """
        try:
            entries = []
            
            # Get all JSON files in history directory
            json_files = sorted(
                [f for f in os.listdir(self.history_dir) if f.endswith(".json")],
                reverse=True  # Newest first
            )[:limit]
            
            for filename in json_files:
                filepath = os.path.join(self.history_dir, filename)
                
                # Get file size and modified time
                stat = os.stat(filepath)
                
                entries.append({
                    "filename": filename.replace(".json", ""),
                    "filepath": filepath,
                    "timestamp": self._parse_timestamp(filename),
                    "file_size_bytes": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                })
            
            logger.debug(f"Listed {len(entries)} history entries")
            return entries
        
        except Exception as e:
            logger.error(f"Failed to list history: {e}")
            return []

    def load_cycle(self, filename: str) -> Dict[str, Any]:
        """
        Load a saved analysis cycle by filename.
        
        Args:
            filename: Timestamp filename (without .json)
            
        Returns:
            Loaded cycle data or error dict
        """
        filepath = os.path.join(self.history_dir, f"{filename}.json")
        
        try:
            if not os.path.exists(filepath):
                return {
                    "status": "error",
                    "error": f"File not found: {filepath}",
                    "filename": filename
                }
            
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            logger.info(f"Loaded cycle from {filepath}")
            
            return {
                "status": "success",
                "filename": filename,
                "data": data,
                "summary": {
                    "suppliers": len(data.get("ingestion_result", {}).get("suppliers", [])),
                    "news_items": len(data.get("ingestion_result", {}).get("news_items", [])),
                    "risks_detected": len(data.get("risk_result", {}).get("risks_detected", [])),
                    "scenarios": len(data.get("simulation_result", {}).get("scenarios", [])),
                    "decisions": len(data.get("decision_result", {}).get("recommended_actions", [])),
                }
            }
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON from {filepath}: {e}")
            return {
                "status": "error",
                "error": f"Invalid JSON: {e}",
                "filename": filename
            }
        except Exception as e:
            logger.error(f"Failed to load cycle: {e}")
            return {
                "status": "error",
                "error": str(e),
                "filename": filename
            }

    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics of history."""
        try:
            entries = self.list_history(limit=1000)
            
            if not entries:
                return {
                    "total_cycles": 0,
                    "oldest_cycle": None,
                    "newest_cycle": None,
                    "total_storage_mb": 0.0
                }
            
            total_size = sum(e["file_size_bytes"] for e in entries)
            
            return {
                "total_cycles": len(entries),
                "oldest_cycle": entries[-1]["timestamp"] if entries else None,
                "newest_cycle": entries[0]["timestamp"] if entries else None,
                "total_storage_mb": round(total_size / (1024 * 1024), 2),
                "average_size_kb": round(sum(e["file_size_bytes"] for e in entries) / len(entries) / 1024, 2),
            }
        
        except Exception as e:
            logger.error(f"Failed to get summary stats: {e}")
            return {"error": str(e)}

    def delete_cycle(self, filename: str) -> Dict[str, Any]:
        """
        Delete a saved analysis cycle.
        
        Args:
            filename: Timestamp filename (without .json)
            
        Returns:
            Deletion status
        """
        filepath = os.path.join(self.history_dir, f"{filename}.json")
        
        try:
            if not os.path.exists(filepath):
                return {
                    "status": "error",
                    "error": f"File not found: {filepath}"
                }
            
            os.remove(filepath)
            logger.info(f"Deleted cycle: {filepath}")
            
            return {
                "status": "success",
                "deleted_file": filepath
            }
        
        except Exception as e:
            logger.error(f"Failed to delete cycle: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    def export_cycle_csv(self, filename: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Export a cycle's risks and decisions to CSV for reporting.
        
        Args:
            filename: Timestamp filename (without .json)
            output_dir: Directory to save CSVs (defaults to history_dir)
            
        Returns:
            Export status with file paths
        """
        output_dir = output_dir or self.history_dir
        
        try:
            import pandas as pd
            
            # Load the cycle
            result = self.load_cycle(filename)
            if result["status"] != "success":
                return result
            
            data = result["data"]
            exported_files = []
            
            # Export risks
            risks = data.get("risk_result", {}).get("risks_detected", [])
            if risks:
                risks_df = pd.DataFrame(risks)
                risks_path = os.path.join(output_dir, f"{filename}_risks.csv")
                risks_df.to_csv(risks_path, index=False)
                exported_files.append(("Risks", risks_path))
                logger.info(f"Exported risks to {risks_path}")
            
            # Export scenarios
            scenarios = data.get("simulation_result", {}).get("scenarios", [])
            if scenarios:
                scenarios_df = pd.DataFrame(scenarios)
                scenarios_path = os.path.join(output_dir, f"{filename}_scenarios.csv")
                scenarios_df.to_csv(scenarios_path, index=False)
                exported_files.append(("Scenarios", scenarios_path))
                logger.info(f"Exported scenarios to {scenarios_path}")
            
            # Export decisions
            decisions = data.get("decision_result", {}).get("recommended_actions", [])
            if decisions:
                decisions_df = pd.DataFrame(decisions)
                decisions_path = os.path.join(output_dir, f"{filename}_decisions.csv")
                decisions_df.to_csv(decisions_path, index=False)
                exported_files.append(("Decisions", decisions_path))
                logger.info(f"Exported decisions to {decisions_path}")
            
            return {
                "status": "success",
                "exported_files": exported_files,
                "count": len(exported_files)
            }
        
        except ImportError:
            return {
                "status": "error",
                "error": "pandas not available for CSV export"
            }
        except Exception as e:
            logger.error(f"Failed to export CSV: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    @staticmethod
    def _parse_timestamp(filename: str) -> str:
        """
        Parse timestamp from filename.
        Format: YYYYMMDD_HHMMSS → ISO format
        """
        try:
            # Remove .json extension
            timestamp_str = filename.replace(".json", "")
            # Parse YYYYMMDD_HHMMSS
            dt = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
            return dt.isoformat()
        except:
            return filename


# Global singleton instance
persistence = DataPersistence()

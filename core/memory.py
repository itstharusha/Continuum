"""
Shared memory system for agents.
Stores intermediate results, graph state, detected risks, etc.
Simple in-memory dict-based implementation (can be upgraded to Redis later).
"""

from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class AgentMemory:
    """Central memory store shared across all agents."""

    def __init__(self):
        self._store: Dict[str, Any] = {}
        logger.info("AgentMemory initialized")

    def set(self, key: str, value: Any) -> None:
        """Store a value under a key."""
        self._store[key] = value
        logger.debug(f"Memory set: {key} (type: {type(value).__name__})")

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve value by key, with optional default."""
        value = self._store.get(key, default)
        if value is None and default is None:
            logger.warning(f"Memory miss for key: {key}")
        return value

    def clear(self) -> None:
        """Reset memory (useful between full cycles)."""
        self._store.clear()
        logger.info("Memory cleared")

    def dump(self) -> Dict[str, Any]:
        """Return full current state (for debugging/logging)."""
        return dict(self._store)


# Global singleton instance (simple for now)
memory = AgentMemory()
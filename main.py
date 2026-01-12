"""
Supply Chain Risk Sentinel – Main Entry Point
Runs continuous monitoring cycles
"""

import logging
import time
import signal
import sys
from core.orchestrator import Orchestrator

# ─── Logging Configuration ───────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-7s | %(name)-18s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

# Global flag for graceful shutdown
RUNNING = True


def signal_handler(sig, frame):
    global RUNNING
    logger.info("\nShutdown signal received. Finishing current cycle and stopping...")
    RUNNING = False


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def main():
    logger.info("═" * 70)
    logger.info("SUPPLY CHAIN RISK SENTINEL – STARTING CONTINUOUS MONITORING")
    logger.info("Press Ctrl+C to stop gracefully")
    logger.info("═" * 70)

    orchestrator = Orchestrator()

    cycle_count = 0
    config = {
        # Future: API keys, real news sources, etc.
        "max_news_articles": 10
    }

    while RUNNING:
        cycle_count += 1
        logger.info(f"\nCycle #{cycle_count} starting...")

        result = orchestrator.run_single_cycle(config)

        if result["status"] == "success":
            summary = result["summary"]
            logger.info("Quick Summary:")
            logger.info(f"  Suppliers:       {summary['suppliers']}")
            logger.info(f"  News items:      {summary['news_items']}")
            logger.info(f"  Risks found:     {summary['risks_detected']}")
            logger.info(f"  Max severity:    {summary['max_risk_severity']:.2f}")
            logger.info(f"  Worst delay:     {summary['worst_delay_days']} days")
            logger.info(f"  Decisions made:  {summary['decisions_count']}")
            logger.info(f"  Top action:      {summary['top_action']}")
        else:
            logger.error("Cycle failed – see logs above for details")

        if RUNNING:
            sleep_minutes = 5  # ← change this for testing (e.g. 0.5 for fast cycles)
            logger.info(f"Next cycle in {sleep_minutes} minutes... (Ctrl+C to stop)")
            time.sleep(sleep_minutes * 60)

    logger.info("Supply Chain Risk Sentinel stopped gracefully.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Interrupted by user – shutting down.")
    except Exception as e:
        logger.critical("Fatal startup error", exc_info=True)
        sys.exit(1)
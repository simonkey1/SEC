"""Run Historical ETL - Entry point for loading historical SEC data to PostgreSQL.

Simple script that instantiates and runs the HistoricalETLOrchestrator.
This is the entry point that you execute manually.
"""

import sys
import logging
from pathlib import Path

sys.path.append(".")

from core.historical_etl_orchestrator import HistoricalETLOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def main():
    """Main ETL execution."""

    # JSON file path
    json_file = "outputs/dataset_completo_2017_2025.json"

    # Check if file exists
    if not Path(json_file).exists():
        print(f"❌ File not found: {json_file}")
        print("💡 Run the async scraper first to generate the data")
        return

    # Instantiate and run orchestrator
    with HistoricalETLOrchestrator(json_file) as orchestrator:
        orchestrator.load_all()
        # Optional: Load only specific years
        # orchestrator.load_all(start_year=2020, end_year=2025)


if __name__ == "__main__":
    main()

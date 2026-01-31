"""Main execution script (Orchestrator).

This script initializes the scraper and transformer, executing an
infinite loop that captures SEC data every 5 minutes, processes it and saves
it to local storage.
"""

import os
import sys
import time
from datetime import datetime

# Add root directory to path for modular imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import logging

from cleanup_old_data import cleanup_old_records

from core.circuitbreaker import CircuitBreaker
from core.database import SupabaseRepository, check_database_capacity
from core.scraper_alternative import (
    SECScraperAlternative,
)  # Usar scraper con fetch directo
from core.tranformer import SecDataTransformer

logger = logging.getLogger(__name__)


def main():
    """Main execution loop.

    Instantiates core components and manages the timed cycle
    of capture, transformation and persistence.
    """

    breaker = CircuitBreaker(3, 600)
    repo = SupabaseRepository()

    bot = SECScraperAlternative()  # Usar scraper con fetch directo
    transformer = SecDataTransformer()

    cycle_counter = 0

    while True:
        now = datetime.now().strftime("%H:%M:%S")
        print(f"\n🔍 [{now}] Starting data capture...")
        if breaker.can_execute():
            try:
                result = bot.run()
                breaker.register_success()
                raw_data = result.get("data", [])
                server_time = result.get("server_time")

                if raw_data:
                    print(f"✅ Captured {len(raw_data)} raw records.")
                    ready_data = transformer.transform(
                        raw_data, server_time_raw=server_time
                    )

                    # Save to Supabase (production)
                    db_result = repo.save_records(ready_data)
                    logger.info(
                        f"💾 Supabase: {db_result['insertados']} inserted, {db_result['duplicados']} duplicates"
                    )
                else:
                    print("⚠️ No data detected (possible page slowness or no outages).")

            except Exception as e:
                breaker.register_failure()
                logger.error(f"❌ Scraper error: {e}")
                import traceback

                logger.error(f"Traceback: {traceback.format_exc()}")
        else:
            logger.info("Circuit open...")

        if cycle_counter % 288 == 0:
            status = check_database_capacity(threshold_percent=85)
            logger.info(f"📊 DB: {status['porcentaje']:.1f}% ({status['size_mb']} MB)")

        if cycle_counter % 2016 == 0:
            deleted = cleanup_old_records(days_to_keep=30)
            logger.info(f"Cleanup: {deleted} records deleted")

        cycle_counter += 1
        print("⏳ Waiting 5 minutes for next update...")
        time.sleep(300)


if __name__ == "__main__":
    main()

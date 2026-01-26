"""Historical ETL Orchestrator - Coordinates ETL pipeline for historical SEC data.

Optimized version with Parallel Processing and Progress Bars (tqdm).
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from tqdm import tqdm

from core.postgres_repository import PostgreSQLRepository
from core.tranformer import SecDataTransformer

logger = logging.getLogger(__name__)


class HistoricalETLOrchestrator:
    """Orchestrator for historical SEC data ETL pipeline.

    Optimized for high performance using ThreadPoolExecutor and tqdm.
    """

    def __init__(
        self,
        json_file: str,
        repository: Optional[PostgreSQLRepository] = None,
        transformer: Optional[SecDataTransformer] = None,
        max_workers: int = 4,
        batch_size: int = 5000,
    ):
        """Initialize the data loader.

        Args:
            json_file: Path to JSON file
            repository: PostgreSQL repository
            transformer: Data transformer
            max_workers: Number of parallel threads
            batch_size: Size of each DB insert batch
        """
        self.json_file = Path(json_file)
        self.repository = repository or PostgreSQLRepository()
        self.transformer = transformer or SecDataTransformer()
        self.max_workers = max_workers
        self.batch_size = batch_size

        self.stats = {
            "total_inserted": 0,
            "years_processed": 0,
            "start_time": None,
            "end_time": None,
        }

    def load_json(self) -> Dict[str, Any]:
        """Load JSON data from file."""
        if not self.json_file.exists():
            raise FileNotFoundError(f"JSON file not found: {self.json_file}")

        logger.info(
            f"📂 Loading heavy JSON: {self.json_file} (This may take a moment...)"
        )
        with open(self.json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data

    def _process_chunk_worker(self, raw_data: list, hora_server: str):
        """Worker function to transform and save a chunk of data."""
        try:
            # Transform
            transformed = self.transformer.transform(
                raw_data, server_time_raw=hora_server
            )

            # Load
            if transformed:
                result = self.repository.save_records(transformed)
                return result["insertados"]
            return 0
        except Exception as e:
            logger.error(f"❌ Worker error: {e}")
            return 0

    def load_all(
        self, start_year: Optional[int] = None, end_year: Optional[int] = None
    ):
        """Fast load using parallels and tqdm."""
        print("\n" + "=" * 70)
        print("SEC HIGH-PERFORMANCE ETL - 6.2M RECORDS")
        print("=" * 70 + "\n")

        # Initial state
        initial_count = self.repository.get_record_count()
        data = self.load_json()

        # Calculate total records for progress bar
        total_batches_all = 0
        all_work_units = []  # List of (data_chunk, hora_server)

        for year_str, year_info in data.get("data_by_year", {}).items():
            yr = int(year_str)
            if start_year and yr < start_year:
                continue
            if end_year and yr > end_year:
                continue

            year_batches = year_info.get("data", [])
            for batch in year_batches:
                raw = batch.get("data", [])
                if raw:
                    all_work_units.append((raw, batch.get("hora_server_scraping")))
                    total_batches_all += 1

        self.stats["start_time"] = datetime.now()

        print(f"🚀 Starting parallel ETL with {self.max_workers} workers...")

        # Global Progress Bar
        with tqdm(
            total=total_batches_all,
            desc="ETL Total Progress",
            unit="batch",
            colour="green",
        ) as pbar:
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = {
                    executor.submit(self._process_chunk_worker, chunk, server_time): i
                    for i, (chunk, server_time) in enumerate(all_work_units)
                }

                for future in as_completed(futures):
                    inserted = future.result()
                    self.stats["total_inserted"] += inserted
                    pbar.update(1)
                    # Update description with speed
                    if self.stats["total_inserted"] > 0:
                        elapsed = (
                            datetime.now() - self.stats["start_time"]
                        ).total_seconds()
                        rps = (
                            self.stats["total_inserted"] / elapsed if elapsed > 0 else 0
                        )
                        pbar.set_postfix({"RPS": f"{rps:.0f}"})

        self.stats["end_time"] = datetime.now()
        self._print_summary(initial_count)

    def _print_summary(self, initial_count: int):
        final_count = self.repository.get_record_count()
        final_size = self.repository.get_database_size()
        duration = (self.stats["end_time"] - self.stats["start_time"]).total_seconds()

        print("\n" + "=" * 70)
        print("ETL COMPLETE")
        print("=" * 70)
        print(f"\n📊 Summary:")
        print(f"   Initial records: {initial_count:,}")
        print(f"   Newly Inserted: {self.stats['total_inserted']:,}")
        print(f"   Final total: {final_count:,}")
        print(f"   Duration: {duration / 60:.1f} minutes")
        print(
            f"   Avg Speed: {self.stats['total_inserted'] / duration:.0f} records/sec"
        )
        print(f"   Database size: {final_size['size_pretty']}")
        print(f"\n✅ Ready for analysis!\n")

    def close(self):
        self.repository.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

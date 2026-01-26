"""Async Historical Scraper - Configurable class for scraping SEC historical data.

This module provides a reusable async scraper that can scrape any date range
with configurable concurrency and intervals.
"""

import asyncio
import json
import time
from pathlib import Path
from datetime import datetime
from typing import List, Optional
import sys

sys.path.append(".")
from test_async_scraper import scrape_point_async


class AsyncHistoricalScraper:
    """Async scraper for historical SEC data with configurable parameters.

    Attributes:
        start_year: First year to scrape (inclusive)
        end_year: Last year to scrape (inclusive)
        max_concurrent: Maximum concurrent requests
        hours: Hours to scrape each day (default: [0, 6, 12, 18])
        output_dir: Directory to save results
    """

    def __init__(
        self,
        start_year: int,
        end_year: int,
        max_concurrent: int = 50,
        hours: Optional[List[int]] = None,
        output_dir: str = "outputs",
    ):
        """Initialize the async historical scraper.

        Args:
            start_year: First year to scrape (e.g., 2017)
            end_year: Last year to scrape (e.g., 2025)
            max_concurrent: Max concurrent requests (default: 50)
            hours: Hours to scrape per day (default: [0, 6, 12, 18])
            output_dir: Output directory (default: "outputs")
        """
        self.start_year = start_year
        self.end_year = end_year
        self.max_concurrent = max_concurrent
        self.hours = hours or [0, 6, 12, 18]
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Calculated properties
        self.years = list(range(start_year, end_year + 1))
        self.total_years = len(self.years)

    def _get_days_in_month(self, year: int, month: int) -> int:
        """Get number of days in a month."""
        if month in [1, 3, 5, 7, 8, 10, 12]:
            return 31
        elif month in [4, 6, 9, 11]:
            return 30
        else:  # February
            return 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28

    async def scrape_year(self, year: int, year_idx: int) -> dict:
        """Scrape all data for a single year.

        Args:
            year: Year to scrape
            year_idx: Index of year (for progress display)

        Returns:
            dict: Year results with metadata and data
        """
        print(f"\n{'=' * 70}")
        print(f"📅 AÑO {year} ({year_idx}/{self.total_years})")
        print(f"{'=' * 70}\n")

        year_start = time.time()
        year_results = []

        # Process each month
        for month in range(1, 13):
            days_in_month = self._get_days_in_month(year, month)
            month_points = days_in_month * len(self.hours)

            print(f"  📆 {year}-{month:02d}: {month_points} puntos")

            # Create tasks for the month
            semaphore = asyncio.Semaphore(self.max_concurrent)
            tasks = []
            point_num = 0

            for day in range(1, days_in_month + 1):
                for hour in self.hours:
                    point_num += 1
                    task = scrape_point_async(
                        year, month, day, hour, semaphore, point_num
                    )
                    tasks.append(task)

            # Execute month
            month_results = await asyncio.gather(*tasks, return_exceptions=True)
            year_results.extend(month_results)

            # Progress
            successful = sum(
                1 for r in month_results if isinstance(r, dict) and r.get("success")
            )
            print(f"     ✅ {successful}/{len(month_results)} exitosos")

        # Year summary
        year_duration = time.time() - year_start
        year_successful = sum(
            1 for r in year_results if isinstance(r, dict) and r.get("success")
        )
        year_records = sum(
            len(r.get("data", [])) for r in year_results if isinstance(r, dict)
        )

        print(f"\n  ✅ Año {year} completado:")
        print(f"     Exitosos: {year_successful}/{len(year_results)}")
        print(f"     Registros: {year_records:,}")
        print(f"     Tiempo: {year_duration:.1f}s ({year_duration / 60:.1f} min)")

        year_data = {
            "metadata": {
                "year": year,
                "total_points": len(year_results),
                "successful": year_successful,
                "total_records": year_records,
                "duration": year_duration,
            },
            "data": year_results,
        }

        # Save checkpoint
        checkpoint_file = self.output_dir / f"checkpoint_{year}.json"
        with open(checkpoint_file, "w", encoding="utf-8") as f:
            json.dump(year_data, f, indent=2, ensure_ascii=False)
        print(f"     💾 Checkpoint guardado: {checkpoint_file}")

        return year_data

    async def scrape_all(self) -> dict:
        """Scrape all configured years.

        Returns:
            dict: Complete dataset with metadata and all years
        """
        print("=" * 70)
        print("ASYNC HISTORICAL SCRAPER")
        print("=" * 70)
        print(f"Años: {self.start_year}-{self.end_year} ({self.total_years} años)")
        print(f"Horas por día: {self.hours}")
        print(f"Concurrencia: {self.max_concurrent}")
        print(f"Output: {self.output_dir}")
        print("=" * 70)
        print()

        total_start = time.time()
        all_results = {}

        # Process each year
        for year_idx, year in enumerate(self.years, 1):
            year_data = await self.scrape_year(year, year_idx)
            all_results[str(year)] = year_data

        total_duration = time.time() - total_start

        # Final summary
        total_points = sum(len(all_results[str(y)]["data"]) for y in self.years)
        total_successful = sum(
            all_results[str(y)]["metadata"]["successful"] for y in self.years
        )
        total_records = sum(
            all_results[str(y)]["metadata"]["total_records"] for y in self.years
        )

        print("\n" + "=" * 70)
        print("✅ SCRAPING COMPLETADO")
        print("=" * 70)
        print(f"Años procesados: {self.total_years}")
        print(f"Puntos totales: {total_points:,}")
        print(
            f"Exitosos: {total_successful:,}/{total_points:,} "
            f"({total_successful / total_points * 100:.1f}%)"
        )
        print(f"Registros totales: {total_records:,}")
        print(
            f"Duración total: {total_duration / 60:.1f} minutos "
            f"({total_duration / 3600:.2f} horas)"
        )
        print(f"Velocidad promedio: {total_points / total_duration:.2f} puntos/s")
        print("=" * 70)

        # Save final dataset
        final_file = self.output_dir / f"dataset_{self.start_year}_{self.end_year}.json"
        final_data = {
            "metadata": {
                "title": "Dataset Completo - Interrupciones Eléctricas Chile",
                "start_year": self.start_year,
                "end_year": self.end_year,
                "years": self.years,
                "hours": self.hours,
                "total_points": total_points,
                "total_successful": total_successful,
                "total_records": total_records,
                "duration_minutes": total_duration / 60,
                "scraping_date": datetime.now().isoformat(),
                "concurrency": self.max_concurrent,
            },
            "data_by_year": all_results,
        }

        with open(final_file, "w", encoding="utf-8") as f:
            json.dump(final_data, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Dataset final guardado en: {final_file}")

        # File size
        size_mb = final_file.stat().st_size / (1024 * 1024)
        print(f"📊 Tamaño del archivo: {size_mb:.1f} MB")

        return final_data


# Convenience function for backward compatibility
async def scrape_full_dataset(years=None, max_concurrent=50):
    """Legacy function for backward compatibility.

    Args:
        years: List of years to scrape
        max_concurrent: Max concurrent requests

    Returns:
        dict: Complete dataset
    """
    if years is None:
        years = [2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]

    start_year = min(years)
    end_year = max(years)

    scraper = AsyncHistoricalScraper(
        start_year=start_year, end_year=end_year, max_concurrent=max_concurrent
    )

    return await scraper.scrape_all()


if __name__ == "__main__":
    print("🚀 Iniciando scraping histórico asíncrono...\n")

    # Example: Scrape 2017-2025 with 50 concurrent requests
    scraper = AsyncHistoricalScraper(
        start_year=2017,
        end_year=2025,
        max_concurrent=50,
        hours=[0, 6, 12, 18],  # 4 snapshots per day
    )

    asyncio.run(scraper.scrape_all())

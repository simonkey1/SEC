"""Example script using AsyncHistoricalScraper.

Shows how to use the configurable async scraper for different scenarios.
"""

import asyncio
import sys

sys.path.append(".")

from core.async_historical_scraper import AsyncHistoricalScraper


async def example_full_dataset():
    """Example: Scrape complete dataset (2017-2025)."""
    scraper = AsyncHistoricalScraper(
        start_year=2017,
        end_year=2025,
        max_concurrent=50,
        hours=[0, 6, 12, 18],  # 4 snapshots per day
    )

    await scraper.scrape_all()


async def example_single_year():
    """Example: Scrape only 2024."""
    scraper = AsyncHistoricalScraper(start_year=2024, end_year=2024, max_concurrent=50)

    await scraper.scrape_all()


async def example_recent_years():
    """Example: Scrape only recent years (2023-2025)."""
    scraper = AsyncHistoricalScraper(
        start_year=2023,
        end_year=2025,
        max_concurrent=30,  # Lower concurrency
    )

    await scraper.scrape_all()


async def example_hourly_snapshots():
    """Example: Scrape with hourly snapshots (more granular)."""
    scraper = AsyncHistoricalScraper(
        start_year=2025,
        end_year=2025,
        max_concurrent=50,
        hours=list(range(0, 24)),  # Every hour
    )

    await scraper.scrape_all()


if __name__ == "__main__":
    print("Ejemplos de uso de AsyncHistoricalScraper\n")
    print("1. Dataset completo (2017-2025)")
    print("2. Un solo año (2024)")
    print("3. Años recientes (2023-2025)")
    print("4. Snapshots por hora (2025)")
    print()

    choice = input("Selecciona un ejemplo (1-4): ")

    if choice == "1":
        asyncio.run(example_full_dataset())
    elif choice == "2":
        asyncio.run(example_single_year())
    elif choice == "3":
        asyncio.run(example_recent_years())
    elif choice == "4":
        asyncio.run(example_hourly_snapshots())
    else:
        print("Opción inválida")

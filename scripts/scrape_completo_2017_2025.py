"""Scraper completo: 9 años (2017-2025) con concurrencia 50."""

import asyncio
import sys

sys.path.append(".")
from test_async_scraper import scrape_point_async
import json
from pathlib import Path
from datetime import datetime
import time

class ScraperHistorical:
    def __init__(self):
        self.   

    async def scrape_full_dataset(
        years=[2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025], max_concurrent=50
    ):
        """Scrape completo de múltiples años."""

        print("=" * 70)
        print("SCRAPING COMPLETO - DATASET FINAL")
        print("=" * 70)
        print(f"Años: {', '.join(map(str, years))} ({len(years)} años)")
        print(f"Concurrencia: {max_concurrent}")
        print("=" * 70)
        print()

        all_results = {}
        total_start = time.time()

        for year_idx, year in enumerate(years, 1):
            print(f"\n{'=' * 70}")
            print(f"📅 AÑO {year} ({year_idx}/{len(years)})")
        print(f"{'=' * 70}\n")

        year_start = time.time()
        year_results = []

        # Calcular días por mes
        for month in range(1, 13):
            days_in_month = 31 if month in [1, 3, 5, 7, 8, 10, 12] else 30
            if month == 2:
                days_in_month = 29 if year % 4 == 0 else 28

            month_points = days_in_month * 4
            print(f"  📆 {year}-{month:02d}: {month_points} puntos")

            # Crear tareas del mes
            semaphore = asyncio.Semaphore(max_concurrent)
            tasks = []
            point_num = 0

            for day in range(1, days_in_month + 1):
                for hour in [0, 6, 12, 18]:
                    point_num += 1
                    task = scrape_point_async(
                        year, month, day, hour, semaphore, point_num
                    )
                    tasks.append(task)

            # Ejecutar mes
            month_results = await asyncio.gather(*tasks, return_exceptions=True)
            year_results.extend(month_results)

            # Progreso
            successful = sum(
                1 for r in month_results if isinstance(r, dict) and r.get("success")
            )
            print(f"     ✅ {successful}/{len(month_results)} exitosos")

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

        all_results[str(year)] = {
            "metadata": {
                "year": year,
                "total_points": len(year_results),
                "successful": year_successful,
                "total_records": year_records,
                "duration": year_duration,
            },
            "data": year_results,
        }

        # Guardar checkpoint por año
        checkpoint_file = Path("outputs") / f"checkpoint_{year}.json"
        with open(checkpoint_file, "w", encoding="utf-8") as f:
            json.dump(all_results[str(year)], f, indent=2, ensure_ascii=False)
        print(f"     💾 Checkpoint guardado: {checkpoint_file}")

    total_duration = time.time() - total_start

    # Resumen final
    total_points = sum(len(all_results[str(y)]["data"]) for y in years)
    total_successful = sum(all_results[str(y)]["metadata"]["successful"] for y in years)
    total_records = sum(all_results[str(y)]["metadata"]["total_records"] for y in years)

    print("\n" + "=" * 70)
    print("✅ SCRAPING COMPLETADO")
    print("=" * 70)
    print(f"Años procesados: {len(years)}")
    print(f"Puntos totales: {total_points:,}")
    print(
        f"Exitosos: {total_successful:,}/{total_points:,} ({total_successful / total_points * 100:.1f}%)"
    )
    print(f"Registros totales: {total_records:,}")
    print(
        f"Duración total: {total_duration / 60:.1f} minutos ({total_duration / 3600:.2f} horas)"
    )
    print(f"Velocidad promedio: {total_points / total_duration:.2f} puntos/s")
    print("=" * 70)

    # Guardar dataset final
    final_file = Path("outputs") / "dataset_completo_2017_2025.json"
    with open(final_file, "w", encoding="utf-8") as f:
        json.dump(
            {
                "metadata": {
                    "title": "Dataset Completo - Interrupciones Eléctricas Chile",
                    "years": years,
                    "total_points": total_points,
                    "total_successful": total_successful,
                    "total_records": total_records,
                    "duration_minutes": total_duration / 60,
                    "scraping_date": datetime.now().isoformat(),
                    "concurrency": max_concurrent,
                },
                "data_by_year": all_results,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )

    print(f"\n💾 Dataset final guardado en: {final_file}")

    # Calcular tamaño
    size_mb = final_file.stat().st_size / (1024 * 1024)
    print(f"📊 Tamaño del archivo: {size_mb:.1f} MB")

    return all_results


if __name__ == "__main__":
    print("🚀 Iniciando scraping completo de 9 años (2017-2025)...\n")
    print("☕ Tiempo estimado: ~48 minutos\n")

    asyncio.run(
        scrape_full_dataset(
            years=[2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025],
            max_concurrent=50,
        )
    )

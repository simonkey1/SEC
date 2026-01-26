"""Export data from PostgreSQL to CSV/Parquet for analysis.

Exports interruption data in various formats for analysis with Pandas/Polars.
"""

import os
import sys
import logging
from pathlib import Path
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.postgres_repository import PostgreSQLRepository

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def export_full_dataset(repo: PostgreSQLRepository, output_dir: Path):
    """Export complete dataset."""

    logger.info("📊 Exporting full dataset...")

    query = """
    SELECT 
        hash_id,
        fecha_interrupcion,
        hora_interrupcion,
        nombre_region,
        nombre_comuna,
        nombre_empresa,
        clientes_afectados,
        actualizado_hace,
        fecha_int_str,
        hora_server_scraping
    FROM interrupciones
    ORDER BY hora_server_scraping
    """

    with repo.conn.cursor() as cur:
        cur.execute(query)
        columns = [desc[0] for desc in cur.description]
        data = cur.fetchall()

    df = pd.DataFrame(data, columns=columns)

    # Save as CSV
    csv_file = output_dir / "dataset_completo.csv"
    df.to_csv(csv_file, index=False, encoding="utf-8")
    logger.info(
        f"✅ CSV saved: {csv_file} ({csv_file.stat().st_size / 1024 / 1024:.1f} MB)"
    )

    # Save as Parquet
    parquet_file = output_dir / "dataset_completo.parquet"
    df.to_parquet(parquet_file, index=False, compression="snappy")
    logger.info(
        f"✅ Parquet saved: {parquet_file} ({parquet_file.stat().st_size / 1024 / 1024:.1f} MB)"
    )

    return df


def export_by_region_year(repo: PostgreSQLRepository, output_dir: Path):
    """Export aggregated data by region-year."""

    logger.info("📊 Exporting region-year aggregation...")

    query = """
    SELECT 
        nombre_region,
        EXTRACT(YEAR FROM fecha_interrupcion) as año,
        COUNT(*) as num_eventos,
        SUM(clientes_afectados) as total_clientes_afectados,
        AVG(clientes_afectados) as promedio_clientes_afectados
    FROM interrupciones
    WHERE nombre_region IS NOT NULL
    GROUP BY nombre_region, EXTRACT(YEAR FROM fecha_interrupcion)
    ORDER BY nombre_region, año
    """

    with repo.conn.cursor() as cur:
        cur.execute(query)
        columns = [desc[0] for desc in cur.description]
        data = cur.fetchall()

    df = pd.DataFrame(data, columns=columns)

    csv_file = output_dir / "agregado_region_año.csv"
    df.to_csv(csv_file, index=False, encoding="utf-8")
    logger.info(f"✅ Region-year aggregation saved: {csv_file}")

    return df


def export_summary_stats(repo: PostgreSQLRepository, output_dir: Path):
    """Export summary statistics."""

    logger.info("📊 Generating summary statistics...")

    queries = {
        "by_year": """
            SELECT 
                EXTRACT(YEAR FROM fecha_interrupcion) as año,
                COUNT(*) as num_eventos,
                SUM(clientes_afectados) as total_clientes,
                AVG(clientes_afectados) as promedio_clientes
            FROM interrupciones
            GROUP BY EXTRACT(YEAR FROM fecha_interrupcion)
            ORDER BY año
        """,
        "by_region": """
            SELECT 
                nombre_region,
                COUNT(*) as num_eventos,
                SUM(clientes_afectados) as total_clientes,
                AVG(clientes_afectados) as promedio_clientes
            FROM interrupciones
            WHERE nombre_region IS NOT NULL
            GROUP BY nombre_region
            ORDER BY num_eventos DESC
        """,
        "by_company": """
            SELECT 
                nombre_empresa,
                COUNT(*) as num_eventos,
                SUM(clientes_afectados) as total_clientes,
                AVG(clientes_afectados) as promedio_clientes
            FROM interrupciones
            WHERE nombre_empresa IS NOT NULL
            GROUP BY nombre_empresa
            ORDER BY num_eventos DESC
        """,
    }

    for name, query in queries.items():
        with repo.conn.cursor() as cur:
            cur.execute(query)
            columns = [desc[0] for desc in cur.description]
            data = cur.fetchall()

        df = pd.DataFrame(data, columns=columns)
        csv_file = output_dir / f"summary_{name}.csv"
        df.to_csv(csv_file, index=False, encoding="utf-8")
        logger.info(f"✅ Summary {name} saved: {csv_file}")


def main():
    """Main export execution."""

    print("\n" + "=" * 70)
    print("EXPORT DATA FROM POSTGRESQL")
    print("=" * 70 + "\n")

    # Initialize repository
    logger.info("🔧 Connecting to PostgreSQL...")
    repo = PostgreSQLRepository()

    # Check database state
    count = repo.get_record_count()
    size = repo.get_database_size()
    logger.info(f"📊 Database: {count:,} records, {size['size_pretty']}\n")

    # Create output directory
    output_dir = Path("data/exports")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Export full dataset
    df_full = export_full_dataset(repo, output_dir)
    print(f"\n📊 Full dataset: {len(df_full):,} records")

    # Export aggregations
    df_region_year = export_by_region_year(repo, output_dir)
    print(f"📊 Region-year: {len(df_region_year):,} combinations")

    # Export summaries
    export_summary_stats(repo, output_dir)

    # Close connection
    repo.close()

    print("\n" + "=" * 70)
    print("EXPORT COMPLETE")
    print("=" * 70)
    print(f"\n📁 Files saved in: {output_dir.absolute()}")
    print(f"\n💡 Use these files for analysis with Pandas/Polars/DuckDB\n")


if __name__ == "__main__":
    main()

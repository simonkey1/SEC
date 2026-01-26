"""Procesamiento inicial del dataset con Polars.

Polars es ~10-100x más rápido que Pandas para datasets grandes.
"""

import polars as pl
import json
from pathlib import Path
from datetime import datetime


def load_dataset_efficient():
    """Carga el dataset de forma eficiente con Polars."""

    print("=" * 70)
    print("CARGANDO DATASET CON POLARS")
    print("=" * 70)
    print()

    # Opción 1: Cargar desde checkpoints (más rápido)
    print("📂 Cargando desde checkpoints individuales...")

    dfs = []
    for year in range(2017, 2026):
        checkpoint_file = Path(f"outputs/checkpoint_{year}.json")

        if checkpoint_file.exists():
            print(f"  📅 Cargando {year}...", end=" ")

            # Leer JSON
            with open(checkpoint_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Extraer registros
            all_records = []
            for result in data["data"]:
                if isinstance(result, dict) and "data" in result:
                    for record in result["data"]:
                        # Agregar metadata de consulta
                        record["fecha_consultada"] = result.get("fecha_consultada", "")
                        record["year"] = year
                        all_records.append(record)

            # Crear DataFrame de Polars
            df_year = pl.DataFrame(all_records)
            dfs.append(df_year)

            print(f"✅ {len(all_records):,} registros")

    # Concatenar todos los años
    print("\n🔗 Concatenando años...")
    df = pl.concat(dfs)

    print(f"\n✅ Dataset cargado: {len(df):,} registros")
    print(f"📊 Memoria usada: ~{df.estimated_size() / 1024**2:.1f} MB")

    return df


def basic_eda(df):
    """Análisis exploratorio básico."""

    print("\n" + "=" * 70)
    print("ANÁLISIS EXPLORATORIO BÁSICO")
    print("=" * 70)
    print()

    # Info general
    print("📊 Información del Dataset:")
    print(f"  Registros: {len(df):,}")
    print(f"  Columnas: {len(df.columns)}")
    print(f"  Años: {df['year'].unique().sort()}")
    print()

    # Columnas
    print("📋 Columnas disponibles:")
    for col in df.columns:
        print(f"  - {col}")
    print()

    # Estadísticas por año
    print("📈 Registros por año:")
    year_stats = (
        df.group_by("year")
        .agg(
            [
                pl.count().alias("registros"),
                pl.col("CLIENTES_AFECTADOS").sum().alias("total_clientes_afectados"),
                pl.col("CLIENTES_AFECTADOS").mean().alias("promedio_clientes"),
            ]
        )
        .sort("year")
    )
    print(year_stats)
    print()

    # Top empresas
    print("🏢 Top 10 empresas por registros:")
    top_empresas = (
        df.group_by("NOMBRE_EMPRESA")
        .agg([pl.count().alias("registros")])
        .sort("registros", descending=True)
        .head(10)
    )
    print(top_empresas)
    print()

    # Top regiones
    print("🗺️ Top 10 regiones por clientes afectados:")
    top_regiones = (
        df.group_by("NOMBRE_REGION")
        .agg([pl.col("CLIENTES_AFECTADOS").sum().alias("total_clientes_afectados")])
        .sort("total_clientes_afectados", descending=True)
        .head(10)
    )
    print(top_regiones)
    print()

    return df


def save_processed_data(df):
    """Guarda datos procesados en formato eficiente."""

    print("=" * 70)
    print("GUARDANDO DATOS PROCESADOS")
    print("=" * 70)
    print()

    # Parquet (mucho más eficiente que JSON)
    parquet_file = Path("outputs/dataset_completo.parquet")
    print(f"💾 Guardando en Parquet: {parquet_file}")
    df.write_parquet(parquet_file, compression="zstd")

    size_mb = parquet_file.stat().st_size / (1024**2)
    print(f"✅ Guardado: {size_mb:.1f} MB")
    print(f"📉 Compresión: {3700 / size_mb:.1f}x vs JSON original")
    print()

    # CSV para compatibilidad
    csv_file = Path("outputs/dataset_completo.csv")
    print(f"💾 Guardando en CSV: {csv_file}")
    df.write_csv(csv_file)

    csv_size_mb = csv_file.stat().st_size / (1024**2)
    print(f"✅ Guardado: {csv_size_mb:.1f} MB")
    print()


if __name__ == "__main__":
    print("🚀 Iniciando procesamiento con Polars...\n")

    # Cargar datos
    df = load_dataset_efficient()

    # EDA básico
    df = basic_eda(df)

    # Guardar procesado
    save_processed_data(df)

    print("\n✅ Procesamiento completado!")
    print("\n💡 Próximos pasos:")
    print("  1. Usar dataset_completo.parquet para análisis (mucho más rápido)")
    print("  2. Calcular métricas SAIDI/SAIFI")
    print("  3. Análisis temporal y regional")
    print("  4. Mapear eventos de desastres")

import sys

sys.path.append(".")

import polars as pl
import pandas as pd
import plotly.express as px
import os
from scripts.analysis.eda_polars import SecDataExplorer
from scripts.analysis.analyze_seia import SeiaAnalyzer


def main():
    print("🔬 Iniciando Análisis de Correlación Inversión vs Confiabilidad...")

    # 1. Obtener datos de interrupciones (Golden Record)
    parquet_path = "outputs/golden_interrupciones.parquet"
    if os.path.exists(parquet_path):
        print(f"🚀 Cargando Golden Record desde {parquet_path}...")
        df_sec_raw = pl.read_parquet(parquet_path)
        # Ajuste de columnas para compatibilidad: 'fecha_dt' -> 'fecha', y extraer año
        df_sec_raw = df_sec_raw.with_columns(pl.col("fecha_dt").dt.year().alias("año"))
    else:
        # Fallback a deprecated loader
        explorer = SecDataExplorer()
        df_sec_raw = explorer.load_data()

    # Calcular métricas por región y año
    # Usamos la misma ponderación que definimos antes
    ponderacion = {
        "METROPOLITANA": 2500,
        "VALPARAISO": 880,
        "BIOBIO": 720,
        "MAULE": 440,
        "LA ARAUCANIA": 430,
        "O'HIGGINS": 400,
        "LOS LAGOS": 350,
        "COQUIMBO": 340,
        "ANTOFAGASTA": 220,
        "NUBLE": 210,
        "LOS RIOS": 170,
        "TARAPACA": 150,
        "ATACAMA": 110,
        "ARICA Y PARINACOTA": 100,
        "MAGALLANES": 80,
        "AYSEN": 40,
    }
    df_pob = pl.DataFrame(
        {
            "nombre_region": list(ponderacion.keys()),
            "clientes_reg_k": list(ponderacion.values()),
        }
    )

    df_sec = (
        df_sec_raw.group_by(["nombre_region", "año"])
        .agg(pl.col("clientes_afectados").sum().alias("total_afectados"))
        .join(df_pob, on="nombre_region")
    )

    # Normalizar: Afectados por 1,000 habitantes en ese año
    df_sec = df_sec.with_columns(
        (pl.col("total_afectados") / pl.col("clientes_reg_k")).alias("tasa_afectados")
    )

    # 2. Obtener datos de inversión
    seia = SeiaAnalyzer()
    seia.load_and_clean()
    df_inv = seia.aggregate_by_region_year()

    # 3. Join Final
    # Nota: La inversión suele tener efecto retardado (Lags), pero iniciaremos con correlación directa
    df_final = df_sec.join(df_inv, on=["nombre_region", "año"], how="inner")

    if df_final.is_empty():
        print(
            "⚠️ No hay intersección de datos entre SEC y SEIA para los mismos años/regiones."
        )
        return

    # 4. Cálculo de Correlación
    corr = df_final.select(pl.corr("total_inversión_mmu", "tasa_afectados")).item()
    print(f"\n📈 Correlación Pearson (Inversión vs Tasa de Fallas): {corr:.4f}")

    # 5. Visualización
    fig = px.scatter(
        df_final.to_pandas(),
        x="total_inversión_mmu",
        y="tasa_afectados",
        color="nombre_region",
        size="n_proyectos",
        hover_data=["año"],
        title="Correlación: Inversión en Energía vs Tasa de Interrupción (por Región)",
        labels={
            "total_inversión_mmu": "Inversión MMU$",
            "tasa_afectados": "Afectados / 1k Clientes",
        },
        template="plotly_dark",
    )
    fig.show()


if __name__ == "__main__":
    main()

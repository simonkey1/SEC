import sys

sys.path.append(".")

import polars as pl
import plotly.express as px
import os
from datetime import timedelta


class AnomalyDiagnoser:
    def __init__(self):
        self.parquet_path = "outputs/golden_interrupciones.parquet"

    def diagnose(self):
        if not os.path.exists(self.parquet_path):
            print("❌ No Golden Data.")
            return

        print("🚀 Analizando anomalías temporales y de magnitud...")
        df = pl.read_parquet(self.parquet_path)

        # 1. Análisis de Continuidad (Gap Analysis)
        # Agrupar por día
        df_daily = (
            df.group_by("fecha_dt")
            .agg(pl.col("clientes_afectados").sum().alias("total_diario"))
            .sort("fecha_dt")
        )

        # Generar rango completo de fechas esperado
        min_date = df_daily["fecha_dt"].min()
        max_date = df_daily["fecha_dt"].max()
        print(f"📅 Rango de Datos: {min_date} al {max_date}")

        # Detectar días faltantes
        # (Polars no tiene 'resample' directo como pandas para gaps, lo simulamos o pasamos a pandas)
        pdf = df_daily.to_pandas()
        pdf["fecha_dt"] = list(
            map(lambda x: x.isoformat(), pdf["fecha_dt"])
        )  # fix date obj

        # 2. Análisis de "Ceros" y "Caídas Bruscas"
        zeros = df_daily.filter(pl.col("total_diario") == 0)
        print(
            f"⚠️ Días con 0 afectados (¿Falla de Scraper o Red Perfecta?): {len(zeros)}"
        )

        # 3. Visualizar la serie diaria para ver los "cortes"
        fig = px.line(
            pdf,
            x="fecha_dt",
            y="total_diario",
            title="Diagnóstico: Total Afectados Diario (Busca Gaps/Ceros)",
            template="plotly_dark",
            log_y=True,  # Log scale para ver mejor los ceros/bajos
        )
        fig.show()

        # 4. Top Caídas (Diferencia día a día)
        df_daily = df_daily.with_columns(
            pl.col("total_diario").diff().alias("cambio_diario")
        ).sort("cambio_diario")

        print("📉 Top 5 Caídas más bruscas (Día vs Día anterior):")
        print(df_daily.head(5))


if __name__ == "__main__":
    diag = AnomalyDiagnoser()
    diag.diagnose()

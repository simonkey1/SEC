import sys

sys.path.append(".")

import polars as pl
import plotly.express as px
import os
from scripts.analysis.analyze_seia import SeiaAnalyzer


class SocialROIAnalyzer:
    def __init__(self):
        self.parquet_path = "outputs/golden_interrupciones.parquet"

    def analyze(self):
        if not os.path.exists(self.parquet_path):
            print("❌ No Golden Data.")
            return

        print("🚀 Calculando Social ROI (Eficiencia de Inversión)...")

        # 1. Cargar Datos de Cortes (Numerador: El Problema)
        df_sec = pl.read_parquet(self.parquet_path)

        # Agrupar por Región (Total Histórico 2017-2025)
        df_problem = df_sec.group_by("nombre_region").agg(
            pl.col("clientes_afectados").sum().alias("total_afectados")
        )

        # 2. Cargar Datos de Inversión (Denominador: La Solución)
        seia = SeiaAnalyzer()
        seia.load_and_clean()
        df_inv_raw = seia.aggregate_by_region_year()

        # Agrupar por Región (Suma total histórica)
        df_solution = df_inv_raw.group_by("nombre_region").agg(
            pl.col("total_inversión_mmu").sum().alias("total_inversion_mmu")
        )

        # 3. Join y Cálculo del Ratio
        df_roi = df_problem.join(df_solution, on="nombre_region", how="inner")

        # Métrica: "Costo de Sufrimiento"
        # ¿Cuántos clientes se siguen cortando por cada Millón de Dólares invertido?
        # Alto = Ineficiente / Estructuralmente Roto.
        # Bajo = Eficiente / Estable.

        df_roi = df_roi.with_columns(
            (pl.col("total_afectados") / pl.col("total_inversion_mmu")).alias(
                "clientes_x_mmu"
            )
        ).sort("clientes_x_mmu", descending=True)

        print(df_roi)

        # 4. Visualización Ranking
        pdf = df_roi.to_pandas()

        fig = px.bar(
            pdf,
            x="clientes_x_mmu",
            y="nombre_region",
            orientation="h",
            title="Ranking de Ineficiencia: Clientes Afectados por cada MMU$ Invertido",
            labels={
                "clientes_x_mmu": "Clientes Afectados / MMU$ (Ratio)",
                "nombre_region": "Región",
            },
            color="clientes_x_mmu",
            color_continuous_scale="RdYlGn_r",  # Low (Efficient) = Green, High (Inefficient) = Red
            template="plotly_dark",
            text_auto=".1f",
        )

        fig.update_layout(
            yaxis=dict(autorange="reversed"),
            xaxis_title="Ineficiencia (Más alto es peor)",
            coloraxis_colorbar_title="Ineficiencia (Afectados/MMU$)",
        )

        fig.show()


if __name__ == "__main__":
    analyzer = SocialROIAnalyzer()
    analyzer.analyze()

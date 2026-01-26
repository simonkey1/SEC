import sys

sys.path.append(".")

import polars as pl
import plotly.express as px
import os


class CompanyRankingAnalyzer:
    def __init__(self):
        self.parquet_path = "outputs/golden_interrupciones.parquet"

    def analyze(self):
        if not os.path.exists(self.parquet_path):
            print("❌ No Golden Data.")
            return

        print("🚀 Calculando Ranking de Empresas (The 'Bad Actors' List)...")
        df = pl.read_parquet(self.parquet_path)

        # 1. Agrupar por Empresa
        # Métricas: Total Eventos, Total Afectados, Promedio Afectados por evento
        df_ranking = (
            df.group_by("nombre_empresa")
            .agg(
                pl.len().alias("total_eventos"),
                pl.col("clientes_afectados").sum().alias("total_clientes_afectados"),
                pl.col("clientes_afectados").mean().alias("promedio_afectados"),
            )
            .sort("total_clientes_afectados", descending=True)
            .head(15)  # Top 15 para no ensuciar el gráfico con cooperativas chicas
        )

        print(df_ranking)

        # 2. Visualización: Scatter Plot (Frecuencia vs Severidad)
        # Eje X: Cantidad de Cortes (Frecuencia)
        # Eje Y: Total Afectados (Impacto Social)
        # Tamaño: Promedio por corte (Severidad Unitaria)

        pdf = df_ranking.to_pandas()

        fig = px.scatter(
            pdf,
            x="total_eventos",
            y="total_clientes_afectados",
            size="promedio_afectados",  # Burbuja grande = Cortes masivos
            color="nombre_empresa",
            text="nombre_empresa",
            title="Mapa de Responsabilidad: Frecuencia vs Impacto por Empresa (2017-2025)",
            labels={
                "total_eventos": "Cantidad de Cortes (Frecuencia)",
                "total_clientes_afectados": "Total Clientes Afectados (Impacto Acumulado)",
            },
            template="plotly_dark",
            log_x=True,  # Log scale porque CGE/Enel distorsionan todo
            log_y=True,
        )

        fig.update_traces(textposition="top center")
        fig.update_layout(showlegend=False)
        fig.show()


if __name__ == "__main__":
    analyzer = CompanyRankingAnalyzer()
    analyzer.analyze()

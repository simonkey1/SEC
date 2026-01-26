import sys

sys.path.append(".")

import polars as pl
import plotly.express as px
import os


class RankingAnalyzer:
    def __init__(self):
        self.parquet_path = "outputs/golden_interrupciones.parquet"

    def load_data(self):
        if os.path.exists(self.parquet_path):
            print(f"🚀 Cargando Golden Record para Rankings...")
            return pl.read_parquet(self.parquet_path)
        else:
            return None

    def plot_top_offenders(self, df):
        # 1. Top Comunas (Por frecuencia de cortes)
        print("📊 Generando Ranking de Comunas...")
        df_comunas = (
            df.group_by("nombre_comuna")
            .agg(
                [
                    pl.len().alias("num_cortes"),
                    pl.col("clientes_afectados").sum().alias("total_afectados"),
                ]
            )
            .sort("num_cortes", descending=True)
            .head(10)
        )

        pdf_comunas = df_comunas.to_pandas()

        fig_com = px.bar(
            pdf_comunas,
            x="num_cortes",
            y="nombre_comuna",
            orientation="h",
            title="Top 10 Comunas con Mayor Frecuencia de Cortes (Histórico)",
            text="num_cortes",
            template="plotly_dark",
            color="total_afectados",  # Color por severidad
            labels={"num_cortes": "Cantidad de Eventos", "nombre_comuna": "Comuna"},
        )
        fig_com.update_layout(yaxis=dict(autorange="reversed"))
        fig_com.show()

        # 2. Top Empresas (Por Clientes Afectados)
        print("📊 Generando Ranking de Empresas...")
        df_emp = (
            df.group_by("nombre_empresa")
            .agg(
                [
                    pl.len().alias("num_cortes"),
                    pl.col("clientes_afectados").sum().alias("total_afectados"),
                ]
            )
            .sort("total_afectados", descending=True)
            .head(10)
        )

        pdf_emp = df_emp.to_pandas()

        fig_emp = px.bar(
            pdf_emp,
            x="total_afectados",
            y="nombre_empresa",
            orientation="h",
            title="Top 10 Empresas por Clientes Afectados (Histórico)",
            text="total_afectados",
            template="plotly_dark",
            color="num_cortes",
            color_continuous_scale="Viridis",
            labels={
                "total_afectados": "Total Clientes Afectados",
                "nombre_empresa": "Empresa",
            },
        )
        fig_emp.update_layout(yaxis=dict(autorange="reversed"))
        fig_emp.show()

        print("✅ Rankings generados.")


if __name__ == "__main__":
    analyzer = RankingAnalyzer()
    df = analyzer.load_data()
    if df is not None:
        analyzer.plot_top_offenders(df)

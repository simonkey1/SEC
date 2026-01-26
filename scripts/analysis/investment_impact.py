import sys

sys.path.append(".")

import polars as pl
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from scripts.analysis.analyze_seia import SeiaAnalyzer


class InvestmentImpactExplorer:
    def __init__(self):
        self.parquet_path = "outputs/golden_interrupciones.parquet"

    def load_data(self):
        # 1. Load SEC (Golden Data)
        if not os.path.exists(self.parquet_path):
            print("❌ No Golden Data found.")
            return None, None

        print("🚀 Cargando datos SEC y SEIA...")
        df_sec_raw = pl.read_parquet(self.parquet_path)

        # Aggregate SEC by Region/Year
        df_sec = (
            df_sec_raw.with_columns(pl.col("fecha_dt").dt.year().alias("año"))
            .group_by(["nombre_region", "año"])
            .agg(pl.col("clientes_afectados").sum().alias("total_afectados"))
        )

        # 2. Load SEIA (Investment)
        seia = SeiaAnalyzer()
        seia.load_and_clean()
        df_inv = (
            seia.aggregate_by_region_year()
        )  # columns: nombre_region, año, total_inversión_mmu

        return df_sec, df_inv

    def plot_impact_for_region(self, region_name, df_sec, df_inv):
        # Filter Data
        sec_reg = df_sec.filter(pl.col("nombre_region") == region_name).sort("año")
        inv_reg = df_inv.filter(pl.col("nombre_region") == region_name).sort("año")

        # Join to ensure years match
        df_joint = (
            sec_reg.join(inv_reg, on=["nombre_region", "año"], how="outer")
            .sort("año")
            .fill_null(0)
        )

        pdf = df_joint.to_pandas()

        # Dual Axis Plot
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Bar: Inversión (MMU$)
        fig.add_trace(
            go.Bar(
                x=pdf["año"],
                y=pdf["total_inversión_mmu"],
                name="Inversión (MMU$)",
                marker_color="#F59E0B",  # Amber
                opacity=0.6,
            ),
            secondary_y=False,
        )

        # Line: Afectados
        fig.add_trace(
            go.Scatter(
                x=pdf["año"],
                y=pdf["total_afectados"],
                name="Clientes Afectados",
                mode="lines+markers",
                marker_color="#EF4444",  # Red
                line=dict(width=4),
            ),
            secondary_y=True,
        )

        fig.update_layout(
            title=f"Impacto de Inversión en {region_name}: Dinero vs Cortes",
            template="plotly_dark",
            legend=dict(orientation="h", y=1.1),
            xaxis_title="Año",
            xaxis=dict(tickmode="linear"),
        )

        fig.update_yaxes(title_text="Inversión (Millones USD)", secondary_y=False)
        fig.update_yaxes(title_text="Clientes Afectados", secondary_y=True)

        fig.show()


if __name__ == "__main__":
    explorer = InvestmentImpactExplorer()
    df_sec, df_inv = explorer.load_data()

    if df_sec is not None:
        # Analizar regiones interesantes (Top inversión o Top problemas)
        explorer.plot_impact_for_region("METROPOLITANA", df_sec, df_inv)
        explorer.plot_impact_for_region("ANTOFAGASTA", df_sec, df_inv)
        explorer.plot_impact_for_region("MAULE", df_sec, df_inv)

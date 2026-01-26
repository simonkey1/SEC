import sys

sys.path.append(".")

import polars as pl
import plotly.express as px
import os


class SeverityAnalyzer:
    def __init__(self):
        self.parquet_path = "outputs/golden_interrupciones.parquet"

    def load_data(self):
        if os.path.exists(self.parquet_path):
            print(f"🚀 Cargando Golden Record para análisis de severidad...")
            return pl.read_parquet(self.parquet_path)
        else:
            print("❌ No se encontró el Golden Dataset. Ejecuta el EDA primero.")
            return None

    def plot_severity_distribution(self, df):
        print("📊 Generando Histograma de Severidad...")
        pdf = df.to_pandas()

        # 1. Histograma (Log Scale para ver micro-cortes vs blackouts)
        fig_hist = px.histogram(
            pdf,
            x="clientes_afectados",
            nbins=100,
            log_y=True,
            title="Distribución de Severidad de Cortes (Escala Log)",
            labels={
                "clientes_afectados": "Clientes Afectados (Bin)",
                "count": "Frecuencia",
            },
            template="plotly_dark",
            color_discrete_sequence=["#F59E0B"],  # Amber
        )
        fig_hist.update_layout(
            xaxis_title="Magnitud del Corte (Clientes)",
            yaxis_title="Cantidad de Eventos (Log)",
        )
        fig_hist.show()

        # 2. Boxplot por Región (Para ver quién tiene los eventos más masivos)
        print("📊 Generando Boxplot por Región...")

        # Filtramos para quitar outliers extremos visualmente si es necesario,
        # pero para análisis queremos verlos.
        fig_box = px.box(
            pdf,
            x="nombre_region",
            y="clientes_afectados",
            log_y=True,
            title="Severidad de Cortes por Región (Log)",
            labels={
                "nombre_region": "Región",
                "clientes_afectados": "Clientes Afectados",
            },
            template="plotly_dark",
            color="nombre_region",
        )
        fig_box.update_layout(showlegend=False)
        fig_box.show()

        print("✅ Visualizaciones generadas.")


if __name__ == "__main__":
    analyzer = SeverityAnalyzer()
    df = analyzer.load_data()
    if df is not None:
        analyzer.plot_severity_distribution(df)

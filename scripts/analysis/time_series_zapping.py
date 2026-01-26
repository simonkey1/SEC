import sys

sys.path.append(".")

import polars as pl
import os
from dotenv import load_dotenv
import plotly.express as px
from datetime import datetime


class SecTimeSeriesExplorer:
    """Explorador de series de tiempo estilo Zapping."""

    def __init__(self):
        load_dotenv()
        db_user = os.getenv("DB_USER", "postgres")
        db_pass = os.getenv("DB_PASSWORD", "acidosa123")
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = os.getenv("DB_PORT", "5432")
        db_name = os.getenv("DB_NAME", "sec_interrupciones")
        self.uri = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

    def load_and_aggregate(self):
        parquet_path = "outputs/golden_interrupciones.parquet"

        if os.path.exists(parquet_path):
            print(f"🚀 Cargando Golden Record desde {parquet_path}...")
            df = pl.read_parquet(parquet_path)
            # Renombrar columna fecha_dt a fecha para compatibilidad
            df = df.rename({"fecha_dt": "fecha"})
        else:
            print("⚠️ Parquet no encontrado. Cargando desde DB (Datos crudos)...")
            query = """
                SELECT 
                    f.clientes_afectados,
                    t.fecha,
                    g.nombre_region
                FROM fact_interrupciones f
                JOIN dim_tiempo t ON f.id_tiempo = t.id_tiempo
                JOIN dim_geografia g ON f.id_geografia = g.id_geografia
            """
            df = pl.read_database_uri(query, self.uri, engine="adbc")

        # Agrupar por mes y región
        # Creamos una columna 'mes_año' para el eje X
        df = df.with_columns(pl.col("fecha").dt.truncate("1mo").alias("mes_trunc"))

        # Filtrar solo las Top 6 regiones para no saturar el gráfico (estilo Zapping)
        top_regions = (
            df.group_by("nombre_region")
            .agg(pl.col("clientes_afectados").sum().alias("total"))
            .sort("total", descending=True)
            .head(6)["nombre_region"]
            .to_list()
        )

        df_top = df.filter(pl.col("nombre_region").is_in(top_regions))

        ts_data = (
            df_top.group_by(["mes_trunc", "nombre_region"])
            .agg(pl.col("clientes_afectados").sum().alias("clientes_afectados"))
            .sort(["mes_trunc", "nombre_region"])
        )

        return ts_data

    def plot_zapping_style(self, df):
        print("🎨 Generando gráfico estilo Zapping...")
        pdf = df.to_pandas()

        # Estilo Zapping: Line chart con áreas rellenas y puntos
        fig = px.line(
            pdf,
            x="mes_trunc",
            y="clientes_afectados",
            color="nombre_region",
            title="Evolución de Interrupciones Eléctricas por Región (Histórico)",
            labels={
                "clientes_afectados": "Clientes Afectados",
                "mes_trunc": "Tiempo",
                "nombre_region": "Región",
            },
            template="plotly_dark",
            markers=True,
            line_shape="spline",  # Curvas suaves como en la imagen
            render_mode="svg",
        )

        # Rellenar áreas (estilo Zapping)
        for i, d in enumerate(fig.data):
            d.fill = "tonexty" if i > 0 else "tozeroy"
            d.line.width = 3

        fig.update_layout(
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
            ),
            hovermode="x unified",
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.1)"),
        )

        fig.show()
        # Guardar imagen para el walkthrough
        image_path = os.path.abspath("outputs/zapping_analysis.png")
        # Plotly show usually opens a browser, but we can't capture that directly as an image easily without kaleido
        # We'll just print that it's ready.
        print(f"✅ Análisis listo. Visualizando ahora.")


if __name__ == "__main__":
    explorer = SecTimeSeriesExplorer()
    ts_df = explorer.load_and_aggregate()
    explorer.plot_zapping_style(ts_df)

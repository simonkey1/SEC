import sys

sys.path.append(".")

import polars as pl
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os


class StormAnalyzer:
    def __init__(self):
        self.parquet_path = "outputs/golden_interrupciones.parquet"

    def load_data(self):
        if not os.path.exists(self.parquet_path):
            return None
        return pl.read_parquet(self.parquet_path)

    def analyze_event(self, df, event_name, start_date, end_date, save_path=None):
        print(f"🌪️ Analizando {event_name} ({start_date} al {end_date})...")

        # Filtro temporal
        df_event = df.filter(
            (pl.col("fecha_dt") >= start_date) & (pl.col("fecha_dt") <= end_date)
        )

        if df_event.is_empty():
            print("⚠️ No data found for this range.")
            return

        # 1. Evolución Temporal (Granularidad Horaria/Snapshot)
        # Como tenemos hora_int, podemos ver la curva de "Entrada de fallas"
        # O mejor, agrupar por el timestamp del registro si lo tuviéramos,
        # pero usamos fecha_dt + hora_int para simular la linea de tiempo.
        # Agrupamos por bloques de 6 horas para limpiar la visual.

        df_timeline = (
            df_event.with_columns(
                pl.datetime(
                    pl.col("fecha_dt").dt.year(),
                    pl.col("fecha_dt").dt.month(),
                    pl.col("fecha_dt").dt.day(),
                    pl.col("hora_int").dt.hour(),
                    pl.col("hora_int").dt.minute(),
                    pl.col("hora_int").dt.second(),
                ).alias("datetime")
            )
            .group_by(pl.col("datetime").dt.truncate("6h").alias("bloque_6h"))
            .agg(pl.col("clientes_afectados").sum().alias("total_afectados"))
            .sort("bloque_6h")
        )

        # 2. Top Comunas Afectadas (Acumulado en el evento)
        df_comunas = (
            df_event.group_by("nombre_comuna")
            .agg(
                pl.col("clientes_afectados").max().alias("peak_afectados")
            )  # Peak simultáneo, no suma
            .sort("peak_afectados", descending=True)
            .head(10)
        )

        # Visualización Combinada
        pdf_time = df_timeline.to_pandas()
        pdf_com = df_comunas.to_pandas()

        fig = make_subplots(
            rows=2,
            cols=1,
            subplot_titles=(
                f"Evolución Temporal: {event_name} (Bloques 6h)",
                f"Comunas más Golpeadas (Peak de Afectados)",
            ),
            vertical_spacing=0.15,
        )

        # Line Chart (Timeline)
        fig.add_trace(
            go.Scatter(
                x=pdf_time["bloque_6h"],
                y=pdf_time["total_afectados"],
                mode="lines+markers",
                name="Clientes sin Luz",
                line=dict(color="#00d4ff", width=3),
                fill="tozeroy",
            ),
            row=1,
            col=1,
        )

        # Bar Chart (Comunas)
        fig.add_trace(
            go.Bar(
                x=pdf_com["nombre_comuna"],
                y=pdf_com["peak_afectados"],
                name="Peak Afectados",
                marker_color="#ff4d4d",
            ),
            row=2,
            col=1,
        )

        fig.update_layout(
            template="plotly_dark",
            height=900,
            title_text=f"Autopsia del Corte: {event_name}",
            showlegend=False,
        )

        if save_path:
            # Crear directorio si no existe
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            fig.write_html(save_path)
            print(f"✅ Reporte guardado en {save_path}")
        else:
            fig.show()


if __name__ == "__main__":
    analyzer = StormAnalyzer()
    df = analyzer.load_data()

    if df is not None:
        from datetime import date, timedelta

        # Test mode
        pass

        # 2017 Nevazón
        analyzer.analyze_event(
            df, "Gran Nevazón 2017", date(2017, 7, 14), date(2017, 7, 20)
        )

        # 2024 Viento
        analyzer.analyze_event(
            df, "Temporal Viento 2024 (Nacional)", date(2024, 7, 31), date(2024, 8, 10)
        )

        # CASOS REGIONALES (Sugeridos por análisis)
        # 3. Araucanía 2017 (Sur)
        analyzer.analyze_event(
            df,
            "Corte Masivo Araucanía (Agosto 2017)",
            date(2017, 8, 10),
            date(2017, 8, 16),
        )

        # 4. Coquimbo 2019 (Norte - Verano)
        analyzer.analyze_event(
            df, "Blackout Coquimbo (Enero 2019)", date(2019, 1, 15), date(2019, 1, 22)
        )

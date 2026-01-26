import sys

sys.path.append(".")

import polars as pl
import os


class RegionalEventFinder:
    def __init__(self):
        self.parquet_path = "outputs/golden_interrupciones.parquet"

    def find_events(self):
        if not os.path.exists(self.parquet_path):
            return

        print("🚀 Escaneando TODOS los eventos masivos (Por Región/Año)...")
        df = pl.read_parquet(self.parquet_path)

        # 1. Agregar año para iterar
        df_daily = (
            df.with_columns(
                [
                    pl.col("fecha_dt").alias("fecha"),
                    pl.col("fecha_dt").dt.year().alias("año"),
                ]
            )
            .group_by(["año", "fecha", "nombre_region"])
            .agg(pl.col("clientes_afectados").sum().alias("total_afectados"))
        )

        # 2. Encontrar el PEAK anual de cada región
        # Partition by Region, Year -> Take Max
        df_peaks = (
            df_daily.sort("total_afectados", descending=True)
            .group_by(["nombre_region", "año"])
            .head(1)  # El evento mas grande de ese año en esa region
            .sort(["nombre_region", "año"])
        )

        # 3. Filtrar solo eventos "Relevantes" (> 30.000 hogares, para ignorar ruido)
        major_events = df_peaks.filter(pl.col("total_afectados") > 30000).sort(
            "total_afectados", descending=True
        )

        print(
            f"\n🏆 Se encontraron {len(major_events)} eventos masivos (>30k) en total."
        )
        print(major_events)

        # Exportar a CSV para que el usuario pueda ver la lista completa si quiere
        output_csv = "outputs/lista_maestra_cortes.csv"
        major_events.write_csv(output_csv)
        print(f"\n💾 Lista guardada en {output_csv}")


if __name__ == "__main__":
    finder = RegionalEventFinder()
    finder.find_events()

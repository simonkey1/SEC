import pandas as pd
import polars as pl
import os
from dotenv import load_dotenv


class SeiaAnalyzer:
    def __init__(self, excel_path="outputs/Proyectos.xlsx"):
        self.excel_path = excel_path

    def normalize_region_name(self, name):
        if not isinstance(name, str):
            return "DESCONOCIDO"
        name = name.upper()
        if "ARICA" in name:
            return "ARICA Y PARINACOTA"
        if "TARAPACA" in name:
            return "TARAPACA"
        if "ANTOFAGASTA" in name:
            return "ANTOFAGASTA"
        if "ATACAMA" in name:
            return "ATACAMA"
        if "COQUIMBO" in name:
            return "COQUIMBO"
        if "VALPARAISO" in name:
            return "VALPARAISO"
        if "METROPOLITANA" in name:
            return "METROPOLITANA"
        if "O'HIGGINS" in name:
            return "O'HIGGINS"
        if "MAULE" in name:
            return "MAULE"
        if "NUBLE" in name or "ÑUBLE" in name:
            return "NUBLE"
        if "BIOBIO" in name or "BÍOBÍO" in name:
            return "BIOBIO"
        if "ARAUCANIA" in name:
            return "LA ARAUCANIA"
        if "LOS RIOS" in name:
            return "LOS RIOS"
        if "LOS LAGOS" in name:
            return "LOS LAGOS"
        if "AYSEN" in name:
            return "AYSEN"
        if "MAGALLANES" in name:
            return "MAGALLANES"
        return "OTRO"

    def load_and_clean(self):
        print(f"📖 Cargando SEIA desde {self.excel_path}...")
        # Usar pandas para leer excel, luego convertir a Polars
        pdf = pd.read_excel(self.excel_path)

        # Limpiar inversión (MMU$) - Convertir a float
        # Asumiendo que puede venir con formatos tipo "1.234,56" o similar
        if pdf["Inversión (MMU$)"].dtype == object:
            pdf["inv_clean"] = (
                pdf["Inversión (MMU$)"]
                .str.replace(".", "")
                .str.replace(",", ".")
                .astype(float)
            )
        else:
            pdf["inv_clean"] = pdf["Inversión (MMU$)"].astype(float)

        # Extraer Año de 'Fecha Presentación'
        pdf["año"] = pd.to_datetime(pdf["Fecha Presentación"], errors="coerce").dt.year

        # Normalizar Nombre de Región para Join
        # (Ajustar nombres de regiones según convención de la SEC si es necesario)
        pdf["nombre_region"] = pdf["Región"].apply(self.normalize_region_name)

        self.df = pl.from_pandas(pdf)
        return self.df

    def aggregate_by_region_year(self):
        agg = (
            self.df.group_by(["nombre_region", "año"])
            .agg(
                pl.col("inv_clean").sum().alias("total_inversión_mmu"),
                pl.col("Nombre del Proyecto").count().alias("n_proyectos"),
            )
            .sort(["nombre_region", "año"])
        )

        print("\n💰 Inversión Agregada por Región-Año (Muestra):")
        print(agg.head(10))
        return agg


if __name__ == "__main__":
    analyzer = SeiaAnalyzer()
    df_inv = analyzer.load_and_clean()
    analyzer.aggregate_by_region_year()

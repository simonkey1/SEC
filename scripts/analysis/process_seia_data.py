"""Procesamiento de datos SEIA - Adaptado a estructura real.

Procesa los 164 proyectos de energía descargados del SEIA.
"""

import pandas as pd
from pathlib import Path

# Mapeo de códigos SEIA a categorías
CODIGOS_SEIA = {
    # Transmisión
    "b1": "Transmisión",
    "b.1": "Transmisión",
    "DS95/DS40-b1": "Transmisión",
    "DS95/DS40/DS17-b": "Transmisión",
    "DS17-b1": "Transmisión",
    # Subestaciones
    "b2": "Subestaciones",
    "b.2": "Subestaciones",
    "DS95/DS40/DS17-b2": "Subestaciones",
    # Generación
    "c": "Generación",
    "DS95/DS40/DS17-c": "Generación",
    # Otros
    "o6": "Otros",
    "DS95/DS40/DS17-o6": "Otros",
}


def process_seia_data(input_file="outputs/Proyectos.xlsx"):
    """Procesa datos de SEIA y los categoriza."""

    print("=" * 70)
    print("PROCESANDO DATOS SEIA")
    print("=" * 70)
    print()

    # Leer Excel
    print(f"📂 Cargando: {input_file}")
    df = pd.read_excel(input_file)

    print(f"✅ Cargados: {len(df):,} proyectos")
    print()

    # Limpiar nombres de columnas
    df.columns = df.columns.str.strip()

    # Extraer año de calificación
    df["año_calificacion"] = pd.to_datetime(df["Fecha Calificación"]).dt.year

    # Mapear códigos a categorías
    print("🏷️ Categorizando proyectos...")
    df["categoria"] = df["Tipo de Proyecto"].map(CODIGOS_SEIA).fillna("Otros")

    # Filtrar solo proyectos eléctricos relevantes
    df_electricos = df[
        df["categoria"].isin(["Transmisión", "Subestaciones", "Generación"])
    ].copy()

    print(f"✅ Proyectos eléctricos: {len(df_electricos):,}")
    print()

    # Resumen por categoría
    print("📊 Resumen por categoría:")
    resumen = (
        df_electricos.groupby("categoria")
        .agg({"Nombre del Proyecto": "count", "Inversión (MMU$)": ["sum", "mean"]})
        .round(2)
    )
    resumen.columns = [
        "Cantidad",
        "Inversión Total (MMUS$)",
        "Inversión Promedio (MMUS$)",
    ]
    print(resumen)
    print()

    # Resumen por año
    print("📈 Inversión por año:")
    por_año = (
        df_electricos.groupby("año_calificacion")
        .agg({"Nombre del Proyecto": "count", "Inversión (MMU$)": "sum"})
        .round(2)
    )
    por_año.columns = ["Proyectos", "Inversión Total (MMUS$)"]
    print(por_año)
    print()

    # Resumen por región
    print("🗺️ Top 10 regiones por inversión:")
    por_region = (
        df_electricos.groupby("Región")
        .agg({"Nombre del Proyecto": "count", "Inversión (MMU$)": "sum"})
        .round(2)
        .sort_values("Inversión (MMU$)", ascending=False)
        .head(10)
    )
    por_region.columns = ["Proyectos", "Inversión Total (MMUS$)"]
    print(por_region)
    print()

    # Crear carpeta de salida
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Guardar procesado
    output_file = output_dir / "seia_inversion_procesada.csv"
    print(f"💾 Guardando datos procesados: {output_file}")
    df_electricos.to_csv(output_file, index=False, encoding="utf-8")
    print("✅ Guardado")
    print()

    return df_electricos


def aggregate_by_region_year(df):
    """Agrega inversión por región y año para análisis."""

    print("=" * 70)
    print("AGREGANDO POR REGIÓN Y AÑO")
    print("=" * 70)
    print()

    # Agregar por región-año
    df_agg = (
        df.groupby(["Región", "año_calificacion"])
        .agg(
            {
                "Nombre del Proyecto": "count",
                "Inversión (MMU$)": "sum",
                "categoria": lambda x: x.value_counts().to_dict(),
            }
        )
        .reset_index()
    )

    df_agg.columns = [
        "region",
        "año",
        "num_proyectos",
        "inversion_total_mmus",
        "proyectos_por_tipo",
    ]

    print(f"✅ Agregado: {len(df_agg):,} combinaciones región-año")
    print()
    print("Muestra:")
    print(df_agg.head(10))
    print()

    # Guardar
    output_file = Path("data/processed/seia_region_año.csv")
    df_agg.to_csv(output_file, index=False, encoding="utf-8")
    print(f"💾 Guardado: {output_file}")
    print()

    return df_agg


def create_summary_stats(df):
    """Crea estadísticas resumen."""

    print("=" * 70)
    print("ESTADÍSTICAS GENERALES")
    print("=" * 70)
    print()

    stats = {
        "Total Proyectos": len(df),
        "Inversión Total (MMUS$)": df["Inversión (MMU$)"].sum(),
        "Inversión Promedio (MMUS$)": df["Inversión (MMU$)"].mean(),
        "Inversión Mediana (MMUS$)": df["Inversión (MMU$)"].median(),
        "Años Cubiertos": f"{df['año_calificacion'].min()} - {df['año_calificacion'].max()}",
        "Regiones Únicas": df["Región"].nunique(),
        "Empresas Únicas": df["Titular"].nunique(),
    }

    for key, value in stats.items():
        if isinstance(value, float):
            print(f"  {key}: {value:,.2f}")
        else:
            print(f"  {key}: {value}")
    print()

    return stats


if __name__ == "__main__":
    print("🚀 Procesando datos de inversión SEIA...\n")

    # Procesar datos
    df = process_seia_data()

    # Estadísticas
    stats = create_summary_stats(df)

    # Agregar por región-año
    df_agg = aggregate_by_region_year(df)

    print("\n✅ Procesamiento completado!")
    print("\n💡 Archivos generados:")
    print("  - data/processed/seia_inversion_procesada.csv")
    print("  - data/processed/seia_region_año.csv")
    print("\n📊 Listos para correlacionar con datos de interrupciones")

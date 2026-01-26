"""Generar visualizaciones para el Research Paper.

Este script conecta a la DB local, extrae los datos necesarios y genera
las 5 figuras citadas en el documento research_paper.md.
"""

import sys
import os
import logging
from pathlib import Path
from datetime import datetime, date

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import psycopg2
from dotenv import load_dotenv

# Configuración
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)

# Rutas
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DOCS_DIR = BASE_DIR / "docs"
FIGURES_DIR = DOCS_DIR / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# Estilo para publicación científica
plt.style.use("seaborn-v0_8-paper")
sns.set_context("paper", font_scale=1.5)
plt.rcParams["figure.figsize"] = (12, 8)
plt.rcParams["axes.titlesize"] = 16
plt.rcParams["axes.labelsize"] = 14


def get_db_connection():
    load_dotenv(BASE_DIR / ".env")
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD"),
        dbname=os.getenv("DB_NAME", "sec_interrupciones"),
    )


def fetch_data(query, params=None):
    with get_db_connection() as conn:
        return pd.read_sql_query(query, conn, params=params)


def plot_fig1_global_timeseries():
    """Figura 1: Series de Tiempo Globales (Raw SAIFI Proxy)."""
    logger.info("Generando Figura 1: Series de Tiempo...")

    query = """
    SELECT 
        d_t.fecha,
        SUM(f.clientes_afectados) as total_afectados,
        COUNT(f.hash_id) as total_eventos
    FROM fact_interrupciones f
    JOIN dim_tiempo d_t ON f.id_tiempo = d_t.id_tiempo
    GROUP BY d_t.fecha
    ORDER BY d_t.fecha
    """
    df = fetch_data(query)
    df["fecha"] = pd.to_datetime(df["fecha"])

    # Resample mensual para suavizar
    df_monthly = df.set_index("fecha").resample("M").sum().reset_index()

    fig, ax1 = plt.subplots(figsize=(14, 7))

    sns.lineplot(
        data=df_monthly,
        x="fecha",
        y="total_afectados",
        ax=ax1,
        color="#e74c3c",
        linewidth=2,
        label="Clientes Afectados",
    )
    ax1.fill_between(
        df_monthly["fecha"], df_monthly["total_afectados"], color="#e74c3c", alpha=0.1
    )

    ax1.set_title("Figura 1: Evolución Temporal de Interrupciones (2017-2025)", pad=20)
    ax1.set_xlabel("Fecha")
    ax1.set_ylabel("Clientes Afectados (Mensual)", color="#e74c3c")
    ax1.tick_params(axis="y", labelcolor="#e74c3c")
    ax1.grid(True, alpha=0.3)

    # Agregar eventos clave si existen en el rango
    events = [
        (pd.Timestamp("2024-08-01"), "Colapso Viento 2024"),
        (pd.Timestamp("2019-10-18"), "Estallido Social"),
        (pd.Timestamp("2020-03-15"), "Inicio Pandemia"),
        (pd.Timestamp("2017-07-15"), "Nevazón 2017"),
    ]

    for dt, label in events:
        if df["fecha"].min() <= dt <= df["fecha"].max():
            ax1.axvline(dt, color="gray", linestyle="--", alpha=0.7)
            # Alternar altura para que no se solapen
            y_pos = ax1.get_ylim()[1] * (0.9 if "2019" not in label else 0.8)
            ax1.text(dt, y_pos, f" {label}", rotation=90, fontsize=10, color="dimgray")

    # Calcular y mostrar SAIFI Raw anual en consola (para el texto)
    df["year"] = df["fecha"].dt.year
    annual_affected = df.groupby("year")["total_afectados"].sum()
    TOTAL_CLIENTES_ESTIMADO = 6500000  # Base aproximada Chile

    print("\n--- CÁLCULO SAIFI RAW (Estimado) ---")
    for year, affected in annual_affected.items():
        saifi_raw = affected / TOTAL_CLIENTES_ESTIMADO
        print(f"Año {year}: Afectados={affected:,.0f} -> SAIFI Raw ~ {saifi_raw:.2f}")
    print("------------------------------------\n")

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "figura1_timeseries.png", dpi=300)
    plt.close()


def plot_fig2_heatmap():
    """Figura 2: Mapa de Calor Geográfico."""
    logger.info("Generando Figura 2: Mapa de Calor Geográfico...")

    query = """
    SELECT 
        g.nombre_region,
        COUNT(f.hash_id) as eventos
    FROM fact_interrupciones f
    JOIN dim_geografia g ON f.id_geografia = g.id_geografia
    GROUP BY g.nombre_region
    ORDER BY eventos DESC
    """
    df = fetch_data(query)

    plt.figure(figsize=(12, 8))
    sns.barplot(
        data=df,
        y="nombre_region",
        x="eventos",
        palette="viridis",
        hue="nombre_region",
        legend=False,
    )

    plt.title("Figura 2: Frecuencia de Interrupciones por Región", pad=20)
    plt.xlabel("Cantidad de Eventos Registrados")
    plt.ylabel("Región")
    plt.grid(axis="x", alpha=0.3)

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "figura2_heatmap.png", dpi=300)
    plt.close()


def plot_fig3_coquimbo_paradox():
    """Figura 3: La Paradoja de Coquimbo (Detalle 2018-2022)."""
    logger.info("Generando Figura 3: Caso Coquimbo...")

    query = """
    SELECT 
        d_t.fecha,
        SUM(f.clientes_afectados) as afectados
    FROM fact_interrupciones f
    JOIN dim_geografia g ON f.id_geografia = g.id_geografia
    JOIN dim_tiempo d_t ON f.id_tiempo = d_t.id_tiempo
    WHERE g.nombre_region ILIKE '%COQUIMBO%'
      AND d_t.año BETWEEN 2018 AND 2022
    GROUP BY d_t.fecha
    ORDER BY d_t.fecha
    """
    df = fetch_data(query)
    df["fecha"] = pd.to_datetime(df["fecha"])
    df["ma_30"] = df["afectados"].rolling(window=30).mean()  # Media móvil

    plt.figure(figsize=(12, 6))
    plt.plot(df["fecha"], df["afectados"], alpha=0.3, color="gray", label="Diario")
    plt.plot(
        df["fecha"],
        df["ma_30"],
        color="#2980b9",
        linewidth=2.5,
        label="Media Móvil (30 días)",
    )

    # Highlight Cardones-Polpaico period
    plt.axvspan(
        pd.Timestamp("2019-01-01"),
        pd.Timestamp("2019-06-30"),
        color="yellow",
        alpha=0.1,
        label="Energización Cardones-Polpaico",
    )

    plt.title(
        "Figura 3: Caso Coquimbo - Persistencia de Fallas post-Interconexión", pad=20
    )
    plt.xlabel("Fecha")
    plt.ylabel("Clientes Afectados")
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "figura3_coquimbo.png", dpi=300)
    plt.close()


def plot_fig4_arica_redenor():
    """Figura 4: Caso Arica (Antes vs Después)."""
    logger.info("Generando Figura 4: Caso Arica...")

    # Asumiendo un hito en 2020 para ejemplo (ajustar fecha real si se tiene)
    query = """
    SELECT 
        d_t.año,
        SUM(f.clientes_afectados) as total_afectados,
        COUNT(f.hash_id) as total_eventos
    FROM fact_interrupciones f
    JOIN dim_geografia g ON f.id_geografia = g.id_geografia
    JOIN dim_tiempo d_t ON f.id_tiempo = d_t.id_tiempo
    WHERE g.nombre_region ILIKE '%ARICA%'
    GROUP BY d_t.año
    ORDER BY d_t.año
    """
    df = fetch_data(query)

    plt.figure(figsize=(10, 6))
    bars = plt.bar(df["año"], df["total_afectados"], color="#27ae60")

    plt.title("Figura 4: Arica y Parinacota - Evolución Anual de Afectación", pad=20)
    plt.xlabel("Año")
    plt.ylabel("Total Clientes Afectados")
    plt.grid(axis="y", alpha=0.3)

    # Trend line or annotation
    if not df.empty:
        plt.plot(df["año"], df["total_afectados"], "r--o", alpha=0.5)

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "figura4_arica.png", dpi=300)
    plt.close()


def plot_fig5_company_ranking():
    """Figura 5: Ranking de Empresas (Top 10 por afectación)."""
    logger.info("Generando Figura 5: Ranking Empresas...")

    query = """
    SELECT 
        e.nombre_empresa,
        SUM(f.clientes_afectados) as total_afectados
    FROM fact_interrupciones f
    JOIN dim_empresa e ON f.id_empresa = e.id_empresa
    GROUP BY e.nombre_empresa
    ORDER BY total_afectados DESC
    LIMIT 10
    """
    df = fetch_data(query)

    plt.figure(figsize=(12, 8))
    sns.barplot(
        data=df,
        x="total_afectados",
        y="nombre_empresa",
        palette="magma",
        hue="nombre_empresa",
        legend=False,
    )

    plt.title(
        "Figura 5: Top 10 Empresas por Total de Clientes Afectados (2017-2025)", pad=20
    )
    plt.xlabel("Total Clientes Afectados")
    plt.ylabel("")
    plt.grid(axis="x", alpha=0.3)

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "figura5_companies.png", dpi=300)
    plt.close()


def main():
    try:
        plot_fig1_global_timeseries()
        plot_fig2_heatmap()
        plot_fig3_coquimbo_paradox()
        plot_fig4_arica_redenor()
        plot_fig5_company_ranking()
        logger.info("✅ Todas las figuras generadas exitosamente en docs/figures/")
    except Exception as e:
        logger.error(f"❌ Error generando figuras: {e}")
        raise


if __name__ == "__main__":
    main()

"""Generar visualizaciones para el Informe Técnico.

Foco: Volumen de datos, cobertura temporal y distribución de la ingesta.
"""

import os
import logging
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import psycopg2
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DOCS_DIR = BASE_DIR / "docs"
FIGURES_DIR = DOCS_DIR / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

plt.style.use("ggplot")
sns.set_context("notebook")


def get_db_connection():
    load_dotenv(BASE_DIR / ".env")
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD"),
        dbname=os.getenv("DB_NAME", "sec_interrupciones"),
    )


def fetch_data(query):
    with get_db_connection() as conn:
        return pd.read_sql_query(query, conn)


def plot_data_volume():
    """Volumen de registros por mes (Ingesta)."""
    logger.info("Generando Plot Técnico 1: Volumen Mensual...")

    query = """
    SELECT 
        DATE_TRUNC('month', d_t.fecha) as mes,
        COUNT(*) as total_registros
    FROM fact_interrupciones f
    JOIN dim_tiempo d_t ON f.id_tiempo = d_t.id_tiempo
    GROUP BY 1
    ORDER BY 1
    """
    df = fetch_data(query)
    df["mes"] = pd.to_datetime(df["mes"], utc=True)

    plt.figure(figsize=(12, 6))
    plt.fill_between(df["mes"], df["total_registros"], color="skyblue", alpha=0.4)
    plt.plot(df["mes"], df["total_registros"], color="steelblue", marker="o")

    plt.title("Volumen de Datos Ingestados (Escala Mensual)", fontsize=14)
    plt.xlabel("Fecha")
    plt.ylabel("Cantidad de Eventos únicos (Snapshots deduplicados)")
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "tech_fig1_volume.png", dpi=150)
    plt.close()


def plot_temporal_coverage():
    """Heatmap: Día de la Semana vs Hora (Consistencia del Scraping/Dato)."""
    logger.info("Generando Plot Técnico 2: Cobertura Temporal...")

    query = """
    SELECT 
        EXTRACT(DOW FROM d_t.fecha) as dia_semana,
        EXTRACT(HOUR FROM f.hora_interrupcion) as hora,
        COUNT(*) as eventos
    FROM fact_interrupciones f
    JOIN dim_tiempo d_t ON f.id_tiempo = d_t.id_tiempo
    GROUP BY 1, 2
    """
    df = fetch_data(query)

    # Pivotar para heatmap
    pivot_table = df.pivot_table(
        index="hora", columns="dia_semana", values="eventos", aggfunc="sum"
    )
    # Renombrar días
    days = {0: "Dom", 1: "Lun", 2: "Mar", 3: "Mié", 4: "Jue", 5: "Vie", 6: "Sáb"}
    pivot_table.columns = [days.get(c, c) for c in pivot_table.columns]
    # Rellenar con 0
    pivot_table = pivot_table.fillna(0)

    plt.figure(figsize=(10, 8))
    sns.heatmap(pivot_table, cmap="YlGnBu", annot=False, fmt=".0f")

    plt.title("Densidad de Eventos: Hora vs Día de Semana", fontsize=14)
    plt.ylabel("Hora del Día (0-23)")
    plt.xlabel("Día de la Semana")

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "tech_fig2_coverage.png", dpi=150)
    plt.close()


def main():
    try:
        plot_data_volume()
        plot_temporal_coverage()
        logger.info("✅ Figuras técnicas generadas en docs/figures/")
    except Exception as e:
        logger.error(f"❌ Error: {e}")


if __name__ == "__main__":
    main()

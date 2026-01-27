"""Clase unificada para la generación de gráficos (Research & Technical).

Este módulo consolida toda la lógica de visualización en una sola clase 'Plot',
permitiendo la generación de figuras mediante la invocación de métodos específicos.
"""

import os
import logging
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import psycopg2
from dotenv import load_dotenv

# Configuración de logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)


class Plot:
    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent.parent.parent
        self.docs_dir = self.base_dir / "docs"
        self.figures_dir = self.docs_dir / "figures"
        self.figures_dir.mkdir(parents=True, exist_ok=True)

        # Cargar variables de entorno una sola vez
        load_dotenv(self.base_dir / ".env")

    def _get_db_connection(self):
        return psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD"),
            dbname=os.getenv("DB_NAME", "sec_interrupciones"),
        )

    def _fetch_data(self, query, params=None):
        with self._get_db_connection() as conn:
            return pd.read_sql_query(query, conn, params=params)

    def _set_paper_style(self):
        """Configura el estilo para los gráficos del Research Paper."""
        plt.style.use("seaborn-v0_8-paper")
        sns.set_context("paper", font_scale=1.5)
        plt.rcParams["figure.figsize"] = (12, 8)
        plt.rcParams["axes.titlesize"] = 16
        plt.rcParams["axes.labelsize"] = 14

    def _set_technical_style(self):
        """Configura el estilo para los gráficos del Reporte Técnico."""
        plt.style.use("ggplot")
        sns.set_context("notebook")

    # --- FIGURAS RESEARCH PAPER ---

    def plot_fig1_global_timeseries(self):
        """Figura 1: Series de Tiempo Globales (Raw SAIFI Proxy)."""
        self._set_paper_style()
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
        df = self._fetch_data(query)
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
            df_monthly["fecha"],
            df_monthly["total_afectados"],
            color="#e74c3c",
            alpha=0.1,
        )

        ax1.set_title(
            "Figura 1: Evolución Temporal de Interrupciones (2017-2025)", pad=20
        )
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
                ax1.text(
                    dt, y_pos, f" {label}", rotation=90, fontsize=10, color="dimgray"
                )

        plt.tight_layout()
        output_path = self.figures_dir / "figura1_timeseries.png"
        plt.savefig(output_path, dpi=300)
        plt.close()
        logger.info(f"Guardado en {output_path}")

    def plot_fig2_heatmap(self):
        """Figura 2: Mapa de Calor Geográfico."""
        self._set_paper_style()
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
        df = self._fetch_data(query)

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
        output_path = self.figures_dir / "figura2_heatmap.png"
        plt.savefig(output_path, dpi=300)
        plt.close()
        logger.info(f"Guardado en {output_path}")

    def plot_fig3_coquimbo_paradox(self):
        """Figura 3: La Paradoja de Coquimbo (Detalle 2018-2022)."""
        self._set_paper_style()
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
        df = self._fetch_data(query)
        df["fecha"] = pd.to_datetime(df["fecha"])
        df["ma_30"] = df["afectados"].rolling(window=30).mean()

        plt.figure(figsize=(12, 6))
        plt.plot(df["fecha"], df["afectados"], alpha=0.3, color="gray", label="Diario")
        plt.plot(
            df["fecha"],
            df["ma_30"],
            color="#2980b9",
            linewidth=2.5,
            label="Media Móvil (30 días)",
        )

        plt.axvspan(
            pd.Timestamp("2019-01-01"),
            pd.Timestamp("2019-06-30"),
            color="yellow",
            alpha=0.1,
            label="Energización Cardones-Polpaico",
        )

        plt.title(
            "Figura 3: Caso Coquimbo - Persistencia de Fallas post-Interconexión",
            pad=20,
        )
        plt.xlabel("Fecha")
        plt.ylabel("Clientes Afectados")
        plt.legend()
        plt.grid(True, alpha=0.3)

        plt.tight_layout()
        output_path = self.figures_dir / "figura3_coquimbo.png"
        plt.savefig(output_path, dpi=300)
        plt.close()
        logger.info(f"Guardado en {output_path}")

    def plot_fig4_arica_redenor(self):
        """Figura 4: Caso Arica (Antes vs Después)."""
        self._set_paper_style()
        logger.info("Generando Figura 4: Caso Arica...")

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
        df = self._fetch_data(query)

        plt.figure(figsize=(10, 6))
        plt.bar(df["año"], df["total_afectados"], color="#27ae60")

        plt.title(
            "Figura 4: Arica y Parinacota - Evolución Anual de Afectación", pad=20
        )
        plt.xlabel("Año")
        plt.ylabel("Total Clientes Afectados")
        plt.grid(axis="y", alpha=0.3)

        if not df.empty:
            plt.plot(df["año"], df["total_afectados"], "r--o", alpha=0.5)

        plt.tight_layout()
        output_path = self.figures_dir / "figura4_arica.png"
        plt.savefig(output_path, dpi=300)
        plt.close()
        logger.info(f"Guardado en {output_path}")

    def plot_fig5_company_ranking(self):
        """Figura 5: Ranking de Empresas (Top 10 por afectación)."""
        self._set_paper_style()
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
        df = self._fetch_data(query)

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
            "Figura 5: Top 10 Empresas por Total de Clientes Afectados (2017-2025)",
            pad=20,
        )
        plt.xlabel("Total Clientes Afectados")
        plt.ylabel("")
        plt.grid(axis="x", alpha=0.3)

        plt.tight_layout()
        output_path = self.figures_dir / "figura5_companies.png"
        plt.savefig(output_path, dpi=300)
        plt.close()
        logger.info(f"Guardado en {output_path}")

    # --- FIGURAS REPORTE TÉCNICO ---

    def plot_technical_volume(self):
        """Volumen de registros por mes (Ingesta)."""
        self._set_technical_style()
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
        df = self._fetch_data(query)
        df["mes"] = pd.to_datetime(df["mes"], utc=True)

        plt.figure(figsize=(12, 6))
        plt.fill_between(df["mes"], df["total_registros"], color="skyblue", alpha=0.4)
        plt.plot(df["mes"], df["total_registros"], color="steelblue", marker="o")

        plt.title("Volumen de Datos Ingestados (Escala Mensual)", fontsize=14)
        plt.xlabel("Fecha")
        plt.ylabel("Cantidad de Eventos únicos")
        plt.grid(True, alpha=0.3)

        plt.tight_layout()
        output_path = self.figures_dir / "tech_fig1_volume.png"
        plt.savefig(output_path, dpi=150)
        plt.close()
        logger.info(f"Guardado en {output_path}")

    def plot_technical_coverage(self):
        """Heatmap: Día de la Semana vs Hora (Consistencia del Scraping/Dato)."""
        self._set_technical_style()
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
        df = self._fetch_data(query)

        pivot_table = df.pivot_table(
            index="hora", columns="dia_semana", values="eventos", aggfunc="sum"
        )
        days = {0: "Dom", 1: "Lun", 2: "Mar", 3: "Mié", 4: "Jue", 5: "Vie", 6: "Sáb"}
        pivot_table.columns = [days.get(c, c) for c in pivot_table.columns]
        pivot_table = pivot_table.fillna(0)

        plt.figure(figsize=(10, 8))
        sns.heatmap(pivot_table, cmap="YlGnBu", annot=False, fmt=".0f")

        plt.title("Densidad de Eventos: Hora vs Día de Semana", fontsize=14)
        plt.ylabel("Hora del Día (0-23)")
        plt.xlabel("Día de la Semana")

        plt.tight_layout()
        output_path = self.figures_dir / "tech_fig2_coverage.png"
        plt.savefig(output_path, dpi=150)
        plt.close()
        logger.info(f"Guardado en {output_path}")

    def plot_eda_missing_values(self):
        """Visualización de Calidad de Datos: Registros Imputados/Etiquetados."""
        self._set_technical_style()
        logger.info("Generando Plot EDA: Calidad e Imputación...")

        # Consultar conteo de registros imputados/fallback
        query = """
        SELECT 
            (SELECT COUNT(*) FROM fact_interrupciones WHERE clientes_afectados = 0) as afectados_zero,
            (SELECT COUNT(*) FROM fact_interrupciones f JOIN dim_geografia g ON f.id_geografia = g.id_geografia 
             WHERE g.nombre_region = 'DESCONOCIDO' OR g.nombre_comuna = 'DESCONOCIDO') as geo_unknown,
            (SELECT COUNT(*) FROM fact_interrupciones f JOIN dim_empresa e ON f.id_empresa = e.id_empresa 
             WHERE e.nombre_empresa = 'DESCONOCIDO') as empresa_unknown,
            (SELECT COUNT(*) FROM fact_interrupciones) as total_rows
        FROM fact_interrupciones LIMIT 1
        """
        df = self._fetch_data(query)

        total = df["total_rows"].iloc[0]
        afectados_zero = df["afectados_zero"].iloc[0]
        geo_unknown = df["geo_unknown"].iloc[0]
        empresa_unknown = df["empresa_unknown"].iloc[0]

        # Log para el reporte escrito
        logger.info(f"📊 REPORT STATS: Total Rows: {total}")
        logger.info(
            f"📊 REPORT STATS: Afectados=0: {afectados_zero} ({afectados_zero / total:.2%})"
        )
        logger.info(
            f"📊 REPORT STATS: Geo=Unknown: {geo_unknown} ({geo_unknown / total:.2%})"
        )
        logger.info(
            f"📊 REPORT STATS: Emp=Unknown: {empresa_unknown} ({empresa_unknown / total:.2%})"
        )

        # Preparar data para plot
        data = {
            "Categoría": [
                "Afectados = 0 (Imputado)",
                "Geografía Desconocida",
                "Empresa Desconocida",
            ],
            "Cantidad": [afectados_zero, geo_unknown, empresa_unknown],
            "Porcentaje": [
                afectados_zero / total,
                geo_unknown / total,
                empresa_unknown / total,
            ],
        }
        df_plot = pd.DataFrame(data)

        plt.figure(figsize=(10, 6))
        ax = sns.barplot(data=df_plot, x="Cantidad", y="Categoría", palette="Wistia_r")

        # Anotar porcentajes
        for i, (cnt, pct) in enumerate(zip(df_plot["Cantidad"], df_plot["Porcentaje"])):
            ax.text(cnt + (total * 0.01), i, f"{cnt:,} ({pct:.1%})", va="center")

        plt.title(
            f"Transparencia de Datos: Registros Imputados (Total: {total:,})",
            fontsize=14,
        )
        plt.xlabel("Cantidad de Registros")
        plt.xlim(
            right=total * 0.15 if max(data["Porcentaje"]) < 0.1 else None
        )  # Ajustar escala si son pocos
        plt.grid(axis="x", alpha=0.3)

        plt.tight_layout()
        output_path = self.figures_dir / "eda_missing_values.png"
        plt.savefig(output_path, dpi=150)
        plt.close()
        logger.info(f"Guardado en {output_path}")

    def plot_eda_projects_distribution(self):
        """Distribución de proyectos SEIA desde Excel."""
        self._set_technical_style()
        logger.info("Generando Plot EDA: Distribución de Proyectos...")

        excel_path = self.base_dir / "outputs" / "Proyectos.xlsx"
        if not excel_path.exists():
            logger.warning(
                f"No se encontró el archivo {excel_path}. Saltando visualización de proyectos."
            )
            return

        # Requiere openpyxl
        df = pd.read_excel(excel_path)

        plt.figure(figsize=(12, 7))
        # Contar proyectospor región
        sns.countplot(
            data=df,
            y="Región",
            order=df["Región"].value_counts().index,
            palette="Blues_r",
        )

        plt.title("Distribución de Proyectos Eléctricos (SEIA) por Región", fontsize=14)
        plt.xlabel("Cantidad de Proyectos")
        plt.ylabel("")
        plt.grid(axis="x", alpha=0.3)

        plt.tight_layout()
        output_path = self.figures_dir / "eda_projects_dist.png"
        plt.savefig(output_path, dpi=150)
        plt.close()
        logger.info(f"Guardado en {output_path}")

    def generate_all(self):
        """Genera TODAS las figuras (Paper + Técnicas)."""
        logger.info("🚀 Iniciando generación masiva de figuras...")
        try:
            # Paper Figures
            self.plot_fig1_global_timeseries()
            self.plot_fig2_heatmap()
            self.plot_fig3_coquimbo_paradox()
            self.plot_fig4_arica_redenor()
            self.plot_fig5_company_ranking()

            # Technical Figures
            self.plot_technical_volume()
            self.plot_technical_coverage()

            logger.info("✅ PROCESO COMPLETADO: Todas las figuras generadas.")
        except Exception as e:
            logger.error(f"❌ Error crítico generando figuras: {e}")
            raise


if __name__ == "__main__":
    # Uso directo si se ejecuta este script
    plotter = Plot()
    plotter.generate_all()

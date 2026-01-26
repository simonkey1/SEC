import polars as pl
import os
from dotenv import load_dotenv
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime


class SecDataExplorer:
    """Explorador de datos de la SEC usando Polars."""

    def __init__(self):
        load_dotenv()
        db_user = os.getenv("DB_USER", "postgres")
        db_pass = os.getenv("DB_PASSWORD", "acidosa123")
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = os.getenv("DB_PORT", "5432")
        db_name = os.getenv("DB_NAME", "sec_interrupciones")

        # URI de conexión para connectorx (muy rápido)
        self.uri = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

    def load_data(self):
        """Carga los datos de la fact table y dimensiones unidas."""
        print("🚀 Cargando datos desde PostgreSQL a Polars...")
        query = """
            SELECT 
                f.hash_id,
                f.clientes_afectados,
                t.fecha,
                t.año,
                t.mes,
                g.nombre_region,
                g.nombre_comuna,
                e.nombre_empresa
            FROM fact_interrupciones f
            JOIN dim_tiempo t ON f.id_tiempo = t.id_tiempo
            JOIN dim_geografia g ON f.id_geografia = g.id_geografia
            JOIN dim_empresa e ON f.id_empresa = e.id_empresa
        """
        self.df = pl.read_database_uri(query, self.uri, engine="adbc")
        print(f"✅ Cargados {len(self.df):,} registros.")
        return self.df

    def analyze_yearly_trends(self):
        """Analiza la tendencia anual de clientes afectados."""
        trend = (
            self.df.group_by("año")
            .agg(
                pl.col("clientes_afectados").sum().alias("total_afectados"),
                pl.col("hash_id").count().alias("num_interrupciones"),
            )
            .sort("año")
        )

        print("\n📈 Tendencia Anual:")
        print(trend)

        fig = px.line(
            trend.to_pandas(),
            x="año",
            y="total_afectados",
            title="Evolución Anual de Clientes Afectados (SEC Chile)",
            labels={"total_afectados": "Total Clientes", "año": "Año"},
            template="plotly_dark",
            markers=True,
        )
        fig.show()
        return trend

    def analyze_regional_impact(self):
        """Ranking de regiones con más impacto (Raw)."""
        regions = (
            self.df.group_by("nombre_region")
            .agg(pl.col("clientes_afectados").sum().alias("total_afectados"))
            .sort("total_afectados", descending=True)
        )

        print("\n🗺️ Impacto por Región (Top 5 - Raw):")
        print(regions.head(5))

        fig = px.bar(
            regions.to_pandas(),
            x="nombre_region",
            y="total_afectados",
            title="Impacto Acumulado por Región (Raw Sum)",
            template="plotly_dark",
            color="total_afectados",
        )
        fig.show()
        return regions

    def analyze_normalized_impact(self):
        """Impacto ponderado por cantidad de clientes por región.
        Estimación aproximada de clientes eléctricos por región (CNE/SEC).
        """
        # Ponderación: Clientes aproximados por región (en miles)
        ponderacion = {
            "METROPOLITANA": 2500,
            "VALPARAISO": 880,
            "BIOBIO": 720,
            "MAULE": 440,
            "LA ARAUCANIA": 430,
            "O'HIGGINS": 400,
            "LOS LAGOS": 350,
            "COQUIMBO": 340,
            "ANTOFAGASTA": 220,
            "NUBLE": 210,
            "LOS RIOS": 170,
            "TARAPACA": 150,
            "ATACAMA": 110,
            "ARICA Y PARINACOTA": 100,
            "MAGALLANES": 80,
            "AYSEN": 40,
        }

        # Convertir a DataFrame de Polars para unir
        df_pob = pl.DataFrame(
            {
                "nombre_region": list(ponderacion.keys()),
                "clientes_reg_k": list(ponderacion.values()),
            }
        )

        # Unir y calcular métrica normalizada
        df_norm = (
            self.df.group_by("nombre_region")
            .agg(
                pl.col("clientes_afectados").sum().alias("total_afectados"),
                pl.col("hash_id").count().alias("n_interrupciones"),
            )
            .join(df_pob, on="nombre_region")
        )

        # Calcular "Eventos por cada 1,000 clientes"
        df_norm = df_norm.with_columns(
            [
                (pl.col("total_afectados") / (pl.col("clientes_reg_k"))).alias(
                    "impacto_per_1k_clientes"
                )
            ]
        ).sort("impacto_per_1k_clientes", descending=True)

        print("\n⚖️ Impacto Ponderado (Normalizado por 1,000 clientes):")
        print(
            df_norm.select(
                ["nombre_region", "impacto_per_1k_clientes", "total_afectados"]
            ).head(10)
        )

        fig = px.bar(
            df_norm.to_pandas(),
            x="nombre_region",
            y="impacto_per_1k_clientes",
            title="Índice de Vulnerabilidad: Afectados por cada 1,000 Clientes",
            labels={"impacto_per_1k_clientes": "Afectados / 1k Clientes"},
            template="plotly_dark",
            color="impacto_per_1k_clientes",
            color_continuous_scale="Reds",
        )
        fig.show()
        return df_norm


if __name__ == "__main__":
    explorer = SecDataExplorer()
    df = explorer.load_data()
    explorer.analyze_yearly_trends()
    explorer.analyze_regional_impact()
    explorer.analyze_normalized_impact()

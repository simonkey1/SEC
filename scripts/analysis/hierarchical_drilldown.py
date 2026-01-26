import sys

sys.path.append(".")

import polars as pl
import os
from dotenv import load_dotenv
import plotly.express as px


class SecHierarchicalExplorer:
    """Explorador jerárquico (Region -> Comuna) con soporte de drill-down."""

    def __init__(self):
        load_dotenv()
        db_user = os.getenv("DB_USER", "postgres")
        db_pass = os.getenv("DB_PASSWORD", "acidosa123")
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = os.getenv("DB_PORT", "5432")
        db_name = os.getenv("DB_NAME", "sec_interrupciones")
        self.uri = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

    def get_macro_zona(self, region):
        norte = ["ARICA Y PARINACOTA", "TARAPACA", "ANTOFAGASTA", "ATACAMA", "COQUIMBO"]
        centro = ["VALPARAISO", "METROPOLITANA", "O'HIGGINS", "MAULE", "NUBLE"]
        sur = ["BIOBIO", "LA ARAUCANIA", "LOS RIOS", "LOS LAGOS", "AYSEN", "MAGALLANES"]

        if region in norte:
            return "NORTE"
        if region in centro:
            return "CENTRO"
        if region in sur:
            return "SUR"
        return "OTRO"

    def get_province(self, region, comuna):
        # Mapeo simplificado de Proviencias basado en la estructura de Chile
        # Este es un mapeo de ejemplo, en producción se usaría una tabla de referencia completa
        rm_provincias = {
            "SANTIAGO": [
                "SANTIAGO",
                "PROVIDENCIA",
                "LAS CONDES",
                "VITACURA",
                "LO BARNECHEA",
                "NUNOA",
                "LA REINA",
                "MACAUL",
                "PENALOLEN",
                "LA FLORIDA",
                "PUENTE ALTO",
                "SAN BERNARDO",
                "MAIPU",
                "PUDAHUEL",
                "QUILICURA",
                "COLINA",
                "LAMPA",
                "TILTIL",
            ],
            "CORDILLERA": ["PUENTE ALTO", "SAN JOSE DE MAIPO", "PIRQUE"],
            "MAIPO": ["SAN BERNARDO", "BUIN", "PAINE", "CALERA DE TANGO"],
            "TALAGANTE": [
                "TALAGANTE",
                "PENAFLOR",
                "PADRE HURTADO",
                "EL MONTE",
                "ISLA DE MAIPO",
            ],
            "MELIPILLA": ["MELIPILLA", "CURACAVI", "MARIA PINTO", "SAN PEDRO", "ALHUE"],
            "CHACABUCO": ["COLINA", "LAMPA", "TILTIL"],
        }

        if region == "METROPOLITANA":
            for prov, comunas in rm_provincias.items():
                if comuna in comunas:
                    return f"PROV. {prov}"
            return "PROV. SANTIAGO"

        # Para otras regiones, agrupamos por nombre de región para el Market Map conceptual
        return f"PROV. {region}"

    def load_hierarchy(self):
        parquet_path = "outputs/golden_interrupciones.parquet"

        if os.path.exists(parquet_path):
            print(f"🚀 Cargando Golden Record desde {parquet_path}...")
            df = pl.read_parquet(parquet_path)
        else:
            print("⚠️ Parquet no encontrado. Cargando desde DB (Datos crudos)...")
            query = """
                SELECT 
                    g.nombre_region,
                    g.nombre_comuna,
                    f.clientes_afectados
                FROM fact_interrupciones f
                JOIN dim_geografia g ON f.id_geografia = g.id_geografia
            """
            df = pl.read_database_uri(query, self.uri, engine="adbc")

        # Ponderación Regional (Miles de clientes)
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
        df_pob = pl.DataFrame(
            {
                "nombre_region": list(ponderacion.keys()),
                "clientes_reg_k": list(ponderacion.values()),
            }
        )

        # Jerarquía profunda
        df = df.with_columns(
            [
                pl.col("nombre_region")
                .map_elements(self.get_macro_zona, return_dtype=pl.String)
                .alias("macro_zona"),
                pl.struct(["nombre_region", "nombre_comuna"])
                .map_elements(
                    lambda x: self.get_province(x["nombre_region"], x["nombre_comuna"]),
                    return_dtype=pl.String,
                )
                .alias("provincia"),
            ]
        ).join(df_pob, on="nombre_region")

        # Agrupar hasta nivel Comuna
        df_agg = df.group_by(
            [
                "macro_zona",
                "nombre_region",
                "provincia",
                "nombre_comuna",
                "clientes_reg_k",
            ]
        ).agg(pl.col("clientes_afectados").sum().alias("total_afectados"))

        # Métrica: Cortes promedio por cliente al año
        # (Total Afectados / Población Regional) / 8 años
        df_agg = df_agg.with_columns(
            (
                (pl.col("total_afectados") / (pl.col("clientes_reg_k") * 1000)) / 8.0
            ).alias("cortes_anuales")
        )

        # Normalización: 100 = El máximo nivel de cortes por cliente histórico (Aprox 2.0)
        # Usamos un techo fijo para que el color sea comparable entre ejecuciones
        MAX_DISTORSION = (
            2.0  # Si alguien tiene más de 2 cortes/año promedio, es crítico 100
        )
        df_agg = df_agg.with_columns(
            (pl.col("cortes_anuales") / MAX_DISTORSION * 100)
            .clip(0, 100)
            .alias("vulnerabilidad_index")
        ).sort("vulnerabilidad_index", descending=True)

        return df_agg

    def plot_market_map(self, df):
        print("📊 Generando Market Map (Área=Magnitud, Color=Inestabilidad)...")
        pdf = df.to_pandas()

        # MARKET MAP REAL:
        # Area (values) = Magnitude (Cuánta gente sufre)
        # Color = Quality (Qué tan inestable es el servicio local)
        fig = px.treemap(
            pdf,
            path=["macro_zona", "nombre_region", "provincia", "nombre_comuna"],
            values="total_afectados",
            title="Market Map: Magnitud de Afectación (Tamaño) vs Inestabilidad de Red (Color)",
            template="plotly_dark",
            color="vulnerabilidad_index",
            color_continuous_scale="RdYlGn_r",
            range_color=[0, 100],  # Escala fija para comparabilidad
            labels={
                "vulnerabilidad_index": "Nivel de Inestabilidad (%)",
                "total_afectados": "Total Afectados Históricos",
            },
        )

        fig.update_traces(
            textinfo="label+value",
            texttemplate="<span style='font-size:22px'><b>%{label}</b></span><br><span style='font-size:16px'>Riesgo: %{color:.1f}/100</span>",
            hovertemplate="<b>%{label}</b><br>Índice Riesgo: %{color:.1f}/100<br>Histórico Afectados: %{value:,.0f}<br>Incidencia: %{customdata[0]:.2f} cortes/cliente año",
            customdata=pdf[["cortes_anuales"]],
            marker=dict(line=dict(width=2, color="rgba(255,255,255,0.2)")),
        )

        fig.update_layout(
            margin=dict(t=80, l=10, r=10, b=10),
            font=dict(size=18, family="Inter, sans-serif", color="white"),
            title_font_size=24,
            coloraxis_colorbar=dict(
                title="Estado Servicio",
                title_font_size=16,
                tickfont_size=14,
                tickvals=[0, 25, 50, 75, 100],
                ticktext=["Óptimo", "Estable", "Bajo Estrés", "Alerta", "Crítico"],
            ),
        )

        fig.show()
        print("✅ Market Map actualizado con Índice de Inestabilidad (0-100).")


if __name__ == "__main__":
    explorer = SecHierarchicalExplorer()
    df_market = explorer.load_hierarchy()
    explorer.plot_market_map(df_market)

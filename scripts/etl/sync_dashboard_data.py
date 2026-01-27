import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import polars as pl
import json
import os
from datetime import datetime
from core.supabase_client import get_supabase_client
from scripts.analysis.analyze_seia import SeiaAnalyzer


class DashboardSyncer:
    def __init__(self):
        self.parquet_path = "outputs/golden_interrupciones.parquet"
        self.supabase = get_supabase_client()
        self.table_name = "dashboard_stats"

    def load_golden_data(self):
        print("🚀 Cargando Golden Data...")
        return pl.read_parquet(self.parquet_path)

    def generate_market_map_json(self, df):
        print("🗺️ Generando JSON Market Map...")
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
        df_agg = (
            df.with_columns(pl.col("fecha_dt").dt.year().alias("año"))
            .group_by(["nombre_region", "nombre_comuna", "nombre_empresa"])
            .agg(
                pl.col("clientes_afectados").sum().alias("total_afectados"),
                pl.len().alias("frecuencia"),
            )
        )
        records = df_agg.to_dicts()
        for r in records:
            reg = r["nombre_region"]
            pob = ponderacion.get(reg, 50) * 1000
            r["instability_index"] = min(100, (r["total_afectados"] / pob) * 100)
        return records

    def generate_time_series_json(self, df):
        print("📈 Generando JSON Series de Tiempo...")
        df_ts = (
            df.with_columns(pl.col("fecha_dt").dt.truncate("1mo").alias("mes"))
            .group_by(["mes", "nombre_region"])
            .agg(pl.col("clientes_afectados").sum().alias("afectados"))
            .sort("mes")
        )
        return df_ts.with_columns(pl.col("mes").dt.strftime("%Y-%m-%d")).to_dicts()

    def generate_investment_roi_ranking(self, df_sec):
        print("💰 Generando ROI de Inversión...")
        seia = SeiaAnalyzer()
        seia.load_and_clean()
        df_inv = seia.aggregate_by_region_year()
        df_sec_total = df_sec.group_by("nombre_region").agg(
            pl.col("clientes_afectados").sum()
        )
        df_inv_total = df_inv.group_by("nombre_region").agg(
            pl.col("total_inversión_mmu").sum()
        )
        df_roi = df_sec_total.join(df_inv_total, on="nombre_region", how="inner")
        df_roi = df_roi.with_columns(
            (pl.col("clientes_afectados") / pl.col("total_inversión_mmu")).alias(
                "efficiency_ratio"
            )
        ).sort("efficiency_ratio", descending=True)
        records = df_roi.to_dicts()
        for r in records:
            if r["nombre_region"] == "NUBLE":
                r["maturity_note"] = "⚠️ Proyectos en construcción (Entrega 2027)"
            elif r["nombre_region"] == "MAULE":
                r["maturity_note"] = "⚠️ Zonas de rezago histórico"
            else:
                r["maturity_note"] = "Operativo"
        return records

    def generate_company_ranking(self, df):
        print("📊 Generando Ranking de Empresas...")
        df_ranking = (
            df.group_by("nombre_empresa")
            .agg(
                pl.len().alias("total_eventos"),
                pl.col("clientes_afectados").sum().alias("total_clientes_afectados"),
                pl.col("clientes_afectados").mean().alias("promedio_afectados"),
            )
            .sort("total_clientes_afectados", descending=True)
            .head(15)
        )
        return df_ranking.to_dicts()

    def generate_investment_validation(self):
        print("⚖️ Generando Validación de Inversiones...")
        return [
            {
                "project": "REDENOR (Arica/Tarapacá)",
                "year": 2023,
                "type": "Inmediato",
                "delta": -70.0,
                "context": "Éxito rotundo. Solución quirúrgica en zona desértica.",
            },
            {
                "project": "Pichirropulli (Valdivia)",
                "year": 2021,
                "type": "Inmediato",
                "delta": -17.6,
                "context": "Estabilizó la zona ante temporales, aunque no es inmune.",
            },
            {
                "project": "Lo Aguirre - C. Navia (RM)",
                "year": 2019,
                "type": "Inmediato",
                "delta": -14.4,
                "context": "Mejora moderada pero crucial para la densidad de Santiago.",
            },
            {
                "project": "Cardones-Polpaico (Norte Chico)",
                "year": 2019,
                "type": "Lag (3 Años)",
                "delta": -5.7,
            },
        ]

    def generate_eda_quality_metrics(self, df):
        print("🕵️ Generando Métricas de Calidad de Datos (EDA)...")
        total = len(df)

        # Conteo de imputaciones (Simulado/Real basado en datos parquet)
        # Nota: En parquet 'nombre_region' ya viene resuelto, si era desconocido puede ser null o "DESCONOCIDO"
        # Ajustar según lógica de transformación real.

        afectados_zero = df.filter(pl.col("clientes_afectados") == 0).height
        geo_unknown = df.filter(pl.col("nombre_region") == "DESCONOCIDO").height
        empresa_unknown = df.filter(pl.col("nombre_empresa") == "DESCONOCIDO").height

        return [
            {
                "category": "Afectados = 0 (Imputado)",
                "count": afectados_zero,
                "percentage": float(afectados_zero / total) if total > 0 else 0,
            },
            {
                "category": "Geografía Desconocida",
                "count": geo_unknown,
                "percentage": float(geo_unknown / total) if total > 0 else 0,
            },
            {
                "category": "Empresa Desconocida",
                "count": empresa_unknown,
                "percentage": float(empresa_unknown / total) if total > 0 else 0,
            },
        ]

    def generate_eda_project_dist(self):
        print("🏗️ Generando Distribución de Proyectos SEIA (EDA)...")
        seia = SeiaAnalyzer()
        try:
            df_seia = seia.load_and_clean()
            # Agrupar solo por región para el gráfico de barras
            dist = (
                df_seia.group_by("nombre_region")
                .agg(pl.len().alias("count"))
                .sort("count", descending=True)
            )
            return dist.to_dicts()
        except Exception as e:
            print(f"⚠️ Error procesando SEIA para EDA: {e}")
            return []

    def sync_to_supabase(self):
        df = self.load_golden_data()
        payloads = {
            "market_map": self.generate_market_map_json(df),
            "time_series": self.generate_time_series_json(df),
            "investment_roi": self.generate_investment_roi_ranking(df),
            "company_ranking": self.generate_company_ranking(df),
            "investment_validation": self.generate_investment_validation(),
            # Nuevos datasets para Documento Técnico
            "eda_quality_stats": self.generate_eda_quality_metrics(df),
            "eda_projects_dist": self.generate_eda_project_dist(),
        }
        print("☁️ Subiendo a Supabase...")
        for key, data in payloads.items():
            try:
                self.supabase.table(self.table_name).upsert(
                    {"id": key, "data": data, "updated_at": datetime.now().isoformat()}
                ).execute()
                print(f"✅ {key} sincronizado ({len(data)} items en payload)")
            except Exception as e:
                print(f"❌ Error subiendo {key}: {e}")


if __name__ == "__main__":
    syncer = DashboardSyncer()
    syncer.sync_to_supabase()

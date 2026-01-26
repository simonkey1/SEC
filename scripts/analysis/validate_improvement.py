import sys

sys.path.append(".")

import polars as pl
from datetime import date


class ImpactValidator:
    def __init__(self):
        self.parquet_path = "outputs/golden_interrupciones.parquet"

    def validate(self):
        print("🚀 Validando Impacto 'Cardones-Polpaico' (Inaugurado Junio 2019)...")
        df = pl.read_parquet(self.parquet_path)

        # Regiones beneficiadas: ATACAMA, COQUIMBO
        target_regions = ["ATACAMA", "COQUIMBO"]

        # Periodos
        # Pre: 2017-01-01 al 2018-12-31
        # Post: 2020-01-01 al 2021-12-31 (Damos 6 meses de margen tras inauguracion)

        for region in target_regions:
            df_reg = df.filter(pl.col("nombre_region") == region)

            # Pre
            pre_stats = df_reg.filter(
                (pl.col("fecha_dt").dt.year().is_in([2017, 2018]))
            )
            pre_affected = pre_stats["clientes_afectados"].sum()
            pre_events = len(pre_stats)

            # Post
            post_stats = df_reg.filter(
                (pl.col("fecha_dt").dt.year().is_in([2020, 2021]))
            )
            post_affected = post_stats["clientes_afectados"].sum()
            post_events = len(post_stats)

            # Cálculo de Cambio
            delta_affected = ((post_affected - pre_affected) / pre_affected) * 100

            # Contexto Estadístico: ¿Es ruido?
            # Calculamos la desviación estándar de los años PRE para ver la volatilidad natural
            years_pre = df_reg.filter(pl.col("fecha_dt").dt.year().is_in([2017, 2018]))
            annual_std = (
                years_pre.group_by(pl.col("fecha_dt").dt.year())
                .agg(pl.col("clientes_afectados").sum())
                .select(pl.col("clientes_afectados").std())
                .item()
            )

            diff_abs = post_affected - pre_affected

            print(f"\n🌍 Región: {region}")
            print(f"   📅 PRE (2017-18): {pre_affected:,.0f} afectados")
            print(f"   📅 POST (2020-21): {post_affected:,.0f} afectados")
            print(
                f"   📉 Variación: {delta_affected:+.1f}% (+{diff_abs:,.0f} clientes)"
            )

            # Criterio de Sigificancia (muy simplificado: cambio > 1.5 sigma?)
            sig_threshold = annual_std * 1.5 if annual_std else 0

            if abs(diff_abs) < sig_threshold:
                print(
                    f"   ⚠️ Cambio MARGINAL (Ruido). Dentro del rango de volatilidad ({sig_threshold:,.0f})."
                )
            elif diff_abs > 0:
                print(
                    f"   ❌ Aumento REAL (Corto Plazo). Supera la volatilidad natural."
                )
            else:
                print(
                    f"   ✅ Mejora REAL (Corto Plazo). Supera la volatilidad natural."
                )

            # --- CHECK A LARGO PLAZO (2022-2024) ---
            # ¿Quizás la mejora tardó en llegar?
            long_term_stats = df_reg.filter(
                (pl.col("fecha_dt").dt.year().is_in([2022, 2023, 2024]))
            )
            long_term_affected = long_term_stats["clientes_afectados"].sum()
            # Ajustamos promedio anual para comparar peras con peras (2 años vs 3 años)
            avg_pre = pre_affected / 2
            avg_long = long_term_affected / 3

            delta_long = ((avg_long - avg_pre) / avg_pre) * 100

            print(
                f"   📅 LARGO PLAZO (2022-24): Promedio {avg_long:,.0f}/año vs Pre {avg_pre:,.0f}/año"
            )
            print(f"   📉 Variación LP: {delta_long:+.1f}%")

            if delta_long < -5:
                print("   ✅ HUBO MEJORA TARDÍA. La red se estabilizó después.")
            elif delta_long > 5:
                print("   ❌ TENDENCIA AL ALZA. El problema es crónico.")
            else:
                print("   ⚠️ ESTANCADO. La inversión no cambió nada a largo plazo.")

    def validate_redenor(self):
        print("\n🚀 Validando Impacto 'REDENOR' (Arica/Tarapacá - 2023)...")
        df = pl.read_parquet(self.parquet_path)

        target_regions = ["ARICA Y PARINACOTA", "TARAPACA"]

        for region in target_regions:
            df_reg = df.filter(pl.col("nombre_region") == region)

            # Pre: 2021-2022
            pre_stats = df_reg.filter(pl.col("fecha_dt").dt.year().is_in([2021, 2022]))
            pre_avg = pre_stats["clientes_afectados"].sum() / 2

            # Post: 2024 (Año completo post-inauguración)
            post_stats = df_reg.filter(pl.col("fecha_dt").dt.year() == 2024)
            post_total = post_stats["clientes_afectados"].sum()

            delta = ((post_total - pre_avg) / pre_avg) * 100

            print(f"\n🌍 Región: {region}")
            print(f"   📅 PRE (2021-22): {pre_avg:,.0f} afectados/año")
            print(f"   📅 POST (2024): {post_total:,.0f} afectados")
            print(f"   📉 Variación: {delta:+.1f}%")

            if delta < -5:
                print("   ✅ MEJORA INMEDIATA. REDENOR funcionó rápido.")
            elif delta > 5:
                print("   ❌ SIN EFECTO AUN. Sigue aumentando.")
            else:
                print("   ⚠️ SIN CAMBIO.")

    def validate_south(self):
        print("\n🚀 Validando Impacto 'Pichirropulli-Tineo' (Sur - 2021)...")
        df = pl.read_parquet(self.parquet_path)

        target_regions = ["LOS RIOS", "LOS LAGOS"]

        for region in target_regions:
            df_reg = df.filter(pl.col("nombre_region") == region)

            # Pre: 2019-2020 (Justo antes de la operación plena)
            pre_stats = df_reg.filter(pl.col("fecha_dt").dt.year().is_in([2019, 2020]))
            pre_avg = pre_stats["clientes_afectados"].sum() / 2

            # Post: 2022-2023 (Operación plena)
            post_stats = df_reg.filter(pl.col("fecha_dt").dt.year().is_in([2022, 2023]))
            post_avg = post_stats["clientes_afectados"].sum() / 2

            delta = ((post_avg - pre_avg) / pre_avg) * 100

            print(f"\n🌍 Región: {region}")
            print(f"   📅 PRE (2019-20): {pre_avg:,.0f} afectados/año")
            print(f"   📅 POST (2022-23): {post_avg:,.0f} afectados/año")
            print(f"   📉 Variación: {delta:+.1f}%")

            if delta < -5:
                print("   ✅ EXITO SUR. La línea estabilizó la zona.")
            elif delta > 5:
                print("   ❌ FRACASO SUR. Los cortes aumentaron pese a la línea.")
            else:
                print("   ⚠️ SIN CAMBIO.")

    def validate_santiago(self):
        print("\n🚀 Validando Impacto 'Lo Aguirre - Cerro Navia' (RM - 2019)...")
        df = pl.read_parquet(self.parquet_path)

        region = "METROPOLITANA"
        df_reg = df.filter(pl.col("nombre_region") == region)

        # Pre: 2017-2018
        pre_stats = df_reg.filter(pl.col("fecha_dt").dt.year().is_in([2017, 2018]))
        pre_avg = pre_stats["clientes_afectados"].sum() / 2

        # Post: 2020-2021 (Impacto post-inauguración Julio 2019)
        post_stats = df_reg.filter(pl.col("fecha_dt").dt.year().is_in([2020, 2021]))
        post_avg = post_stats["clientes_afectados"].sum() / 2

        delta = ((post_avg - pre_avg) / pre_avg) * 100

        print(f"\n🌍 Región: {region}")
        print(f"   📅 PRE (2017-18): {pre_avg:,.0f} afectados/año")
        print(f"   📅 POST (2020-21): {post_avg:,.0f} afectados/año")
        print(f"   📉 Variación: {delta:+.1f}%")

        if delta < 0:
            print("   ✅ ÉXITO RM. La línea mejoró Santiago.")
        else:
            print("   ❌ SIN EFECTO RM. La inversión se diluyó en la densidad.")


if __name__ == "__main__":
    validator = ImpactValidator()
    validator.validate()
    validator.validate_redenor()
    validator.validate_south()
    validator.validate_santiago()

import os
from dotenv import load_dotenv
import polars as pl
import hashlib


class ComprehensiveCleaner:
    def __init__(self):
        load_dotenv()
        user = os.getenv("DB_USER", "postgres")
        password = os.getenv("DB_PASSWORD", "")
        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "5432")
        dbname = os.getenv("DB_NAME", "sec_interrupciones")

        self.uri = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"

    def generate_hash_expr(self):
        # Lógica Polars para replicar el Hash MD5: Comuna + Empresa + Fecha + Hora + Afectados
        # Nota: En Polars concatenamos strings y hasheamos
        return (
            pl.col("nombre_comuna")
            + "_"
            + pl.col("nombre_empresa")
            + "_"
            + pl.col("fecha_dt").dt.strftime("%Y%m%d")
            + "_"
            + pl.col("hora_int").dt.strftime("%H%M")
            + "_"
            + pl.col("clientes_afectados").cast(pl.Utf8)
        )

    def load_and_clean(self):
        print("🚀 Carga masiva desde PostgreSQL...")

        # 1. Cargar JOIN completo
        query = """
            SELECT 
                f.id_interrupcion,
                f.hash_id as original_hash,
                f.clientes_afectados,
                f.hora_interrupcion as hora_int,
                t.fecha as fecha_dt,
                g.nombre_region,
                g.nombre_comuna,
                e.nombre_empresa
            FROM fact_interrupciones f
            JOIN dim_tiempo t ON f.id_tiempo = t.id_tiempo
            JOIN dim_geografia g ON f.id_geografia = g.id_geografia
            JOIN dim_empresa e ON f.id_empresa = e.id_empresa
        """
        df = pl.read_database_uri(query, self.uri, engine="adbc")
        print(f"📦 Registros brutos cargados: {len(df):,}")

        # 2. Generar 'Smart Hash' para deduplicación retroactiva
        print("🧹 Generando Hash de Contenido (Deduplicación)...")

        # Concatenar columnas clave
        # Es más eficiente en Polars crear una columna concatenada y luego usar 'unique'
        # Si queremos el hash MD5 exacto string-wise es costoso, para dedup basta con agrupar por las columnas clave

        cols_clave = [
            "nombre_comuna",
            "nombre_empresa",
            "fecha_dt",
            "hora_int",
            "clientes_afectados",
        ]

        df_clean = df.unique(subset=cols_clave, keep="first")

        duplicados = len(df) - len(df_clean)
        print(f"♻️  Duplicados eliminados (mismo evento y magnitud): {duplicados:,}")
        print(f"✨ Registros únicos (Golden Set): {len(df_clean):,}")

        # 3. Validación de Calidad
        print("\n🔍 Validaciones de Calidad:")

        # a) Nulos
        nulls = df_clean.null_count()
        total_nulls = nulls.sum_horizontal()[0]

        if total_nulls > 0:
            print("⚠️ ADVERTENCIA: Se detectaron nulos post-limpieza")
            print(nulls)
        else:
            print("✅ Integridad de columnas: OK (0 Nulls)")

        # b) Consistencia Geográfica (Población)
        # Cargamos diccionario de población para detectar outliers (afectados > población)
        # Usamos una referencia rápida hardcodeada o externa si existe.
        # Por ahora solo alertamos anomalías obvias (> 1 Millón de afectados en un evento puntual salvo RM)
        anomalias = df_clean.filter(pl.col("clientes_afectados") > 500000)
        if len(anomalias) > 0:
            print(
                f"⚠️ Anomalías de magnitud detectadas (>500k afectados): {len(anomalias)}"
            )
            print(anomalias.select(["fecha_dt", "nombre_region", "clientes_afectados"]))
        else:
            print("✅ Validacion de Magnitud: OK (Sin eventos inverosímiles > 500k)")

        # 4. Exportar Golden Record
        output_path = "outputs/golden_interrupciones.parquet"
        df_clean.write_parquet(output_path)
        print(f"\n💾 Dataset maestro guardado en: {output_path}")

        return df_clean


if __name__ == "__main__":
    cleaner = ComprehensiveCleaner()
    df = cleaner.load_and_clean()

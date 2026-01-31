"""Data persistence and path management module.

This module defines storage paths and provides functions
to save processed data in CSV formats (local).
"""

import logging
import os
from datetime import datetime

import pandas as pd
from dotenv import load_dotenv
from supabase import Client, create_client

logger = logging.getLogger(__name__)

# Global paths for file management


# In core/database.py


class SupabaseRepository:
    """Repository pattern for Supabase data persistence.

    Manages dimension tables (get_or_create) and fact table insertions.
    """

    def __init__(self):
        """Initialize Supabase client with credentials from .env"""
        load_dotenv()
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")

        if not url or not key:
            raise ValueError(
                f"Missing Supabase credentials. SUPABASE_URL={'set' if url else 'NOT SET'}, "
                f"SUPABASE_KEY={'set' if key else 'NOT SET'}"
            )

        self.supabase = create_client(url, key)

    def get_or_create_geografia(self, region: str, comuna: str) -> int:
        """Get or create geography dimension record."""

        result = (
            self.supabase.table("dim_geografia")
            .select("id_geografia")
            .eq("nombre_region", region)
            .eq("nombre_comuna", comuna)
            .execute()
        )

        if result.data and len(result.data) > 0:
            return result.data[0]["id_geografia"]

        new = (
            self.supabase.table("dim_geografia")
            .insert({"nombre_region": region, "nombre_comuna": comuna})
            .execute()
        )
        return new.data[0]["id_geografia"]

    def get_or_create_empresa(self, empresa: str) -> int:
        """Get or create company dimension record."""
        result = (
            self.supabase.table("dim_empresa")
            .select("id_empresa")
            .eq("nombre_empresa", empresa)
            .execute()
        )

        if result.data and len(result.data) > 0:
            return result.data[0]["id_empresa"]

        new = (
            self.supabase.table("dim_empresa")
            .insert({"nombre_empresa": empresa})
            .execute()
        )
        return new.data[0]["id_empresa"]

    def get_or_create_tiempo(self, timestamp_str: str) -> int:
        """Get or create time dimension record."""

        # 1. Parse timestamp
        dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")

        # 2. Generate time_id as integer (YYYYMMDDHHMM)
        id_tiempo = int(dt.strftime("%Y%m%d%H%M"))

        # 3. Search if exists
        result = (
            self.supabase.table("dim_tiempo")
            .select("id_tiempo")
            .eq("id_tiempo", id_tiempo)
            .execute()
        )

        if result.data and len(result.data) > 0:
            return id_tiempo  # ← Return the time_id, not .data[0]

        # 4. Insert new
        self.supabase.table("dim_tiempo").insert(
            {
                "id_tiempo": id_tiempo,
                "fecha": dt.date().isoformat(),  # "2026-01-23"
                "hora": dt.time().isoformat(),  # "14:30:00"
                "año": dt.year,
                "mes": dt.month,
                "dia": dt.day,
            }
        ).execute()

        return id_tiempo  # ← Return the time_id

    def save_records(self, records: list) -> dict:
        """Save processed records to fact table."""
        inserted = 0
        duplicates = 0
        errors = 0

        for record in records:
            try:
                # Get FKs using self
                id_geografia = self.get_or_create_geografia(
                    region=record["REGION"], comuna=record["COMUNA"]
                )
                id_empresa = self.get_or_create_empresa(empresa=record["EMPRESA"])
                id_tiempo = self.get_or_create_tiempo(timestamp_str=record["TIMESTAMP"])

                # Insert into fact table
                self.supabase.table("fact_interrupciones").insert(
                    {
                        "id_tiempo": id_tiempo,
                        "id_geografia": id_geografia,
                        "id_empresa": id_empresa,
                        "clientes_afectados": record["CLIENTES_AFECTADOS"],
                        "hash_id": record["ID_UNICO"],
                    }
                ).execute()

                inserted += 1

            except Exception as e:
                if "duplicate" in str(e).lower() or "unique" in str(e).lower():
                    duplicates += 1
                else:
                    errors += 1
                    logger.error(f"Error inserting: {e}")

        # Logging AFTER the loop
        logger.info(
            f"✅ Inserted: {inserted} | Duplicates: {duplicates} | Errors: {errors}"
        )

        return {"insertados": inserted, "duplicados": duplicates, "errores": errors}


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

# Ensure output directory exists

os.makedirs(OUTPUT_DIR, exist_ok=True)

csv_near_real_time = os.path.join(OUTPUT_DIR, "affected_customers_near_real_time.csv")
csv_historical = os.path.join(OUTPUT_DIR, "affected_customers_historical.csv")


def save_data_csv(records):
    """Saves processed records to local CSV files.

    Manages two files: one historical (incremental without duplicates) and
    one near-real-time (overwrites the current state).

    Args:
        records (list): List of dictionaries processed by the transformer.
    """
    if records:
        df_new = pd.DataFrame(records)

        # Save to historical
        if os.path.exists(csv_historical):
            df_hist = pd.read_csv(csv_historical, encoding="utf-8-sig")
            df_hist = pd.concat([df_hist, df_new], ignore_index=True)
            df_hist = df_hist.drop_duplicates(subset=["ID_UNICO", "TIMESTAMP"])
        else:
            df_hist = df_new
            print(
                f"✅ Data saved to:\n📌 {csv_historical} (Historical)\n📌 {csv_near_real_time} (Near-Real-Time)"
            )

        df_hist.to_csv(csv_historical, index=False, encoding="utf-8-sig")

        # Save to near-real-time (overwrite)
        df_new.to_csv(csv_near_real_time, index=False, encoding="utf-8-sig")

        print(
            f"✅ Data saved to:\n📌 {csv_historical} (Historical)\n📌 {csv_near_real_time} (Near-Real-Time)"
        )


def save_data_sql():
    pass


def check_database_capacity(threshold_percent=85):
    load_dotenv()

    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_KEY")

    supabase: Client = create_client(url, key)
    try:
        response = (
            supabase.table("fact_interrupciones").select("*", count="exact").execute()
        )
        total_filas = response.count

        size_mb = (total_filas * 200) / 1024 / 1024

        porcentaje = (size_mb / 500) * 100
        alert_sent = False
        if porcentaje >= threshold_percent:
            from core.notifications import EmailNotifier

            notifier = EmailNotifier()
            notifier.send_capacity_alert(
                porcentaje=porcentaje, size_mb=size_mb, total_filas=total_filas
            )
            logger.warning(f"⚠️ Base de datos al {porcentaje:.2f}% de capacidad")
            alert_sent = True

        # 5. Retornar estado
        return {
            "size_mb": round(size_mb, 2),
            "porcentaje": round(porcentaje, 2),
            "alert_sent": alert_sent,
            "total_filas": total_filas,  # Extra: útil para debugging
        }

    except Exception as e:
        logger.error(f"❌ Error verificando capacidad: {e}")
        return {"size_mb": 0, "porcentaje": 0, "alert_sent": False, "total_filas": 0}

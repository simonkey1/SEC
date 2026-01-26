"""PostgreSQL Repository with Star Schema support.

Handles connection and data persistence to local PostgreSQL instance
using star schema (fact table + dimension tables). Optimized for high performance.
"""

import logging
import os
from typing import List, Dict, Any, Optional
from datetime import date, datetime
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class PostgreSQLRepository:
    """Repository for PostgreSQL with star schema. Optimized version."""

    def __init__(self):
        """Initialize PostgreSQL connection from environment variables."""
        load_dotenv()

        self.conn_params = {
            "host": os.getenv("DB_HOST") or os.getenv("POSTGRES_HOST") or "localhost",
            "port": os.getenv("DB_PORT") or os.getenv("POSTGRES_PORT") or "5432",
            "database": os.getenv("DB_NAME")
            or os.getenv("POSTGRES_DB")
            or "sec_interrupciones",
            "user": os.getenv("DB_USER") or os.getenv("POSTGRES_USER") or "postgres",
            "password": os.getenv("DB_PASSWORD") or os.getenv("POSTGRES_PASSWORD"),
        }

        if not self.conn_params["password"]:
            raise ValueError("DB_PASSWORD or POSTGRES_PASSWORD not set in .env file")

        self.conn = None

        # In-memory caches for dimensions to avoid redundant DB queries
        self._geo_cache: Dict[str, int] = {}
        self._emp_cache: Dict[str, int] = {}

        self._connect()

    def _connect(self):
        """Establish database connection."""
        try:
            self.conn = psycopg2.connect(**self.conn_params)
            self.conn.autocommit = False  # Manual transaction control
            logger.info(f"✅ Connected to PostgreSQL: {self.conn_params['database']}")
        except Exception as e:
            logger.error(f"❌ Failed to connect to PostgreSQL: {e}")
            raise

    def get_or_create_geografia(self, region: str, comuna: str) -> int:
        """Get or create geografia dimension record (with caching)."""
        cache_key = f"{region}|{comuna}"
        if cache_key in self._geo_cache:
            return self._geo_cache[cache_key]

        with self.conn.cursor() as cur:
            # Try to get existing
            cur.execute(
                "SELECT id_geografia FROM dim_geografia WHERE nombre_region = %s AND nombre_comuna = %s",
                (region, comuna),
            )
            result = cur.fetchone()
            if result:
                id_geo = result[0]
            else:
                # Create new
                cur.execute(
                    """
                    INSERT INTO dim_geografia (nombre_region, nombre_comuna)
                    VALUES (%s, %s)
                    ON CONFLICT (nombre_region, nombre_comuna) DO UPDATE
                    SET nombre_region = EXCLUDED.nombre_region
                    RETURNING id_geografia
                    """,
                    (region, comuna),
                )
                id_geo = cur.fetchone()[0]
                self.conn.commit()

            self._geo_cache[cache_key] = id_geo
            return id_geo

    def get_or_create_empresa(self, nombre_empresa: str) -> int:
        """Get or create empresa dimension record (with caching)."""
        if nombre_empresa in self._emp_cache:
            return self._emp_cache[nombre_empresa]

        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT id_empresa FROM dim_empresa WHERE nombre_empresa = %s",
                (nombre_empresa,),
            )
            result = cur.fetchone()
            if result:
                id_emp = result[0]
            else:
                cur.execute(
                    """
                    INSERT INTO dim_empresa (nombre_empresa)
                    VALUES (%s)
                    ON CONFLICT (nombre_empresa) DO UPDATE
                    SET nombre_empresa = EXCLUDED.nombre_empresa
                    RETURNING id_empresa
                    """,
                    (nombre_empresa,),
                )
                id_emp = cur.fetchone()[0]
                self.conn.commit()

            self._emp_cache[nombre_empresa] = id_emp
            return id_emp

    def get_id_tiempo(self, fecha: date) -> Optional[int]:
        """Get tiempo dimension ID from pre-populated table."""
        # Note: We don't cache this as it's a simple PK lookup, but we could
        with self.conn.cursor() as cur:
            cur.execute("SELECT id_tiempo FROM dim_tiempo WHERE fecha = %s", (fecha,))
            result = cur.fetchone()
            return result[0] if result else None

    def save_records(self, records: List[Dict[str, Any]]) -> Dict[str, int]:
        """Save records to PostgreSQL using massive batch inserts.

        Args:
            records: List of dictionaries with transformed interruption data

        Returns:
            Dict with counts of processed records
        """
        if not records:
            return {"insertados": 0, "duplicados": 0}

        try:
            batch_data = []
            for record in records:
                # Dim IDs (efficiently cached)
                id_geografia = self.get_or_create_geografia(
                    record.get("REGION") or "DESCONOCIDO",
                    record.get("COMUNA") or "DESCONOCIDO",
                )
                id_empresa = self.get_or_create_empresa(
                    record.get("EMPRESA") or "DESCONOCIDO"
                )
                id_tiempo = self.get_id_tiempo(record.get("FECHA_DT") or date.today())

                batch_data.append(
                    (
                        record.get("ID_UNICO"),
                        id_geografia,
                        id_empresa,
                        id_tiempo,
                        record.get("CLIENTES_AFECTADOS", 0),
                        record.get("HORA_INT"),
                        record.get("TIMESTAMP_SERVER"),
                        record.get("FECHA_STR"),
                        record.get("ACTUALIZADO_HACE"),
                    )
                )

            # Massive Insert
            query = """
                INSERT INTO fact_interrupciones (
                    hash_id, id_geografia, id_empresa, id_tiempo,
                    clientes_afectados, hora_interrupcion,
                    hora_server_scraping, fecha_int_str, actualizado_hace
                ) VALUES %s
                ON CONFLICT (hash_id) DO NOTHING;
            """

            with self.conn.cursor() as cur:
                execute_values(cur, query, batch_data)
                self.conn.commit()

            return {"insertados": len(batch_data), "duplicados": 0}

        except Exception as e:
            if self.conn:
                self.conn.rollback()
            logger.error(f"❌ Error in batch saving: {e}")
            raise

    def get_record_count(self) -> int:
        """Get total number of records in fact table."""
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM fact_interrupciones")
                return cur.fetchone()[0]
        except Exception:
            return 0

    def get_database_size(self) -> Dict[str, Any]:
        """Get database size information."""
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT pg_size_pretty(pg_database_size(current_database())) as size,
                           pg_database_size(current_database()) as size_bytes
                """)
                result = cur.fetchone()
                return {
                    "size_pretty": result[0],
                    "size_bytes": result[1],
                    "size_mb": result[1] / (1024 * 1024),
                }
        except Exception:
            return {"size_pretty": "Unknown", "size_bytes": 0, "size_mb": 0}

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
            logger.info("🔌 PostgreSQL connection closed")

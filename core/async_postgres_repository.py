"""Async PostgreSQL Repository.

High-performance asynchronous implementation using asyncpg.
"""

import logging
import os
import asyncio
from typing import List, Dict, Any, Optional
from datetime import date
import asyncpg
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class AsyncPostgreSQLRepository:
    """Async Repository for PostgreSQL with star schema."""

    def __init__(self):
        """Initialize."""
        load_dotenv()
        self.dsn = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
        self.pool = None

        # In-memory caches
        self._geo_cache: Dict[str, int] = {}
        self._emp_cache: Dict[str, int] = {}

        # Lock for cache population to prevent race conditions
        self._geo_lock = asyncio.Lock()
        self._emp_lock = asyncio.Lock()

    async def connect(self):
        """Establish connection pool."""
        if not self.pool:
            try:
                self.pool = await asyncpg.create_pool(
                    self.dsn,
                    min_size=10,
                    max_size=50,  # Allow high concurrency
                    command_timeout=60,
                )
                logger.info("✅ Async PostgreSQL Pool created")
            except Exception as e:
                logger.error(f"❌ Failed to create async pool: {e}")
                raise

    async def close(self):
        """Close connection pool."""
        if self.pool:
            await self.pool.close()
            logger.info("🔌 Async PostgreSQL Pool closed")

    async def get_or_create_geografia(self, region: str, comuna: str) -> int:
        """Get or create geografia dimension with caching."""
        key = f"{region}|{comuna}"
        if key in self._geo_cache:
            return self._geo_cache[key]

        async with self._geo_lock:
            # Double-check locking
            if key in self._geo_cache:
                return self._geo_cache[key]

            async with self.pool.acquire() as conn:
                # Try to find
                row = await conn.fetchrow(
                    "SELECT id_geografia FROM dim_geografia WHERE nombre_region = $1 AND nombre_comuna = $2",
                    region,
                    comuna,
                )

                if row:
                    geo_id = row["id_geografia"]
                else:
                    # Create
                    geo_id = await conn.fetchval(
                        """
                        INSERT INTO dim_geografia (nombre_region, nombre_comuna)
                        VALUES ($1, $2)
                        ON CONFLICT (nombre_region, nombre_comuna) 
                        DO UPDATE SET nombre_region = EXCLUDED.nombre_region
                        RETURNING id_geografia
                        """,
                        region,
                        comuna,
                    )

                self._geo_cache[key] = geo_id
                return geo_id

    async def get_or_create_empresa(self, nombre_empresa: str) -> int:
        """Get or create empresa dimension with caching."""
        if nombre_empresa in self._emp_cache:
            return self._emp_cache[nombre_empresa]

        async with self._emp_lock:
            if nombre_empresa in self._emp_cache:
                return self._emp_cache[nombre_empresa]

            async with self.pool.acquire() as conn:
                row = await conn.fetchrow(
                    "SELECT id_empresa FROM dim_empresa WHERE nombre_empresa = $1",
                    nombre_empresa,
                )

                if row:
                    emp_id = row["id_empresa"]
                else:
                    emp_id = await conn.fetchval(
                        """
                        INSERT INTO dim_empresa (nombre_empresa)
                        VALUES ($1)
                        ON CONFLICT (nombre_empresa) 
                        DO UPDATE SET nombre_empresa = EXCLUDED.nombre_empresa
                        RETURNING id_empresa
                        """,
                        nombre_empresa,
                    )

                self._emp_cache[nombre_empresa] = emp_id
                return emp_id

    async def get_id_tiempo(self, fecha: date) -> Optional[int]:
        """Get tiempo ID."""
        async with self.pool.acquire() as conn:
            return await conn.fetchval(
                "SELECT id_tiempo FROM dim_tiempo WHERE fecha = $1", fecha
            )

    async def save_records(self, records: List[Dict[str, Any]]) -> Dict[str, int]:
        """Save batch of records."""
        if not records:
            return {"insertados": 0}

        try:
            # Prepare batch data
            # We need to resolve dimensions first.
            # Doing this sequentially in a loop might be slow if cache misses.
            # But with cache populated, it's fast.

            tuples = []

            # Pre-resolve dims for the batch
            # In a real high-perf scenario, we might want to batch these lookups too,
            # but for now, rely on cache.

            for r in records:
                id_geo = await self.get_or_create_geografia(
                    r.get("REGION") or "DESCONOCIDO", r.get("COMUNA") or "DESCONOCIDO"
                )
                id_emp = await self.get_or_create_empresa(
                    r.get("EMPRESA") or "DESCONOCIDO"
                )
                # Optimize: maybe cache tiempo roughly or assuming it exists?
                # For safety, let's query it or rely on a local cache for dates?
                # For now query.
                id_tiempo = await self.get_id_tiempo(r.get("FECHA_DT") or date.today())

                if not id_tiempo:
                    # If date not found in dim_tiempo, log warning or skip?
                    # For now skip or use default?
                    # Let's assume dim_tiempo is populated.
                    continue

                tuples.append(
                    (
                        r["ID_UNICO"],
                        id_geo,
                        id_emp,
                        id_tiempo,
                        r.get("CLIENTES_AFECTADOS", 0),
                        r.get("HORA_INT"),
                        r.get("TIMESTAMP_SERVER"),
                        r.get("FECHA_STR"),
                        r.get("ACTUALIZADO_HACE"),
                    )
                )

            if not tuples:
                return {"insertados": 0}

            query = """
                INSERT INTO fact_interrupciones (
                    hash_id, id_geografia, id_empresa, id_tiempo,
                    clientes_afectados, hora_interrupcion,
                    hora_server_scraping, fecha_int_str, actualizado_hace
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                ON CONFLICT (hash_id) DO NOTHING
            """

            async with self.pool.acquire() as conn:
                await conn.executemany(query, tuples)

            return {"insertados": len(tuples)}

        except Exception as e:
            logger.error(f"❌ Async Batch Error: {e}")
            raise

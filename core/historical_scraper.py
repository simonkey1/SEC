"""Historical scraper for SEC data with retry protocols and DETAILED LOGGING.

This module allows scraping historical data from SEC by specifying
custom date/time ranges with automatic retry on failures.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import random
import time
import pytz

from core.retry_handler import retry_with_backoff

# Configurar logger
logger = logging.getLogger(__name__)


FETCH_SEC_DATA_SCRIPT = """
                    async (payload) => {
                        try {
                            const response = await fetch('https://apps.sec.cl/INTONLINEv1/ClientesAfectados/GetPorFecha', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json; charset=utf-8'
                                },
                                body: JSON.stringify(payload)
                            });
                            
                            if (!response.ok) {
                                return { error: `HTTP ${response.status}`, data: null };
                            }
                            
                            const data = await response.json();
                            
                            // Intentar obtener hora del servidor también
                            const timeResponse = await fetch('https://apps.sec.cl/INTONLINEv1/ClientesAfectados/GetHoraServer', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json; charset=utf-8'
                                }
                            });
                            
                            let horaServer = null;
                            if (timeResponse.ok) {
                                horaServer = await timeResponse.json();
                            }
                            
                            return { data: data, horaServer: horaServer, error: null };
                        } catch (e) {
                            return { error: e.toString(), data: null };
                        }
                    }
                """
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
]
EXTRA_HEADERS = {
    "Accept-Language": "es-CL,es;q=0.9,en;q=0.8",
    "Referer": "https://www.sec.cl/",
    "sec-ch-ua-platform": '"Windows"',
    "sec-ch-ua": '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
}


class SECHistoricalScraper:
    """Scraper for historical SEC data with configurable date ranges."""

    def __init__(self):
        """Initialize the historical scraper."""
        self.registros = []
        self.hora_server = None
        self.chile_tz = pytz.timezone("America/Santiago")

    @retry_with_backoff(
        max_attempts=5,
        base_delay=3.0,
        max_delay=60.0,
        strategy="exponential",
        exceptions=(PlaywrightTimeoutError, Exception),
        logger=logger,
    )
    def scrape_datetime(self, year: int, month: int, day: int, hour: int) -> dict:
        """Scrape data for a specific date and time.

        Args:
            year: Year (e.g., 2017)
            month: Month (1-12)
            day: Day (1-31)
            hour: Hour (0-23)

        Returns:
            dict: Dictionary with 'data' and 'hora_server'

        Raises:
            Exception: If scraping fails after all retries
        """
        self.registros = []
        self.hora_server = None

        logger.info(f"🔍 Scraping: {year}-{month:02d}-{day:02d} {hour:02d}:00")

        try:
            with sync_playwright() as p:
                # User agents para rotar
                user_agents = USER_AGENTS
                ua = random.choice(user_agents)

                logger.info("  🌐 Lanzando navegador...")
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent=ua,
                    viewport={"width": 1920, "height": 1080},
                    locale="es-CL",
                    timezone_id="America/Santiago",
                )
                page = context.new_page()

                # Headers adicionales
                page.set_extra_http_headers(EXTRA_HEADERS)

                logger.info("  🔗 Conectando a SEC...")

                # Ir a la home primero
                page.goto(
                    "https://www.sec.cl/", wait_until="domcontentloaded", timeout=60000
                )
                logger.info("  ✓ Home cargada")
                time.sleep(2)

                # Luego a la aplicación
                logger.info("  🔗 Accediendo a app de interrupciones...")
                page.goto(
                    "https://apps.sec.cl/INTONLINEv1/index.aspx",
                    wait_until="commit",
                    timeout=90000,
                )
                logger.info("  ✓ App cargada")
                time.sleep(10)

                # Payload con fecha histórica
                payload = {"anho": year, "mes": month, "dia": day, "hora": hour}

                logger.info(f"  📡 Ejecutando fetch API con payload: {payload}")

                # Fetch directo a la API
                result = page.evaluate(
                    FETCH_SEC_DATA_SCRIPT,
                    payload,
                )

                browser.close()
                logger.info("  🔒 Navegador cerrado")

                # Procesar resultado
                if result.get("error"):
                    logger.error(f"  ❌ Error en fetch: {result['error']}")
                    raise Exception(f"Error en fetch API: {result['error']}")
                elif result.get("data") is not None:
                    self.registros = result["data"]
                    self.hora_server = result.get("horaServer")
                    logger.info(f"  ✅ Capturados {len(self.registros)} registros")
                else:
                    logger.warning("  ⚠️ No se detectaron datos")

                return {
                    "data": self.registros,
                    "hora_server": self.hora_server,
                    "fecha_consultada": f"{year}-{month:02d}-{day:02d} {hour:02d}:00",
                }

        except PlaywrightTimeoutError as e:
            logger.error(f"  ❌ Timeout: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"  ❌ Error: {str(e)}")
            raise

    def scrape_date_range(
        self, start_date: datetime, end_date: datetime, hour_interval: int = 6
    ) -> List[Dict]:
        """Scrape data for a date range.

        Args:
            start_date: Start date (datetime object)
            end_date: End date (datetime object)
            hour_interval: Hours between samples (default: 6, samples at 0, 6, 12, 18)

        Returns:
            List of dictionaries with scraped data for each datetime
        """
        results = []
        current = start_date

        total_points = 0
        while current <= end_date:
            for hour in range(0, 24, hour_interval):
                if current > end_date:
                    break
                total_points += 1

        logger.info(f"📅 Rango: {start_date.date()} a {end_date.date()}")
        logger.info(f"📊 Total de puntos a scrapear: {total_points}")
        logger.info(f"⏱️ Tiempo estimado: {total_points * 20 / 60:.1f} minutos")

        current = start_date
        point_num = 0
        successful = 0
        failed = 0

        while current <= end_date:
            for hour in range(0, 24, hour_interval):
                if current > end_date:
                    break

                point_num += 1
                logger.info(f"\n{'=' * 60}")
                logger.info(
                    f"📍 Punto {point_num}/{total_points} ({point_num / total_points * 100:.1f}%)"
                )
                logger.info(f"📅 Fecha: {current.date()} {hour:02d}:00")
                logger.info(f"{'=' * 60}")

                try:
                    result = self.scrape_datetime(
                        year=current.year,
                        month=current.month,
                        day=current.day,
                        hour=hour,
                    )
                    results.append(result)
                    successful += 1
                    logger.info(
                        f"✅ Punto {point_num} exitoso - Total exitosos: {successful}/{point_num}"
                    )

                    # Pequeña pausa entre requests
                    logger.info("  ⏸️ Pausa de 2s...")
                    time.sleep(2)

                except Exception as e:
                    failed += 1
                    logger.error(f"❌ Punto {point_num} falló: {str(e)[:100]}")
                    logger.info(f"⚠️ Total fallidos: {failed}/{point_num}")
                    continue

            current += timedelta(days=1)

        logger.info(f"\n{'=' * 60}")
        logger.info(
            f"✅ COMPLETADO: {successful}/{total_points} exitosos ({successful / total_points * 100:.1f}%)"
        )
        logger.info(
            f"❌ Fallidos: {failed}/{total_points} ({failed / total_points * 100:.1f}%)"
        )
        logger.info(f"{'=' * 60}")

        return results

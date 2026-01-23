"""Alternative HTTP-based scraper for SEC data.

This module provides a lightweight scraper that makes direct HTTP requests
to SEC's API instead of using Playwright, avoiding bot detection issues.
"""

import httpx
from datetime import datetime
from typing import Dict, List, Optional

from config import URL_SEC_GET_POR_FECHA, URL_SEC_GET_HORA_SERVER


class SECScraperHTTP:
    """HTTP-based scraper for SEC API (no browser automation).
    
    This scraper makes direct POST requests to SEC's API endpoints,
    bypassing the need for Playwright and avoiding bot detection.
    
    Attributes:
        registros (list): List of dictionaries with captured outages.
        hora_server (str): Official date and time reported by SEC server.
    """

    def __init__(self):
        """Initializes the scraper object with empty lists and values."""
        self.registros = []
        self.hora_server = None

    def run(self) -> Dict[str, any]:
        """Fetches data directly from SEC API using HTTP requests.

        Makes POST requests to GetPorFecha and GetHoraServer endpoints
        to retrieve outage data and server time.

        Returns:
            dict: Dictionary containing 'data' (records) and 'hora_server'.
        """
        self.registros = []
        self.hora_server = None

        # Headers para parecer navegador real
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "es-CL,es;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/json; charset=UTF-8",
            "Origin": "https://www.sec.cl",
            "Referer": "https://www.sec.cl/interrupciones-en-linea/",
            "X-Requested-With": "XMLHttpRequest",
        }

        print("🌐 Haciendo request HTTP directo a la SEC...")

        try:
            with httpx.Client(headers=headers, timeout=30.0) as client:
                # 1. Obtener hora del servidor
                try:
                    print("⏰ Obteniendo hora del servidor...")
                    hora_response = client.post(
                        URL_SEC_GET_HORA_SERVER,
                        json={}
                    )
                    if hora_response.status_code == 200:
                        self.hora_server = hora_response.json()
                        print(f"✅ Hora server: {self.hora_server}")
                except Exception as e:
                    print(f"⚠️ No se pudo obtener hora del servidor: {e}")

                # 2. Obtener datos de cortes
                print("📡 Obteniendo datos de cortes...")
                
                # La API de la SEC necesita año, mes, día y hora separados
                now = datetime.now()
                payload = {
                    "anho": now.year,
                    "mes": now.month,
                    "dia": now.day,
                    "hora": now.hour
                }
                
                print(f"📅 Payload: {payload}")
                
                data_response = client.post(
                    URL_SEC_GET_POR_FECHA,
                    json=payload
                )

                if data_response.status_code == 200:
                    data = data_response.json()
                    if isinstance(data, list) and len(data) > 0:
                        self.registros = data
                        print(f"✅ ¡Datos capturados exitosamente! ({len(data)} registros)")
                    else:
                        print("⚠️ La API devolvió datos vacíos (sin cortes actualmente)")
                else:
                    print(f"❌ Error HTTP {data_response.status_code}")

        except httpx.TimeoutException:
            print("❌ Timeout al conectar con la SEC")
        except Exception as e:
            print(f"❌ Error inesperado: {e}")

        if not self.registros:
            print("⚠️ No se detectaron datos")

        return {"data": self.registros, "hora_server": self.hora_server}

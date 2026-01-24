from playwright.sync_api import sync_playwright
import random
import time
from datetime import datetime

from config import URL_SEC_PRINCIPAL


class SECScraperAlternative:
    """Scraper that uses direct fetch to SEC API instead of network interception.
    
    This approach navigates to the page to get cookies/session, then executes
    a direct fetch to the API endpoint to get all data at once.
    """

    def __init__(self):
        """Initializes the scraper object with empty lists and values."""
        self.registros = []
        self.hora_server = None

    def run(self) -> dict:
        """Starts the navigation and data capture process using direct fetch.

        Launches a headless browser, navigates to the SEC page to get session,
        then executes a direct fetch to the API endpoint.

        Returns:
            dict: Dictionary containing 'data' (records) and 'hora_server'.
        """
        self.registros = []
        self.hora_server = None
        print("🚀 Iniciando navegador...")

        with sync_playwright() as p:
            # Lista de User-Agents recientes para rotar
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0"
            ]
            ua = random.choice(user_agents)
            
            browser = p.chromium.launch(headless=True)
            # Simular un dispositivo real
            context = browser.new_context(
                user_agent=ua,
                viewport={'width': 1920, 'height': 1080},
                locale="es-CL",
                timezone_id="America/Santiago"
            )
            page = context.new_page()

            # Añadir headers extras para parecer más humano
            page.set_extra_http_headers({
                "Accept-Language": "es-CL,es;q=0.9,en;q=0.8",
                "Referer": "https://www.sec.cl/",
                "sec-ch-ua-platform": '"Windows"',
                "sec-ch-ua": '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"'
            })

            print(f"🔗 Navegando a la SEC con UA: {ua[:40]}...")
            
            try:
                # Primero ir a la home de SEC para establecer contexto/cookies generales
                page.goto("https://www.sec.cl/", wait_until="domcontentloaded", timeout=60000)
                time.sleep(2)
                
                # Luego ir a la aplicación de interrupciones
                print("🔗 Accediendo a la aplicación de interrupciones...")
                page.goto("https://apps.sec.cl/INTONLINEv1/index.aspx", 
                         wait_until="commit", # Capturar apenas empiece a cargar
                         timeout=90000)
                
                # Esperar un poco a que se asiente la sesión y JS cargue
                print("⏳ Esperando estabilización de sesión (15s)...")
                time.sleep(15)
                
            except Exception as e:
                print(f"⚠️ Nota en navegación: {str(e)}")
                # Si falló por timeout pero la página ya "comiteó", intentamos seguir
                pass

            print("📡 Ejecutando fetch directo a la API...")
            
            # Obtener fecha y hora actual
            now = datetime.now()
            
            # Ejecutar fetch directo desde el navegador
            result = page.evaluate("""
                async (payload) => {
                    try {
                        // Fetch a GetPorFecha
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
                        
                        // Fetch a GetHoraServer
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
            """, {
                "anho": now.year,
                "mes": now.month,
                "dia": now.day,
                "hora": now.hour
            })

            browser.close()

            # Procesar resultado
            if result.get("error"):
                print(f"❌ Error en fetch: {result['error']}")
            elif result.get("data"):
                self.registros = result["data"]
                self.hora_server = result.get("horaServer")
                print(f"✅ ¡Datos capturados exitosamente! ({len(self.registros)} registros via FETCH)")
            else:
                print("⚠️ No se detectaron datos.")

        if not self.registros:
            print("❌ No se obtuvieron datos del fetch.")

        return {"data": self.registros, "hora_server": self.hora_server}

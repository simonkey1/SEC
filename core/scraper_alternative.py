from playwright.sync_api import sync_playwright
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
            # Usar un User-Agent real para evitar bloqueos
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent=user_agent)
            page = context.new_page()

            print("🔗 Navegando a la SEC (iframe directo)...")
            # Navegar directamente al iframe que contiene la aplicación
            page.goto("https://apps.sec.cl/INTONLINEv1/index.aspx", timeout=60000)

            # Esperar a que la página esté completamente cargada
            print("⏳ Esperando carga completa...")
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(5000)  # Esperar 5s adicionales

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

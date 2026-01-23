from playwright.sync_api import Response, sync_playwright

from config import URL_SEC_PRINCIPAL


class SECScraper:
    """Class responsible for intercepting and capturing data from the SEC API.

    This class uses Playwright to navigate the official page and act as
    a network interceptor, capturing JSON responses from the data
    and server time endpoints.

    Attributes:
        registros (list): List of dictionaries with captured outages.
        hora_server (str): Official date and time reported by SEC server.
    """

    def __init__(self):
        """Initializes the scraper object with empty lists and values."""
        self.registros = []
        self.hora_server = None

    def handle_response(self, response: Response):
        """Event handler to intercept network responses.

        Filters SEC URLs to extract outage data (GetPorFecha)
        or official time (GetHoraServer).

        Args:
            response (Response): Response object captured by Playwright.
        """
        # Filtramos por URL, independientemente de si es GET o POST
        if "GetPorFecha" in response.url:
            method = response.request.method
            try:
                if response.status == 200:
                    data = response.json()
                    # Si es una lista y tiene datos, es lo que buscamos
                    if isinstance(data, list) and len(data) > 0:
                        self.registros.extend(data)
                        print(
                            f"✅ ¡Datos capturados exitosamente! ({len(data)} registros via {method})"
                        )
                else:
                    # Si el status no es 200, algo falló en esa petición
                    if method == "POST":
                        print(
                            f"⚠️ El POST a GetPorFecha devolvió status {response.status}"
                        )
            except Exception:
                # Silenciamos errores de parsing si la respuesta no era JSON
                pass

        elif "GetHoraServer" in response.url:
            try:
                if response.status == 200:
                    self.hora_server = response.json()
                    # GetHoraServer suele devolver [{"FECHA": "23/05/2024 15:30"}
            except Exception:
                pass

    def run(self) -> dict:
        """Starts the navigation and data capture process.

        Launches a headless browser, navigates to the SEC page,
        waits for AJAX requests and returns the results.

        Returns:
            dict: Dictionary containing 'data' (records) and 'hora_server'.
        """
        self.registros = []  # Limpiamos el saco
        self.hora_server = None
        print("🚀 Iniciando navegador...")

        with sync_playwright() as p:
            # Usar un User-Agent real para evitar bloqueos
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox'
                ]
            )
            
            # Configuración stealth para parecer navegador real
            context = browser.new_context(
                user_agent=user_agent,
                viewport={'width': 1920, 'height': 1080},
                locale='es-CL',
                timezone_id='America/Santiago',
                permissions=['geolocation'],
                geolocation={'latitude': -33.4489, 'longitude': -70.6693},  # Santiago, Chile
                color_scheme='light',
                extra_http_headers={
                    'Accept-Language': 'es-CL,es;q=0.9,en;q=0.8',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1'
                }
            )
            
            page = context.new_page()
            
            # Ocultar que es un bot
            page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['es-CL', 'es', 'en']
                });
            """)

            page.on("response", self.handle_response)

            print("🔗 Navegando a la SEC...")
            page.goto(URL_SEC_PRINCIPAL, timeout=60000)

            # Esperamos un tiempo prudente para que la página tire sus peticiones AJAX
            print("⏳ Esperando datos (30s)...")
            page.wait_for_timeout(30000)

            browser.close()

        if not self.registros:
            print("❌ No se encontró la petición 'GetPorFecha' en esta vuelta.")

        return {"data": self.registros, "hora_server": self.hora_server}

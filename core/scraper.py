from playwright.sync_api import sync_playwright, Response
from config import URL_SEC_PRINCIPAL


class SECScraper:
    """Clase encargada de interceptar y capturar datos de la API de la SEC.
    
    Esta clase utiliza Playwright para navegar por la página oficial y actuar como
    un interceptor de red, capturando las respuestas JSON de los endpoints de 
    datos y hora del servidor.
    
    Attributes:
        registros (list): Lista de diccionarios con los cortes capturados.
        hora_server (str): Fecha y hora oficial reportada por el servidor SEC.
    """

    def __init__(self):
        """Inicializa el objeto scraper con listas y valores vacíos."""
        self.registros = []
        self.hora_server = None

    def handle_response(self, response: Response):
        """Manejador de eventos para interceptar respuestas de red.
        
        Filtra las URLs de la SEC para extraer datos de cortes (GetPorFecha) 
        o la hora oficial (GetHoraServer).

        Args:
            response (Response): Objeto de respuesta capturado por Playwright.
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
                        print(f"✅ ¡Datos capturados exitosamente! ({len(data)} registros via {method})")
                else:
                    # Si el status no es 200, algo falló en esa petición
                    if method == "POST":
                        print(f"⚠️ El POST a GetPorFecha devolvió status {response.status}")
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
        """Inicia el proceso de navegación y captura de datos.
        
        Lanza un navegador en modo headless, navega a la página de la SEC,
        espera las peticiones AJAX y retorna los resultados.

        Returns:
            dict: Diccionario conteniendo 'data' (registros) y 'hora_server'.
        """
        self.registros = [] # Limpiamos el saco
        self.hora_server = None
        print("🚀 Iniciando navegador...")
        
        with sync_playwright() as p:
            # Usar un User-Agent real para evitar bloqueos
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent=user_agent)
            page = context.new_page()

            page.on("response", self.handle_response)
            
            print("🔗 Navegando a la SEC...")
            page.goto(URL_SEC_PRINCIPAL, timeout=60000)
            
            # Esperamos un tiempo prudente para que la página tire sus peticiones AJAX
            print("⏳ Esperando datos (10s)...")
            page.wait_for_timeout(10000) 
            
            browser.close()
            
        if not self.registros:
            print("❌ No se encontró la petición 'GetPorFecha' en esta vuelta.")
            
        return {
            "data": self.registros,
            "hora_server": self.hora_server
        }
from playwright.sync_api import sync_playwright, Response

class SECScraper:
    def __init__(self):
        self.registros = []
        self.hora_server = None

    def handle_response(self, response: Response):
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
                    data = response.json()
                    # GetHoraServer suele devolver [{"FECHA": "23/05/2024 15:30"}]
                    if isinstance(data, list) and len(data) > 0:
                        self.hora_server = data[0].get("FECHA")
                        print(f"🕒 Hora del servidor SEC capturada: {self.hora_server}")
            except Exception:
                pass
    
    def run(self) -> dict:
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
            page.goto("https://apps.sec.cl/INTONLINEv1/index.aspx", timeout=60000)
            
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
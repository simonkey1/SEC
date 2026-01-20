from playwright.sync_api import sync_playwright, Response

def get_hora_server(response: Response):
    if "GetHoraServer" in response.url:
        try:
            if response.status == 200:
                data = response.json()
                        # GetHoraServer suele devolver [{"FECHA": "23/05/2024 15:30"}]
                if isinstance(data, list) and len(data) > 0:
                        hora_server = data[0].get("FECHA")
                        print(f"🕒 Hora del servidor SEC capturada: {hora_server}")
        except Exception:
                    pass
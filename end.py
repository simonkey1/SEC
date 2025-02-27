from playwright.sync_api import sync_playwright
import pandas as pd
import os
import time
import re  # 📌 Nueva importación para extraer números de cadenas
from datetime import datetime, timedelta

# 📂 Nombres de los archivos CSV
csv_tiempo_real = "clientes_afectados_tiempo_real.csv"
csv_historico = "clientes_afectados_historico.csv"

# 🛠️ Función para capturar y almacenar datos
def intercept_responses():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        registros = []  # Lista para almacenar datos nuevos

        # 🎯 Función para interceptar las respuestas de la API
        def handle_response(response):
            if "GetPorFecha" in response.url:
                try:
                    data = response.json()
                    timestamp_actual = datetime.now()  # Tiempo de consulta

                    for entry in data:
                        actualizado_hace = entry.get("ACTUALIZADO_HACE", "")
                        minutos_atras = 0

                        # 🔎 Extraer los minutos de "ACTUALIZADO_HACE" con REGEX
                        match = re.search(r'(\d+)\s+Minutos', actualizado_hace)
                        if match:
                            minutos_atras = int(match.group(1))  # Extrae el número antes de "Minutos"

                        # ⏳ Calcular la hora exacta del reporte
                        hora_exacta_reporte = timestamp_actual - timedelta(minutes=minutos_atras)

                        # 📌 Construir el ID único del registro
                        unique_id = f"{entry.get('FECHA_INT_STR', '')}-{entry.get('REGION', '')}-{entry.get('COMUNA', '')}-{entry.get('EMPRESA', '')}-{entry.get('CLIENTES_AFECTADOS', 0)}-{hora_exacta_reporte.strftime('%Y-%m-%d %H:%M:%S')}"

                        # 📝 Guardar el registro
                        registros.append({
                            "ID_UNICO": unique_id,
                            "TIMESTAMP": timestamp_actual.strftime("%Y-%m-%d %H:%M:%S"),
                            "HORA_EXACTA_REPORTE": hora_exacta_reporte.strftime("%Y-%m-%d %H:%M:%S"),
                            "FECHA": entry.get("FECHA_INT_STR", ""),
                            "REGION": entry.get("NOMBRE_REGION", ""),
                            "COMUNA": entry.get("NOMBRE_COMUNA", ""),
                            "EMPRESA": entry.get("NOMBRE_EMPRESA", ""),
                            "CLIENTES_AFECTADOS": entry.get("CLIENTES_AFECTADOS", 0),
                            "ACTUALIZADO_HACE": actualizado_hace
                        })
                except:
                    print("❌ Error al procesar JSON")

        # 🔄 Capturar respuestas de la API
        page.on("response", handle_response)

        # 🌐 Acceder a la página
        page.goto("https://apps.sec.cl/INTONLINEv1/index.aspx")
        page.wait_for_timeout(5000)  # Espera para capturar datos

        # 🔒 Cerrar navegador
        browser.close()

        # 📊 Guardar en CSV (Tiempo Real y Histórico)
        if registros:
            df_new = pd.DataFrame(registros)

            # 📌 Guardar en CSV histórico (sin borrar registros)
            if os.path.exists(csv_historico):
                df_historico = pd.read_csv(csv_historico, encoding="utf-8-sig")
                df_historico = pd.concat([df_historico, df_new]).drop_duplicates(subset=["ID_UNICO"], keep="first")
            else:
                df_historico = df_new

            df_historico.to_csv(csv_historico, index=False, encoding="utf-8-sig")

            # 📌 Guardar en CSV de Tiempo Real (mantiene solo los datos más recientes)
            if os.path.exists(csv_tiempo_real):
                df_tiempo_real = pd.read_csv(csv_tiempo_real, encoding="utf-8-sig")
                df_tiempo_real = df_new  # Sobrescribir con los datos nuevos
            else:
                df_tiempo_real = df_new

            df_tiempo_real.to_csv(csv_tiempo_real, index=False, encoding="utf-8-sig")

            print(f"✅ Datos guardados en:\n📌 {csv_historico} (Histórico)\n📌 {csv_tiempo_real} (Tiempo Real)")

# 🕒 Automatización cada 5 minutos
while True:
    intercept_responses()
    print("⏳ Esperando 5 minutos para la siguiente ejecución...\n")
    time.sleep(5 * 60)  # 5 minutos en segundos

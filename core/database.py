"""Módulo de persistencia y gestión de rutas de datos.

Este módulo se encarga de definir las rutas de almacenamiento y proveer funciones
para guardar los datos procesados en formatos CSV (local).
"""
import pandas as pd
import os
from dotenv import load_dotenv
import logging
from supabase import create_client, Client
from core.notifications import send_capacity_alert
logger = logging.getLogger(__name__)

# Rutas globales para gestión de archivos

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) 
BASE_DIR = os.path.dirname(SCRIPT_DIR)
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

# Cerciorarse de que el directorio de salida existe

os.makedirs(OUTPUT_DIR, exist_ok=True)

csv_tiempo_real = os.path.join(OUTPUT_DIR, "clientes_afectados_tiempo_real.csv")
csv_historico = os.path.join(OUTPUT_DIR, "clientes_afectados_historico.csv")

def save_data_csv(registros):
    """Guarda los registros procesados en archivos CSV locales.
    
    Gestiona dos archivos: uno histórico (incremental y sin duplicados) y
    uno de tiempo real (sobrescritura del estado actual).

    Args:
        registros (list): Lista de diccionarios procesados por el transformer.
    """
    if registros:
        df_new = pd.DataFrame(registros)

        # Guardar en histórico
        if os.path.exists(csv_historico):
            df_hist = pd.read_csv(csv_historico, encoding="utf-8-sig")
            df_hist = pd.concat([df_hist, df_new], ignore_index=True)
            df_hist = df_hist.drop_duplicates(subset=["ID_UNICO", "TIMESTAMP"])
        else:
            df_hist = df_new
            print(f"✅ Datos guardados en:\n📌 {csv_historico} (Histórico)\n📌 {csv_tiempo_real} (Tiempo Real)")

        df_hist.to_csv(csv_historico, index=False, encoding="utf-8-sig")

        # Guardar en tiempo real (sobrescribe)
        df_new.to_csv(csv_tiempo_real, index=False, encoding="utf-8-sig")

        print(f"✅ Datos guardados en:\n📌 {csv_historico} (Histórico)\n📌 {csv_tiempo_real} (Tiempo Real)")

def save_data_sql():
     pass



def check_database_capacity(threshold_percent = 85):
    load_dotenv()

    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_KEY")

    supabase: Client = create_client(url, key)
    try:

        response = (
        supabase.table('fact_interrupciones')
        .select('*', count='exact').execute()
    )
        total_filas = response.count


        size_mb = (total_filas * 200) / 1024 / 1024

        porcentaje = (size_mb / 500) * 100
        alert_sent = False
        if porcentaje >= threshold_percent:
            send_capacity_alert(porcentaje=porcentaje, size_mb=size_mb)
            logger.warning(f"⚠️ Base de datos al {porcentaje:.2f}% de capacidad")
            alert_sent = True
        
        # 5. Retornar estado
        return {
            "size_mb": round(size_mb, 2),
            "porcentaje": round(porcentaje, 2),
            "alert_sent": alert_sent,
            "total_filas": total_filas  # Extra: útil para debugging
            }
        
    except Exception as e:
        logger.error(f"❌ Error verificando capacidad: {e}")
        return {
            "size_mb": 0,
            "porcentaje": 0,
            "alert_sent": False,
            "total_filas": 0
        }


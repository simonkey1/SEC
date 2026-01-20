"""Módulo de persistencia y gestión de rutas de datos.

Este módulo se encarga de definir las rutas de almacenamiento y proveer funciones
para guardar los datos procesados en formatos CSV (local).
"""
import pandas as pd
import os

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
import pandas as pd
import os

# path

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) 
BASE_DIR = os.path.dirname(SCRIPT_DIR)
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

# make sure create directory if doesnt exist

os.makedirs(OUTPUT_DIR, exist_ok=True)

csv_tiempo_real = os.path.join(OUTPUT_DIR, "clientes_afectados_tiempo_real.csv")
csv_historico = os.path.join(OUTPUT_DIR, "clientes_afectados_historico.csv")

def save_data_csv(registros):
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
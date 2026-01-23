import os

import pandas as pd

from core.database import csv_historico, csv_tiempo_real


def check_variacion_historico():
    """
    Replica la lógica de la medida DAX para comparar la suma de CLIENTES_AFECTADOS
    entre el último y el penúltimo TIMESTAMP, pero asegurándose de que sean snapshots distintos.
    """
    if not os.path.exists(csv_historico):
        print("No existe el histórico, no se puede chequear variación.")
        return

    df_hist = pd.read_csv(csv_historico, encoding="utf-8-sig")
    if len(df_hist) < 2:
        print("No hay suficiente data en el histórico para calcular la variación.")
        return

    # Obtenemos la lista de TIMESTAMP distintos y la ordenamos
    timestamps_unicos = (
        df_hist["TIMESTAMP"].drop_duplicates().sort_values(ascending=True)
    )
    if len(timestamps_unicos) < 2:
        print("Solo hay un snapshot único, no hay penúltimo para comparar.")
        return

    # El último timestamp (ejecución más reciente)
    ultimo_tiempo = timestamps_unicos.iloc[-1]
    # El penúltimo timestamp (la ejecución anterior)
    penultimo_tiempo = timestamps_unicos.iloc[-2]

    # Sumar los CLIENTES_AFECTADOS en cada snapshot
    afectados_ultimo = df_hist.loc[
        df_hist["TIMESTAMP"] == ultimo_tiempo, "CLIENTES_AFECTADOS"
    ].sum()
    afectados_penultimo = df_hist.loc[
        df_hist["TIMESTAMP"] == penultimo_tiempo, "CLIENTES_AFECTADOS"
    ].sum()

    variacion = afectados_ultimo - afectados_penultimo

    print(f"🔎 Health Check:")
    print(f"    Último snapshot: {ultimo_tiempo} → {afectados_ultimo} afectados")
    print(
        f"    Penúltimo snapshot: {penultimo_tiempo} → {afectados_penultimo} afectados"
    )
    print(f"    Variación (DAX-like): {variacion}\n")
    print(
        f"✅ Datos guardados en:\n📌 {csv_historico} (Histórico)\n📌 {csv_tiempo_real} (Tiempo Real)"
    )

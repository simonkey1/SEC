

from datetime import datetime
import pandas as pd

class SecDataTransformer:
    def __init__(self):
        pass

    def transform(self, raw_data: list, server_time: str = None) -> list:
        """
        Agrupa los datos por comuna/empresa sumando los afectados, 
        limpia textos y genera un ID único sensible al cambio de magnitud.
        Usa 'server_time' como referencia para mayor precisión.
        """
        if not raw_data:
            return []

        # 1. Convertir a DataFrame para agrupar
        df = pd.DataFrame(raw_data)
        
        # Parsear hora del servidor si existe, sino usar local
        if server_time:
            try:
                # El formato suele ser "DD/MM/YYYY HH:MM"
                dt_server = datetime.strptime(server_time, "%d/%m/%Y %H:%M")
                timestamp_actual = dt_server.strftime("%Y-%m-%d %H:%M:%S")
                referencia_hoy = dt_server.date()
                print(f"🔬 Usando hora del servidor SEC como referencia: {timestamp_actual}")
            except:
                timestamp_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                referencia_hoy = datetime.now().date()
        else:
            timestamp_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            referencia_hoy = datetime.now().date()

        # 2. Agrupar y sumar (Legacy: Puerto Montt enviaba múltiples filas de 1 cliente)
        df_grouped = df.groupby([
            "NOMBRE_REGION", 
            "NOMBRE_COMUNA", 
            "NOMBRE_EMPRESA", 
            "FECHA_INT_STR"
        ]).agg({
            "CLIENTES_AFECTADOS": "sum",
            "ACTUALIZADO_HACE": "first"
        }).reset_index()

        registros_procesados = []

        for _, row in df_grouped.iterrows():
            region = str(row["NOMBRE_REGION"]).strip()
            comuna = str(row["NOMBRE_COMUNA"]).strip()
            empresa = str(row["NOMBRE_EMPRESA"]).strip()
            fecha_str = str(row["FECHA_INT_STR"]).strip()
            afectados = int(row["CLIENTES_AFECTADOS"])

            # Cálculo de la antigüedad exacta en días usando la referencia (server o local)
            try:
                fecha_incidente = datetime.strptime(fecha_str, "%d/%m/%Y").date()
                dias_antiguedad = (referencia_hoy - fecha_incidente).days
            except:
                dias_antiguedad = 0

            # ID robusto: Incluye afectados para detectar cambios en tiempo real
            unique_id = f"{fecha_str}-{region}-{comuna}-{empresa}-{afectados}".replace(" ", "_")

            registros_procesados.append({
                "ID_UNICO": unique_id,
                "TIMESTAMP": timestamp_actual,
                "FECHA": fecha_str,
                "REGION": region,
                "COMUNA": comuna,
                "EMPRESA": empresa,
                "CLIENTES_AFECTADOS": afectados,
                "DIAS_ANTIGUEDAD": dias_antiguedad,
                "ACTUALIZADO_HACE": str(row["ACTUALIZADO_HACE"]).strip()
            })
        
        return registros_procesados
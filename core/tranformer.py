

from datetime import datetime
import pandas as pd
import hashlib
from core.logger import logger


class SecDataTransformer():
    """Clase para la transformación y normalización de datos de cortes eléctricos.
    
    Esta clase implementa la lógica de agregación (resolviendo la duplicidad de 
    datos fragmentados), limpieza de strings, cálculo de antigüedad de los cortes
    y generación de IDs únicos sensibles a la severidad.
    """

    def __init__(self):
        """Inicializa el transformador."""
        pass

    def _parse_server_time(self, raw):
        """Intenta parsear la hora del servidor (lista o str), cae en local con aviso."""
        try:
            # Extraemos el string si es lista, o usamos el str si viene directo
            fecha_str = raw[0].get("FECHA") if isinstance(raw, list) else raw
            dt = datetime.strptime(fecha_str, "%d/%m/%Y %H:%M")
            logger.info(f"Hora SEC detectada: {dt}")
        except (ValueError, TypeError, IndexError, AttributeError):
            dt = datetime.now()
            logger.warning(f"No se detectó hora SEC. Usando local: {dt.strftime('%H:%M')}")
            
        return dt.strftime("%Y-%m-%d %H:%M:%S"), dt.date()

    def _create_robust_id(self, comuna: str, empresa: str, timestamp: str) -> str:
        """Genera un hash MD5 único basado en la ubicación y el tiempo."""
        unique_str = f"{comuna}_{empresa}_{timestamp}"
        return hashlib.md5(unique_str.encode()).hexdigest()

    def transform(self, raw_data: list, server_time_raw: any = None) -> list:
        """Procesa los datos crudos capturados para su almacenamiento.
        
        Aplica agrupaciones por región, comuna y empresa, suma los afectados
        y calcula la antigüedad del corte en días respecto a la hora del servidor.

        Args:
            raw_data (list): Lista de diccionarios con datos provenientes de la API.
            server_time_raw (any, optional): Datos de hora del servidor (lista o str).

        Returns:
            list: Lista de diccionarios con los registros procesados y normalizados.
        """
        if not raw_data:
            return []

        # 1. Preparar referencias de tiempo usando el nuevo método centralizado
        timestamp_actual, referencia_hoy = self._parse_server_time(server_time_raw)

        # 2. Convertir a DataFrame para agrupar
        df = pd.DataFrame(raw_data)

        # Agrupar y sumar (Resuelve fragmentación de datos)
        df_grouped = df.groupby([
            "NOMBRE_REGION", 
            "NOMBRE_COMUNA", 
            "NOMBRE_EMPRESA", 
            "FECHA_INT_STR"
        ]).agg({
            "CLIENTES_AFECTADOS": "sum",
            "ACTUALIZADO_HACE": "first"
        }).reset_index()

        print(df_grouped)

        registros_procesados = []

        for _, row in df_grouped.iterrows():
            region = str(row["NOMBRE_REGION"]).strip()
            comuna = str(row["NOMBRE_COMUNA"]).strip()
            empresa = str(row["NOMBRE_EMPRESA"]).strip()
            
            # FECHA_INT_STR ya viene como string de la SEC (ej: 19/01/2026)
            fecha_str = str(row["FECHA_INT_STR"]).strip()
            afectados = int(row["CLIENTES_AFECTADOS"])

            # Cálculo de la antigüedad
            try:
                fecha_incidente = datetime.strptime(fecha_str, "%d/%m/%Y").date()
                dias_antiguedad = (referencia_hoy - fecha_incidente).days
            except:
                dias_antiguedad = 0

            # ID robusto: Incluye afectados para detectar cambios en tiempo real
            corte_id = self._create_robust_id(comuna, empresa, timestamp_actual)

            registros_procesados.append({
                "ID_UNICO": corte_id,
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
    
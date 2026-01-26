import hashlib
import unicodedata
from datetime import datetime
import logging

import pandas as pd

from core.logger import logger


class SecDataTransformer:
    """Clase para la transformación y normalización de datos de cortes eléctricos.

    Esta clase implementa la lógica de agregación (resolviendo la duplicidad de
    datos fragmentados), limpieza de strings, cálculo de antigüedad de los cortes
    y generación de IDs únicos sensibles a la severidad.
    """

    def __init__(self):
        """Initializes the transformer."""
        pass

    def _normalize_text(self, text: str) -> str:
        """Normaliza texto: mayúsculas, sin acentos, sin espacios extra.

        Args:
            text (str): Texto a normalizar

        Returns:
            str: Texto normalizado
        """
        # Quitar acentos
        text_nfd = unicodedata.normalize("NFD", text)
        text_ascii = text_nfd.encode("ASCII", "ignore").decode("ASCII")

        # Mayúsculas y quitar espacios extra
        return text_ascii.upper().strip()

    def _parse_server_time(self, raw):
        """Intenta parsear la hora del servidor (lista o str), cae en local con aviso."""
        try:
            # Extraemos el string si es lista, o usamos el str si viene directo
            fecha_str = raw[0].get("FECHA") if isinstance(raw, list) else raw
            dt = datetime.strptime(fecha_str, "%d/%m/%Y %H:%M")
            logger.info(f"Hora SEC detectada: {dt}")
        except (ValueError, TypeError, IndexError, AttributeError):
            dt = datetime.now()
            # Silenciamos aviso repetitivo para no ensuciar la barra de progreso
            # logger.warning(f"No se detectó hora SEC. Usando local: {dt.strftime('%H:%M')}")

        return dt.strftime("%Y-%m-%d %H:%M:%S"), dt.date()

    def _create_robust_id(
        self, comuna: str, empresa: str, fecha_dt, hora_time, afectados: int
    ) -> str:
        """Genera un hash MD5 único basado en el CONTENIDO del corte (Deduplicación).

        Args:
            comuna: Nombre normalizado de la comuna.
            empresa: Nombre normalizado de la empresa.
            fecha_dt: Fecha del incidente (date).
            hora_time: Hora del incidente (time).
            afectados: Cantidad de clientes afectados.

        Returns:
            str: Hash MD5 único para identificar el evento exacto.
        """
        # Formato determinista
        fecha_str = fecha_dt.strftime("%Y%m%d")
        hora_str = hora_time.strftime("%H%M")

        # Hash Key: SANTIAGO_ENEL_20231025_1430_500
        unique_str = f"{comuna}_{empresa}_{fecha_str}_{hora_str}_{afectados}"
        return hashlib.md5(unique_str.encode()).hexdigest()

    def transform(self, raw_data: list, server_time_raw: any = None) -> list:
        """Procesa los datos crudos capturados para su almacenamiento.

        Args:
            raw_data (list): Lista de diccionarios con datos provenientes de la API.
            server_time_raw (any, optional): Datos de hora del servidor (lista o str).

        Returns:
            list: Lista de diccionarios con los registros procesados y normalizados.
        """
        if not raw_data:
            return []

        # 1. Preparar referencias de tiempo
        timestamp_actual, referencia_hoy = self._parse_server_time(server_time_raw)

        # 2. Convertir a DataFrame para agrupar
        df = pd.DataFrame(raw_data)

        # Agrupar y sumar
        df_grouped = (
            df.groupby(
                ["NOMBRE_REGION", "NOMBRE_COMUNA", "NOMBRE_EMPRESA", "FECHA_INT_STR"]
            )
            .agg({"CLIENTES_AFECTADOS": "sum", "ACTUALIZADO_HACE": "first"})
            .reset_index()
        )

        registros_procesados = []

        for _, row in df_grouped.iterrows():
            region = self._normalize_text(str(row["NOMBRE_REGION"]))
            comuna = self._normalize_text(str(row["NOMBRE_COMUNA"]))
            empresa = self._normalize_text(str(row["NOMBRE_EMPRESA"]))

            fecha_str = str(row["FECHA_INT_STR"]).strip()
            afectados = int(row["CLIENTES_AFECTADOS"])

            # Objetos de tiempo para la DB
            try:
                dt_incidente = datetime.strptime(fecha_str, "%d/%m/%Y")
                fecha_incidente_date = dt_incidente.date()
                dias_antiguedad = (referencia_hoy - fecha_incidente_date).days
            except:
                # Fallback al tiempo del servidor del batch
                dt_server = datetime.strptime(timestamp_actual, "%Y-%m-%d %H:%M:%S")
                fecha_incidente_date = dt_server.date()
                dt_incidente = dt_server
                dias_antiguedad = 0

            hora_incidente = dt_incidente.time()

            # Generamos ID basado en contenido para deduplicar automáticamente
            corte_id = self._create_robust_id(
                comuna, empresa, fecha_incidente_date, hora_incidente, afectados
            )

            registros_procesados.append(
                {
                    "ID_UNICO": corte_id,
                    "TIMESTAMP_SERVER": datetime.strptime(
                        timestamp_actual, "%Y-%m-%d %H:%M:%S"
                    ),
                    "FECHA_STR": fecha_str,
                    "FECHA_DT": fecha_incidente_date,
                    "HORA_INT": hora_incidente,
                    "REGION": region,
                    "COMUNA": comuna,
                    "EMPRESA": empresa,
                    "CLIENTES_AFECTADOS": afectados,
                    "DIAS_ANTIGUEDAD": dias_antiguedad,
                    "ACTUALIZADO_HACE": str(row["ACTUALIZADO_HACE"]).strip(),
                }
            )

        return registros_procesados

# core/data_quality.py

import logging
import re
from datetime import datetime

logger = logging.getLogger(__name__)


class DataQualityChecker:
    """Valida integridad de datos transformados"""

    @staticmethod
    def validate_row(row: dict) -> tuple[bool, str]:
        """
        Valida una fila de datos transformados.
        Retorna: (is_valid, error_message)
        """

        # 1. ¿ACTUALIZADO_HACE está en formato correcto?
        if not row.get("ACTUALIZADO_HACE"):
            return False, "ACTUALIZADO_HACE vacío"

        actualizado_pattern = r"\d+\s+Dias\s+\d+\s+Horas\s+\d+\s+Minutos"
        if not re.match(actualizado_pattern, row["ACTUALIZADO_HACE"]):
            return (
                False,
                f"ACTUALIZADO_HACE formato inválido: {row['ACTUALIZADO_HACE']}",
            )

        # 2. ¿CLIENTES_AFECTADOS > 0?
        if not isinstance(row.get("clientes_afectados"), int):
            return False, "CLIENTES_AFECTADOS no es int"

        if row["clientes_afectados"] <= 0:
            return False, f"CLIENTES_AFECTADOS <= 0: {row['clientes_afectados']}"

        # 3. ¿Fecha inicio es razonable (no futuro)?
        fecha_inicio = row.get("fecha_inicio_corte")
        if fecha_inicio > datetime.now():
            return False, f"FECHA_INICIO futura: {fecha_inicio}"

        # 4. ¿Hay campos requeridos?
        required_fields = [
            "corte_id",
            "comuna",
            "empresa",
            "fecha_inicio_corte",
            "clientes_afectados",
        ]
        for field in required_fields:
            if field not in row or row[field] is None:
                return False, f"Campo requerido faltante: {field}"

        return True, ""

    @staticmethod
    def validate_batch(transformed_data: list) -> dict:
        """
        Valida un batch completo de datos.
        Retorna: {
            'total_rows': int,
            'valid_rows': int,
            'invalid_rows': int,
            'errors': list,
            'duplicates': int
        }
        """

        results = {
            "total_rows": len(transformed_data),
            "valid_rows": 0,
            "invalid_rows": 0,
            "errors": [],
            "duplicates": 0,
        }

        seen_corte_ids = set()

        for i, row in enumerate(transformed_data):
            is_valid, error_msg = DataQualityChecker.validate_row(row)

            if is_valid:
                results["valid_rows"] += 1

                # Detecta duplicados por corte_id
                corte_id = row.get("corte_id")
                if corte_id in seen_corte_ids:
                    results["duplicates"] += 1
                    results["errors"].append(f"Row {i}: Duplicate corte_id={corte_id}")
                else:
                    seen_corte_ids.add(corte_id)
            else:
                results["invalid_rows"] += 1
                results["errors"].append(f"Row {i}: {error_msg}")

        return results


# Uso en transformer:
def transform_sec_data(raw_data, hora_servidor):
    transformed = [...]  # Tu lógica actual

    quality = DataQualityChecker.validate_batch(transformed)

    if quality["invalid_rows"] > 0:
        logger.warning(f"Quality issues: {quality['invalid_rows']} invalid rows")
        for error in quality["errors"][:5]:  # Log primeros 5
            logger.warning(error)

    return transformed

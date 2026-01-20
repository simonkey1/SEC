# core/transformer.py (mejorado)

import logging
from datetime import datetime, timedelta
import re
from ..helper.hash_generator import generate_corte_id

logger = logging.getLogger(__name__)

class TransformerError(Exception):
    """Base exception para transformer errors"""
    pass

class ParseError(TransformerError):
    """Error al parsear ACTUALIZADO_HACE"""
    pass

def parse_actualizado_hace(actualizado_str: str) -> timedelta:
    """
    Parsea 'X Dias Y Horas Z Minutos' → timedelta
    
    Raises: ParseError si no logra parsear
    """
    try:
        if not actualizado_str or not isinstance(actualizado_str, str):
            raise ParseError(f"ACTUALIZADO_HACE inválido: {actualizado_str}")
        
        match = re.search(
            r'(\d+)\s+Dias\s+(\d+)\s+Horas\s+(\d+)\s+Minutos',
            actualizado_str
        )
        
        if not match:
            raise ParseError(f"Formato no coincide: {actualizado_str}")
        
        dias, horas, minutos = map(int, match.groups())
        return timedelta(days=dias, hours=horas, minutes=minutos)
    
    except ParseError:
        raise
    except Exception as e:
        logger.error(f"Error parsing ACTUALIZADO_HACE '{actualizado_str}': {e}")
        raise ParseError(f"Parse error: {e}")

def transform_row(row: dict, hora_servidor: datetime) -> dict:
    """
    Transforma 1 fila SEC → formato interno
    
    Raises: TransformerError si hay problema
    """
    try:
        # Validar campos requeridos
        required = ['NOMBRE_COMUNA', 'NOMBRE_EMPRESA', 'ACTUALIZADO_HACE', 'CLIENTES_AFECTADOS']
        for field in required:
            if field not in row:
                raise TransformerError(f"Campo requerido faltante: {field}")
        
        # Parse ACTUALIZADO_HACE (con error handling)
        try:
            tiempo_transcurrido = parse_actualizado_hace(row['ACTUALIZADO_HACE'])
        except ParseError as e:
            logger.warning(f"Cannot parse ACTUALIZADO_HACE for {row.get('NOMBRE_COMUNA', '?')}: {e}")
            # OPCIÓN: Skip row o usar default?
            # Para seguridad, usamos valor por defecto
            tiempo_transcurrido = timedelta(minutes=0)
        
        # Calcula fecha inicio
        fecha_inicio_corte = hora_servidor - tiempo_transcurrido
        
        # Genera corte_id
        corte_id = generate_corte_id(
            row['NOMBRE_COMUNA'],
            row['NOMBRE_EMPRESA'],
            fecha_inicio_corte
        )
        
        return {
            'corte_id': corte_id,
            'comuna': row['NOMBRE_COMUNA'],
            'empresa': row['NOMBRE_EMPRESA'],
            'fecha_inicio_corte': fecha_inicio_corte,
            'clientes_afectados': row['CLIENTES_AFECTADOS'],
            'timestamp_reporte': hora_servidor,
            'actualizado_hace': row['ACTUALIZADO_HACE'],
            'batch_id': datetime.now().isoformat(),
            'validated': True
        }
    
    except Exception as e:
        logger.error(f"Error transforming row {row}: {e}")
        raise TransformerError(f"Transform failed: {e}")

def transform_sec_data(raw_data: list, hora_servidor: datetime) -> tuple[list, list]:
    """
    Transforma batch completo.
    
    Retorna: (transformed_data, failed_rows)
    """
    transformed = []
    failed_rows = []
    
    for i, row in enumerate(raw_data):
        try:
            transformed_row = transform_row(row, hora_servidor)
            transformed.append(transformed_row)
        
        except TransformerError as e:
            failed_rows.append({
                'index': i,
                'row': row,
                'error': str(e)
            })
            logger.warning(f"Row {i} failed: {e}")
        
        except Exception as e:
            failed_rows.append({
                'index': i,
                'row': row,
                'error': f"Unexpected error: {e}"
            })
            logger.error(f"Unexpected error on row {i}: {e}")
    
    if failed_rows:
        logger.info(f"Transformation summary: {len(transformed)} success, {len(failed_rows)} failed")
    
    return transformed, failed_rows
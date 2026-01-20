
import hashlib
import datetime


def generate_corte_id(
    comuna: str,
    empresa: str,
    fecha_inicio_corte: datetime
) -> str:
    """
    Genera ID único para un corte basado en:
    - Comuna
    - Empresa
    - Fecha inicio (calculada)
    
    El mismo corte (reportado múltiples veces) siempre 
    tendrá el MISMO corte_id.
    """
    # Formatea fecha a granularidad de minuto (no segundos)
    # Para que pequeñas diferencias de timestamp no afecten
    fecha_str = fecha_inicio_corte.strftime('%Y-%m-%d %H:%M')
    
    # Clave compuesta
    clave = f"{comuna}_{empresa}_{fecha_str}"
    
    # Hash MD5 (determinístico, siempre igual input = igual output)
    corte_id = hashlib.md5(clave.encode()).hexdigest()
    
    return corte_id
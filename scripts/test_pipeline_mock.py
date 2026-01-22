"""Script de prueba del pipeline con datos mockeados.

Usa datos de ejemplo para probar el flujo Transformer → CSV → Validación
sin necesidad de ejecutar el scraper real.

Uso:
    python scripts/test_pipeline_mock.py
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.tranformer import SecDataTransformer
from core.logger import logger


def main():
    """Ejecuta el pipeline con datos mockeados."""
    logger.info("=== PRUEBA DE PIPELINE CON DATOS MOCK ===")
    
    # Datos de ejemplo (estructura real de la SEC)
    mock_data = [
        {
            "MES_INT": 1,
            "ANHO_INT": 2024,
            "HORA": 0,
            "DIA": 0,
            "MES": 0,
            "ANHO": 0,
            "NOMBRE_REGION": "METROPOLITANA",
            "NOMBRE_COMUNA": "SANTIAGO",
            "NOMBRE_EMPRESA": "ENEL",
            "CLIENTES_AFECTADOS": 150,
            "ACTUALIZADO_HACE": "1 Dias 0 Horas 0 Minutos",
            "FECHA_INT_STR": "19/01/2024"
        },
        {
            "MES_INT": 1,
            "ANHO_INT": 2024,
            "HORA": 0,
            "DIA": 0,
            "MES": 0,
            "ANHO": 0,
            "NOMBRE_REGION": "LOS LAGOS",
            "NOMBRE_COMUNA": "PUERTO MONTT",
            "NOMBRE_EMPRESA": "SAESA",
            "CLIENTES_AFECTADOS": 300,
            "ACTUALIZADO_HACE": "2 Dias 0 Horas 0 Minutos",
            "FECHA_INT_STR": "18/01/2024"
        },
        {
            "MES_INT": 1,
            "ANHO_INT": 2024,
            "HORA": 0,
            "DIA": 0,
            "MES": 0,
            "ANHO": 0,
            "NOMBRE_REGION": "LOS LAGOS",
            "NOMBRE_COMUNA": "PUERTO MONTT",
            "NOMBRE_EMPRESA": "SAESA",
            "CLIENTES_AFECTADOS": 200,
            "ACTUALIZADO_HACE": "2 Dias 0 Horas 0 Minutos",
            "FECHA_INT_STR": "18/01/2024"
        },
        {
            "MES_INT": 1,
            "ANHO_INT": 2024,
            "HORA": 0,
            "DIA": 0,
            "MES": 0,
            "ANHO": 0,
            "NOMBRE_REGION": "VALPARAISO",
            "NOMBRE_COMUNA": "VALPARAISO",
            "NOMBRE_EMPRESA": "CHILQUINTA",
            "CLIENTES_AFECTADOS": 80,
            "ACTUALIZADO_HACE": "3 Dias 0 Horas 0 Minutos",
            "FECHA_INT_STR": "17/01/2024"
        }
    ]
    
    mock_server_time = [{"FECHA": "20/01/2024 15:30"}]
    
    logger.info(f"✅ Datos mock preparados: {len(mock_data)} registros")
    
    # Transformación
    logger.info("\nPaso 1: Transformando datos...")
    transformer = SecDataTransformer()
    data_procesada = transformer.transform(mock_data, mock_server_time)
    
    logger.info(f"✅ Transformer procesó {len(data_procesada)} registros")
    logger.info(f"   (Puerto Montt agregado: 300 + 200 = 500 clientes)")
    
    # Exportar a CSV
    logger.info("\nPaso 2: Exportando a CSV...")
    csv_path = transformer.save_to_csv(data_procesada)
    
    if csv_path:
        logger.info(f"✅ Pipeline completado exitosamente")
        logger.info(f"   CSV generado: {csv_path}")
        logger.info(f"\n💡 Ahora ejecuta: python scripts/validate_data.py")
    else:
        logger.error("❌ Error al guardar CSV")


if __name__ == "__main__":
    main()

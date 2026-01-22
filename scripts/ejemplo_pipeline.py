"""Ejemplo de uso del pipeline completo: Scraper → Transformer → CSV.

Este script demuestra el flujo ETL básico:
1. Scraper captura datos de la SEC
2. Transformer procesa y normaliza
3. Exporta a CSV para análisis

Uso:
    python scripts/ejemplo_pipeline.py
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from core.scraper import SECScraper
from core.tranformer import SecDataTransformer
from core.logger import logger


def main():
    """Ejecuta el pipeline completo y genera CSV."""
    logger.info("=== INICIANDO PIPELINE ETL ===")
    
    # 1. Scraping
    logger.info("Paso 1: Ejecutando scraper...")
    scraper = SECScraper()
    result = scraper.run()
    
    if not result.get('registros'):
        logger.error("❌ No se capturaron datos. Abortando.")
        return
    
    logger.info(f"✅ Scraper capturó {len(result['registros'])} registros")
    logger.info(f"   Hora servidor: {result.get('hora_server')}")
    
    # 2. Transformación
    logger.info("\nPaso 2: Transformando datos...")
    transformer = SecDataTransformer()
    data_procesada = transformer.transform(
        result['registros'], 
        result.get('hora_server')
    )
    
    if not data_procesada:
        logger.error("❌ Transformación falló. No hay datos procesados.")
        return
    
    logger.info(f"✅ Transformer procesó {len(data_procesada)} registros")
    
    # 3. Exportar a CSV
    logger.info("\nPaso 3: Exportando a CSV...")
    csv_path = transformer.save_to_csv(data_procesada)
    
    if csv_path:
        logger.info(f"✅ Pipeline completado exitosamente")
        logger.info(f"   CSV generado: {csv_path}")
        logger.info(f"\n💡 Tip: Ejecuta 'python scripts/validate_data.py' para validar los datos")
    else:
        logger.error("❌ Error al guardar CSV")


if __name__ == "__main__":
    main()
